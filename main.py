import asyncio
import os
import copy
from tkinter import *
from bilibiliClient import bilibiliClient
import threading

print("")
print("=====Bilibili直播弹幕投票系统=====")
print("           By Trychen")
print("1.使用时按 回车Enter 查看当前投票情况")
print("2.输入 'reset' + 回车 重置投票")
print("2.输入 'load <文件名>' + 回车 加载其他投票内容")
print("==================================")
print("")
file_name = input('请输入投票列表文件名(默认: "vote.txt"): ')
room_id = input('请输入直播间ID: ')

if not file_name or file_name == "":
    file_name = "vote.txt"
try:
    file_object = open(os.path.split(os.path.realpath(__file__))[0] + "/" + file_name)
except FileNotFoundError:
    print("找不到投票列表文件: " + file_name)
    exit()
print("正在读取,投票内容!")

vote = {}
try:
    for line in file_object:
        vote[line.replace("\n", "")] = 0
finally:
    file_object.close()
print("读取投票内容成功...")

danmuji = bilibiliClient(copy.deepcopy(vote), room_id)

tasks = [
    danmuji.connectServer(),
    danmuji.HeartbeatLoop()
]

loop = asyncio.get_event_loop()


class command_thread(threading.Thread):

    def run(self):
        while 1:
            inp = input()
            if inp == "":
                if danmuji.loaded:
                    print("")
                    print("---投票结果---")
                    print("(由低到高排序)")
                    votes = danmuji.getVote()
                    big_to_small = sorted(votes.items(), key=lambda d: d[1])
                    for (k, v) in big_to_small:
                        if v != 0:
                            print(k + " : " + str(v))
                    print("---投票结果---")
                    print("")
            elif inp == 'reset':
                danmuji.reset()
            elif inp.startswith("load "):
                danmuji.load(inp[5:])



command_thread().start()

try:
    loop.run_until_complete(asyncio.wait(tasks))
except KeyboardInterrupt:
    danmuji.connected = False
    for task in asyncio.Task.all_tasks():
        task.cancel()
    loop.run_forever()

loop.close()
