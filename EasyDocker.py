import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
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

def build_image(image_name='python-app', output_callback=None):
    result = subprocess.run(['docker', 'build', '-t', image_name, '.'], capture_output=True, text=True)
    if output_callback:
        output_callback(result.stdout)
    if result.returncode == 0:
        msg = f'映像檔  {image_name} 建立成功！'
        if output_callback:
            output_callback(msg)
        else:
            print(msg)
    else:
        msg = '建立映像檔失敗：\n' + result.stderr
        if output_callback:
            output_callback(msg)
        else:
            print(msg)

def check_docker():
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def select_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[('Python Files', '*.py')])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, os.path.basename(file_path))

def start_pack(pyfile_entry, image_entry, output_text, gen_bat_var):
    pyfile = pyfile_entry.get().strip()
    image_name = image_entry.get().strip() or 'python-app'
    if not pyfile or not os.path.exists(pyfile):
        messagebox.showerror('錯誤', '請選擇正確的 Python 檔案！')
        return
    ensure_dockerfile(pyfile)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f'已產生 Dockerfile，開始建構映像檔...\n')
    build_image(image_name, lambda msg: output_text.insert(tk.END, msg + '\n'))
    # 產生 run_docker.bat
    if gen_bat_var.get():
        bat_content = f"docker run --rm {image_name}\n"
        with open('run_docker.bat', 'w', encoding='utf-8') as f:
            f.write(bat_content)
        output_text.insert(tk.END, '已產生 run_docker.bat，可直接雙擊啟動容器。\n')

def main():
    if not check_docker():
        import webbrowser
        tk.Tk().withdraw()
        messagebox.showerror('找不到 Docker', '系統未偵測到 Docker，將自動開啟官方下載頁面，請安裝 Docker Desktop 並確認已加入 PATH。')
        webbrowser.open('https://www.docker.com/products/docker-desktop/')
        sys.exit(1)

    root = tk.Tk()
    root.title('EasyDocker GUI')
    root.geometry('500x350')

    tk.Label(root, text='Python 檔案:').pack(anchor='w', padx=10, pady=(10,0))
    frame = tk.Frame(root)
    frame.pack(fill='x', padx=10)
    pyfile_entry = tk.Entry(frame, width=40)
    pyfile_entry.pack(side='left', fill='x', expand=True)
    tk.Button(frame, text='選擇檔案', command=lambda: select_file(pyfile_entry)).pack(side='left', padx=5)

    tk.Label(root, text='映像名稱（可選）:').pack(anchor='w', padx=10, pady=(10,0))
    image_entry = tk.Entry(root, width=40)
    image_entry.pack(fill='x', padx=10)


    gen_bat_var = tk.BooleanVar(value=True)
    bat_checkbox = tk.Checkbutton(root, text='自動產生 run_docker.bat 啟動檔', variable=gen_bat_var)
    bat_checkbox.pack(anchor='w', padx=10)

    tk.Button(root, text='一鍵包裝', command=lambda: start_pack(pyfile_entry, image_entry, output_text, gen_bat_var)).pack(pady=10)

    output_text = tk.Text(root, height=10)
    output_text.pack(fill='both', padx=10, pady=5, expand=True)

    root.mainloop()

if __name__ == '__main__':
    main()
