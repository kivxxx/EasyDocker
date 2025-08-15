import os
import subprocess
import sys

DOCKERFILE_TEMPLATE = '''\
FROM python:3.11-slim
WORKDIR /app
COPY . /app
CMD ["python", "{pyfile}"]
'''

def ensure_dockerfile(pyfile):
    content = DOCKERFILE_TEMPLATE.format(pyfile=pyfile)
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(content)

def build_image(image_name='python-app'):
    result = subprocess.run(['docker', 'build', '-t', image_name, '.'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print(f'映像檔 {image_name} 建立成功！')
    else:
        print('建立映像檔失敗：')
        print(result.stderr)

def check_docker():
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

    pass  # CLI 版本不需要

def start_pack(pyfile, image_name, gen_bat):
    if not pyfile or not os.path.exists(pyfile):
        print('錯誤：請輸入正確的 Python 檔案名稱！')
        return
    ensure_dockerfile(pyfile)
    print('已產生 Dockerfile，開始建構映像檔...')
    build_image(image_name)
    if gen_bat:
        bat_content = f"docker run --rm {image_name}\n"
        with open('run_docker.bat', 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print('已產生 run_docker.bat，可直接雙擊啟動容器。')

def main():
    if not check_docker():
        print('找不到 Docker，請先安裝 Docker Desktop 並確認已加入 PATH。')
        print('下載網址：https://www.docker.com/products/docker-desktop/')
        sys.exit(1)

    print('==== EasyDocker CLI ====' )
    pyfile = input('請輸入要包裝的 Python 檔案名稱（例如 app.py）：').strip()
    image_name = input('請輸入映像名稱（預設 python-app）：').strip() or 'python-app'
    gen_bat = input('是否自動產生 run_docker.bat 啟動檔？(Y/n)：').strip().lower() != 'n'
    start_pack(pyfile, image_name, gen_bat)

if __name__ == '__main__':
    main()
