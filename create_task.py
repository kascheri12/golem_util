from twisted.internet import task
from twisted.internet import reactor
from subprocess import Popen, PIPE
import os, time, sys, json
import getpass as gp
from time import sleep


class Create_Task:
  username = "ascherik"
  init_start_timeout = 0
  timeout = 120 * 60.0 # xx minutes @ Sixty seconds
  difficulty_level = 2 
  res_golem_header = ["".join(["/Users/",username,"/Downloads/golem-header.blend"])]
  res_airplane = ["".join(["/Users/",username,"/Downloads/Golem\ Airplane/"])]
  path_to_golemcli = "~/Downloads/golem-0.9.0/golemcli"
  filename = "tmp.task"
  
  def __init__(self):
    pass

  def add_new_task(self):
    command_str = " ".join([self.path_to_golemcli,"tasks","create",self.build_golem_header_task(self.difficulty_level)])
    proc = Popen(command_str, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

  def build_golem_header_task(self,level):
    ght = None
    if level == 1:
      ght = self.build_simple_golem_header_task(1,300,200,3,30)
    elif level == 2:
      ght = self.build_simple_golem_header_task(5,3000,2000,3,25)
    elif level = 3:
      ght = self.build_simple_golem_header_task(20,3000,2000,5,25)
  elif level == 4:
      ght = self.build_simple_golem_header_task(100,3000,2000,5,20)
    return ght

  def build_simple_golem_header_task(self,subtasks,height,width,price,subtask_to_min):
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
      "timeout": "8:00:00",
      "subtask_timeout": "0:"+subtask_to_min+":00",
      "bid": price,
      "resources": self.res_golem_header
    }
    with open(self.filename,'w') as f:
      f.write(json.dumps(ts))
    return self.filename


def __main__(argv):

  ct = Create_Task()
  sleep(ct.init_start_timeout)
  l = task.LoopingCall(ct.add_new_task)
  l.start(ct.timeout) # call every sixty seconds

  reactor.run()

if __name__ == '__main__':
  __main__(sys.argv[1:])
