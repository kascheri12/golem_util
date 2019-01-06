from subprocess import Popen, PIPE
import os, time, sys, json
import os, time, sys, json, config
import getpass as gp
from time import sleep
from datetime import datetime as dt


class Create_Task:

  def __init__(self):
    self.init_start_timeout = 0 # 20 * 60
    self.timeout = 30 * 60.0 # seconds
    self.difficulty_level = 3
    self.blend_file = config.blend_file
    self.path_to_golemcli = "golemcli"
    self.filename = "tmp.task"
    self.output_path = config.output_path

  def clean_tasks_of_status(self, task_status):
    # command_str = " ".join([self.path_to_golemcli,"tasks","show | grep '",task_status,"' | grep -o '^\S*' | sed 's/^/",self.path_to_golemcli," tasks delete /'"])
    command_str = " ".join([self.path_to_golemcli,"tasks","show | grep '",task_status,"' | grep -o '^\S*' | sed 's/^/",self.path_to_golemcli," tasks delete /' | bash -s"])
    proc = Popen(command_str, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
  def add_new_task(self):
    print("Create new task %s" % dt.now())
    command_str = " ".join([self.path_to_golemcli,"-m","tasks","create",self.build_golem_header_task(self.difficulty_level)])
    if not config.prod:
      command_str = " ".join([self.path_to_golemcli,"tasks","create",self.build_golem_header_task(self.difficulty_level)])
    proc = Popen(command_str, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

  def build_golem_header_task(self,level):
    ght = None
    if level == 1:
      ght = self.build_simple_golem_header_task(1,300,200,3,5)
    elif level == 2:
      ght = self.build_simple_golem_header_task(5,3000,2000,3,5)
    elif level == 3:
      ght = self.build_simple_golem_header_task(20,8000,4000,1,1)
    elif level == 4:
      ght = self.build_simple_golem_header_task(50,6000,4000,3,5)
    return ght

  def build_simple_golem_header_task(self,subtasks,height,width,price,subtask_to_min):
    ts = {
      "name":"Golem Task Simple",
      "type": "Blender",
      "compute_on": "cpu",
      # "concent_enabled": "true",
      "subtasks": subtasks,
      "options": {
          "frame_count": 1,
          "output_path": self.output_path,
          "format": "PNG",
          "resolution": [
              height,
              width
          ],
          "frames": "1",
          "compositing": False
      },
      "timeout": "20:00:00",
      "subtask_timeout": "0:"+str(subtask_to_min)+":00",
      "bid": price,
      "resources": [self.blend_file]
    }
    with open(self.filename,'w') as f:
      f.write(json.dumps(ts))
    return self.filename


def __main__(argv):

  ct = Create_Task()

  if len(argv) > 0:
    if argv[0] == 'clean':
      ct.clean_tasks_of_status(argv[1])
    if argv[0] == 'setup':
      ct.get_task_header_blender_sample()
    if argv[0] == 'create':
      ct.add_new_task()
  else:
    from twisted.internet import task
    from twisted.internet import reactor
    sleep(ct.init_start_timeout)
    l = task.LoopingCall(ct.add_new_task)
    l.start(ct.timeout) # call every sixty seconds
    reactor.run()

if __name__ == '__main__':
  __main__(sys.argv[1:])
