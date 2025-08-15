import os
import subprocess
import sys
import re
import datetime

DOCKERFILE_TEMPLATE = '''\
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "{pyfile}"]
'''

def ensure_dockerfile(pyfile, custom_content=None):
    content = custom_content or DOCKERFILE_TEMPLATE.format(pyfile=pyfile)
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(content)

def build_image(image_name='python-app', log_path=None):
    # 強制用 utf-8 寫 log，避免 Windows 預設編碼問題
    with open(log_path, 'a', encoding='utf-8', errors='replace') if log_path else open(os.devnull, 'w', encoding='utf-8', errors='replace') as logf:
        result = subprocess.run(['docker', 'build', '-t', image_name, '.'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(result.stdout)
        logf.write(result.stdout)
        if result.returncode == 0:
            print(f'映像檔 {image_name} 建立成功！')
            logf.write(f'映像檔 {image_name} 建立成功！\n')
        else:
            print('建立映像檔失敗：')
            print(result.stderr)
            logf.write('建立映像檔失敗：\n')
            logf.write((result.stderr or '') + '\n')

def check_docker():
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

    pass  # CLI 版本不需要

def start_pack(pyfile, image_name, gen_bat, custom_dockerfile=None, lang='zh', log_path=None):
    msg = {
        'zh': {
            'file_error': '錯誤：請輸入正確的 Python 檔案名稱！',
            'dockerfile': '已產生 Dockerfile，開始建構映像檔...',
            'bat': '已產生 run_docker.bat，可直接雙擊啟動容器。',
            'req': '已自動產生 requirements.txt',
        },
        'en': {
            'file_error': 'Error: Please enter a valid Python file name!',
            'dockerfile': 'Dockerfile generated. Building image...',
            'bat': 'run_docker.bat generated. Double-click to start the container.',
            'req': 'requirements.txt generated automatically.',
        }
    }
    if not pyfile or not os.path.exists(pyfile):
        print(msg[lang]['file_error'])
        return
    auto_generate_requirements(pyfile, lang)
    print(msg[lang]['req'])
    ensure_dockerfile(pyfile, custom_dockerfile)
    print(msg[lang]['dockerfile'])
    build_image(image_name, log_path)
    if gen_bat:
        bat_content = f"docker run --rm {image_name}\n"
        with open('run_docker.bat', 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print(msg[lang]['bat'])

def main():
    # 語言選擇
    lang = 'zh'
    lang_input = input('Language? (zh/en, 預設 zh)：').strip().lower()
    if lang_input == 'en':
        lang = 'en'

    msg = {
        'zh': {
            'docker_not_found': '找不到 Docker，請先安裝 Docker Desktop 並確認已加入 PATH。',
            'docker_url': '下載網址：https://www.docker.com/products/docker-desktop/',
            'main_title': '==== EasyDocker CLI ====',
            'detecting': '自動偵測主程式...',
            'detected': '偵測到主程式：',
            'input_py': '請輸入要包裝的 Python 檔案名稱（直接 Enter 使用偵測到的）：',
            'input_img': '請輸入映像名稱（預設 python-app）：',
            'input_bat': '是否自動產生 run_docker.bat 啟動檔？(Y/n)：',
            'input_dockerfile': '是否自訂 Dockerfile？(y/N)：',
            'input_log': '是否輸出 log 檔？(Y/n)：',
            'input_logname': '請輸入 log 檔名（預設 build.log）：',
        },
        'en': {
            'docker_not_found': 'Docker not found. Please install Docker Desktop and ensure it is in PATH.',
            'docker_url': 'Download: https://www.docker.com/products/docker-desktop/',
            'main_title': '==== EasyDocker CLI ====',
            'detecting': 'Detecting main Python file...',
            'detected': 'Detected main file:',
            'input_py': 'Enter Python file to package (press Enter to use detected):',
            'input_img': 'Enter image name (default python-app):',
            'input_bat': 'Generate run_docker.bat? (Y/n):',
            'input_dockerfile': 'Custom Dockerfile? (y/N):',
            'input_log': 'Output log file? (Y/n):',
            'input_logname': 'Enter log file name (default build.log):',
        }
    }
    if not check_docker():
        print(msg[lang]['docker_not_found'])
        print(msg[lang]['docker_url'])
        sys.exit(1)

    print(msg[lang]['main_title'])
    # 1. 自動偵測主程式
    print(msg[lang]['detecting'])
    py_candidates = [f for f in os.listdir('.') if f.endswith('.py') and f not in ('build_exe.py', 'EasyDocker.py')]
    pyfile = py_candidates[0] if py_candidates else ''
    if pyfile:
        print(f"{msg[lang]['detected']} {pyfile}")
    pyfile_input = input(msg[lang]['input_py']).strip()
    if pyfile_input:
        pyfile = pyfile_input
    if not pyfile:
        print('找不到可用的 Python 檔案。')
        sys.exit(1)
    image_name = input(msg[lang]['input_img']).strip() or 'python-app'
    gen_bat = input(msg[lang]['input_bat']).strip().lower() != 'n'
    # 8. 自訂 Dockerfile
    custom_dockerfile = None
    if input(msg[lang]['input_dockerfile']).strip().lower() == 'y':
        print('請貼上自訂 Dockerfile 內容，結束請輸入單獨一行 END：')
        lines = []
        while True:
            l = input()
            if l.strip() == 'END':
                break
            lines.append(l)
        custom_dockerfile = '\n'.join(lines)
    # 5. log 支援
    log_path = None
    if input(msg[lang]['input_log']).strip().lower() != 'n':
        log_path = input(msg[lang]['input_logname']).strip() or 'build.log'
    start_pack(pyfile, image_name, gen_bat, custom_dockerfile, lang, log_path)

# 2. 自動產生 requirements.txt
def auto_generate_requirements(pyfile, lang='zh'):
    # 只分析主程式，進階可遞迴分析
    try:
        with open(pyfile, 'r', encoding='utf-8') as f:
            code = f.read()
        # 更完整的標準庫清單（Python 3.11）
        stdlibs = set([
            'abc','aifc','argparse','array','ast','asynchat','asyncio','asyncore','atexit','audioop','base64','bdb','binascii','binhex','bisect','builtins','bz2',
            'calendar','cgi','cgitb','chunk','cmath','cmd','code','codecs','codeop','collections','colorsys','compileall','concurrent','configparser','contextlib','contextvars','copy','copyreg','crypt','csv','ctypes','curses','dataclasses','datetime','dbm','decimal','difflib','dis','distutils','doctest','email','encodings','ensurepip','enum','errno','faulthandler','fcntl','filecmp','fileinput','fnmatch','formatter','fractions','ftplib','functools','gc','getopt','getpass','gettext','glob','graphlib','grp','gzip','hashlib','heapq','hmac','html','http','imaplib','imghdr','imp','importlib','inspect','io','ipaddress','itertools','json','keyword','lib2to3','linecache','locale','logging','lzma','mailbox','mailcap','marshal','math','mimetypes','mmap','modulefinder','msilib','msvcrt','multiprocessing','netrc','nntplib','numbers','operator','optparse','os','ossaudiodev','parser','pathlib','pdb','pickle','pickletools','pipes','pkgutil','platform','plistlib','poplib','posix','pprint','profile','pstats','pty','pwd','py_compile','pyclbr','pydoc','queue','quopri','random','re','readline','reprlib','resource','rlcompleter','runpy','sched','secrets','select','selectors','shelve','shlex','shutil','signal','site','smtpd','smtplib','sndhdr','socket','socketserver','spwd','sqlite3','ssl','stat','statistics','string','stringprep','struct','subprocess','sunau','symtable','sys','sysconfig','syslog','tabnanny','tarfile','telnetlib','tempfile','termios','test','textwrap','threading','time','timeit','tkinter','token','tokenize','trace','traceback','tracemalloc','tty','turtle','turtledemo','types','typing','unicodedata','unittest','urllib','uu','uuid','venv','warnings','wave','weakref','webbrowser','winreg','winsound','wsgiref','xdrlib','xml','xmlrpc','zipapp','zipfile','zipimport','zlib'
        ])
        # 新增：本地 .py 檔案名稱（不含副檔名）與本地資料夾名稱（視為本地模組）
        local_py_modules = set(os.path.splitext(f)[0] for f in os.listdir('.') if f.endswith('.py'))
        local_dirs = set(f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('__'))
        local_modules = local_py_modules | local_dirs

        visited = set()
        pkgs = set()

        def visit_file(filename):
            if filename in visited:
                return
            visited.add(filename)
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception:
                return
            imports = re.findall(r'^\s*(?:import|from)\s+([\w_\.]+)', code, re.MULTILINE)
            for imp in imports:
                root = imp.split('.')[0]
                if root in stdlibs:
                    continue
                if root in local_modules:
                    # 遞迴分析本地模組
                    # 先找 .py 檔，再找資料夾/__init__.py
                    py_path = root + '.py'
                    dir_init_path = os.path.join(root, '__init__.py')
                    if os.path.isfile(py_path):
                        visit_file(py_path)
                    elif os.path.isfile(dir_init_path):
                        visit_file(dir_init_path)
                    continue
                pkgs.add(root)

        visit_file(pyfile)

        if pkgs:
            with open('requirements.txt', 'w', encoding='utf-8') as f:
                for p in sorted(pkgs):
                    f.write(p+'\n')
        else:
            with open('requirements.txt', 'w', encoding='utf-8') as f:
                f.write('')
    except Exception as e:
        print('requirements.txt 產生失敗:', e)

if __name__ == '__main__':
    main()
