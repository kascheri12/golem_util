import time
from twisted.internet import task
from twisted.internet import reactor
from subprocess import Popen, PIPE
import os
import getpass as gp
import sys
import config

timeout = 10 * 60.0 # xx minutes @ Sixty seconds
# pword =  str.encode(gp.getpass())

def __main__(argv):
    
    l = task.LoopingCall(add_new_task)
    l.start(timeout) # call every sixty seconds
    
    reactor.run()

def add_new_task():
  proc = Popen('sudo -S golemcli tasks create sample_tasks/task.task', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
  print(proc.communicate(str.encode(config.password+'\n')))
  
if __name__ == '__main__':
    __main__(sys.argv[1:])
