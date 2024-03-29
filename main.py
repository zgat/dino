import subprocess
import json
import time
import os

def is_script_running(script_name):
    # 使用ps命令列出所有进程，并通过grep搜索脚本名称
    process = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    out, _ = process.communicate()
    for line in out.splitlines():
        if script_name in str(line):
            return True
    return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    # 检查脚本是否正在运行
    if not is_script_running('88.py'):
        # 启动脚本a.py
        subprocess.Popen(['python', '88.py'])
        time.sleep(2) 
    file_path = "config.json"
    with open(file_path) as file:
        conf = json.load(file)
    index = len(conf["zga"]["message"]) - 1
    top_index = len(conf["zga"]["top_message"]) - 1
    if index > 2:
        for i in range(3):
            print(conf["zga"]["message"][index - i])
    else:
        for item in conf["zga"]["message"]:
            print(item)
    if top_index > 2:
        for i in range(3):
            print(conf["zga"]["top_message"][top_index - i])
    else:
        for item in conf["zga"]["top_message"]:
            print(item)
