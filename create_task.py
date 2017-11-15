import time
from twisted.internet import task
from twisted.internet import reactor
from subprocess import Popen, PIPE
import os
import getpass as gp
import sys


class Create_Task:
  timeout = 120 * 60.0 # xx minutes @ Sixty seconds
  res_golem_header = "/Users/ascherik/Downloads/golem-header.blend"
  res_airplane = "/Users/ascherik/Downloads/Golem\ Airplane"
  filename = "tmp.task"
  
  def __init__(self):
    pass

  def add_new_task(self):
    command_str = " ".join("~/Downloads/golem-0.9.0/golemcli","tasks","create",self.build_golem_header_task(2))
    proc = Popen(command_str, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

  def build_golem_header_task(self,level):
    ght = None
    if level == 1:
      ght = self.build_simple_golem_header_task(10,300,200)
    elif level == 2:
      ght = self.build_simple_golem_header_task(100,3000,2000)
    return ght

  def build_simple_golem_header_task(self,subtasks,height,width):
    ts = {
      "name":"Golem Task Simple",
      "type": "Blender",
      "subtasks": subtasks,
      "options": {
          "frame_count": 1,
          "output_path": "",
          "format": "PNG",
          "resolution": [
              height,
              width
          ],
          "frames": "1",
          "compositing": False
      },
      "timeout": "20:00:00",
      "subtask_timeout": "0:35:00",
      "bid": 5.0,
      "resources": [
          self.res_golem_header
      ]
    }
    with open(self.filename,'w') as f:
      f.write(str(ts))
    return self.filename


def __main__(argv):

  ct = Create_Task()
  l = task.LoopingCall(ct.add_new_task)
  l.start(timeout) # call every sixty seconds

  reactor.run()

if __name__ == '__main__':
  __main__(sys.argv[1:])
