import subprocess
import os
import time

def run_command(command, cwd=None, shell=True):
    """运行命令并返回进程对象"""
    print(f"执行命令: {' '.join(command) if isinstance(command, list) else command}")
    if cwd:
        print(f"工作目录: {cwd}")
    
    # 使用subprocess.Popen启动命令，创建新窗口
    if os.name == 'nt':  # Windows系统
        process = subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=shell,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:  # 非Windows系统
        process = subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=shell
        )
    return process

def main():
    print("正在准备重启服务...")
    print("=" * 50)
    
    # 前端服务
    print("\n启动前端服务...")
    frontend_dir = "D:\\Users\\tianxiaxiaoyao\\Desktop\\毕设\\my_graduation_project\\frontend"
    frontend_process = run_command("npm run dev", cwd=frontend_dir)
    
    # 等待2秒，确保前端服务有时间启动
    time.sleep(2)
    
    # 后端服务
    print("\n启动后端服务...")
    backend_dir = "D:\\Users\\tianxiaxiaoyao\\Desktop\\毕设\\my_graduation_project\\backend"
    backend_process = run_command("python manage.py runserver", cwd=backend_dir)
    
    print("\n" + "=" * 50)
    print("服务启动完成！")
    print("前端服务运行在新窗口中")
    print("后端服务运行在新窗口中")
    print("\n按任意键退出...")
    input()

if __name__ == "__main__":
    main()