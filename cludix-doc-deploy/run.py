import os
import requests
import tarfile
import shutil
import re

# 配置
LOGIN_URL = "http://pan.yunke.icu/api/login"
DOWNLOAD_URL = "http://pan.yunke.icu/api/raw/cludix-doc.tar.gz"
TARGET_DIR = "/opt/nginx/html/cludix"
TEMP_FILE = "/tmp/cludix-doc.tar.gz"


def login_and_get_token(username, password):
    """登录filebrowser服务器并获取token"""
    print(f"正在登录 {LOGIN_URL}...")
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })

    if response.status_code == 200:
        token = response.text
        print("登录成功，获取到token")
        return token
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        raise Exception("登录失败")


def extract_file_from_multipart(content):
    """从 multipart 响应中提取实际的文件内容"""
    first_line_end = content.find(b'\r\n')
    if first_line_end == -1:
        first_line_end = content.find(b'\n')

    if first_line_end > 0:
        first_line = content[:first_line_end]
        if first_line.startswith(b'--'):
            boundary = first_line[2:]
            parts = content.split(b'--' + boundary)

            for part in parts:
                if b'Content-Disposition: form-data' in part and b'filename=' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end == -1:
                        header_end = part.find(b'\n\n')

                    if header_end != -1:
                        return part[header_end + 4:].rstrip(b'\r\n').rstrip(b'\n')

    return None


def download_file(token):
    """下载tar.gz文件到本地"""
    print(f"正在下载文件...")
    headers = {"X-Auth": token}
    response = requests.get(DOWNLOAD_URL, headers=headers)

    if response.status_code == 200:
        content = response.content

        if content.startswith(b'--'):
            extracted_data = extract_file_from_multipart(content)
            if not extracted_data:
                raise Exception("无法从 multipart 响应中提取文件")
            content = extracted_data

        with open(TEMP_FILE, 'wb') as f:
            f.write(content)

        print("文件下载完成")
        return True
    else:
        print(f"下载失败: {response.status_code} - {response.text}")
        raise Exception("下载失败")


def remove_target_dir():
    """删除目标目录"""
    if os.path.exists(TARGET_DIR):
        print(f"正在删除目录: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR)
        print("目录删除完成")
    else:
        print(f"目录不存在: {TARGET_DIR}")


def extract_tar():
    """解压tar.gz文件到目标目录"""
    print(f"正在解压文件...")

    # 创建目标目录的父目录（如果不存在）
    os.makedirs(os.path.dirname(TARGET_DIR), exist_ok=True)

    with tarfile.open(TEMP_FILE, 'r:gz') as tar:
        tar.extractall(path=os.path.dirname(TARGET_DIR))

    print("解压完成")

    # 删除临时文件
    os.remove(TEMP_FILE)


def deploy(username, password):
    """执行完整的部署流程"""
    try:
        # 1. 登录获取token
        token = login_and_get_token(username, password)

        # 2. 下载文件
        download_file(token)

        # 3. 删除目标目录
        remove_target_dir()

        # 4. 解压文件
        extract_tar()

        print("\n部署完成！")
        print(f"文件已部署到: {TARGET_DIR}")

    except Exception as e:
        print(f"\n部署失败: {str(e)}")
        return 1

    return 0


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("使用方法: python cludix-doc-depoly.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    print("=" * 50)
    print("开始执行 Cludix 文档部署脚本")
    print("=" * 50)

    exit_code = deploy(username, password)
    sys.exit(exit_code)
