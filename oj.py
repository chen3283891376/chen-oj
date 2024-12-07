import asyncio
import requests
import websockets
import threading
import os,re
import json
import pystray as stray
from PIL import Image

def contains_string(haystack, needle):
    # 转义特殊字符以确保正则表达式正确
    needle = re.escape(needle)
    # 创建正则表达式
    pattern = re.compile(needle)
    # 使用re.search进行匹配
    return pattern.search(haystack) is not None

def compare_answer(output, expected_output):
    output = output.strip()  # 去除实际输出两端的空白字符
    expected_output = expected_output.strip()  # 去除预期输出两端的空白字符
    if output == expected_output:
        return True
    return False

# 创建托盘图标的函数
def create_tray_icon():
    def on_quit(icon, item):
        icon.stop()
        os._exit(200)

    image = Image.new('RGB', (64, 64), color=(255, 0, 0))
    menu = (stray.MenuItem('Quit', on_quit),)
    icon = stray.Icon('test', image, '托盘', menu)
    icon.run()


async def handler(websocket, path):
    data = await websocket.recv()
    code = str(json.loads(data)["str"])
    id = str(json.loads(data)["id"])
    stdin = open(f"./in/{id}.in","r",encoding="utf-8")
    stdout = open(f"./out/{id}.out","r",encoding="utf-8")
    data = {
        "code": code,
        "token": "066417defb80d038228de76ec581a50a",
        "stdin": stdin.read(),
        "language": "7",
        "fileext": "cpp"
    }
    answer = json.loads(requests.post("https://www.runoob.com/try/compile2.php",data=data).text)
    if answer["output"]!="":
        if compare_answer(answer["output"],stdout.read()):
            await websocket.send("通过")
        else:
            await websocket.send("答案错误")
    else:
        await websocket.send(answer["errors"]+"\n编译错误")

start_server = websockets.serve(handler, "localhost", 8765)

# 在一个单独的线程中运行托盘图标
threading.Thread(target=create_tray_icon).start()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()