"""
项目启动脚本 - 前端
"""
import os
import sys
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 启动Streamlit应用
if __name__ == "__main__":
    print("启动自动小说生成器前端界面...")
    subprocess.run(["streamlit", "run", "app.py", "--server.port=8501"])
