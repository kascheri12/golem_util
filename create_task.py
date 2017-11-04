import time
from twisted.internet import task
from twisted.internet import reactor
from subprocess import Popen, PIPE
import os
import getpass as gp
import sys
import config

timeout = 60 * 60.0 # xx minutes @ Sixty seconds

def __main__(argv):

    l = task.LoopingCall(add_new_task)
    l.start(timeout) # call every sixty seconds

    reactor.run()

def add_new_task():
  # proc = Popen('sudo -S golemcli tasks create sample_tasks/task.task', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
  # print(proc.communicate(str.encode(config.password+'\n')))
  
  proc = Popen('~/golem-0.9.0/golemcli tasks create sample_tasks/task.task', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
  
  
if __name__ == '__main__':
    __main__(sys.argv[1:])
