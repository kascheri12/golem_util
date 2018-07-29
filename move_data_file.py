from apscheduler.schedulers.blocking import BlockingScheduler
import scan_nodes as sn
import time, config
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move
import os, traceback, sys


class Move_Data_File():

  def __init__(self):
    self._timeout = 24 * 60 * 60.0 # 12 hrs @ 60 min @ Sixty seconds
      
  def get_pretty_time(self):
    lt = time.localtime()
    return time.strftime("%Y%m%d-%H:%M %Z",lt)

  def handle_file_transfer():
    prep_file_for_transfer()
    do_move_file()
  
  def prep_file_for_transfer():
    copy_cmd = "copy \""+config.prod_network_log+"\" \""+config.prod_network_log_copy+"\""
    del_cmd = "del /f "+config.prod_graphing_network_log
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>BEGIN copy cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    os.system(copy_cmd)
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>END copy cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>BEGIN del cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    os.system(del_cmd)
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>END del cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    
  def do_move_file():
    move_file_cmd = "copy \""+config.prod_network_log_copy+"\" "+config.prod_graphing_network_log
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>BEGIN mv cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    os.system(move_file_cmd)
    print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>END mv cmd<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    del_copy_cmd = "del /f \""+config.prod_network_log_copy+"\""
    os.system(del_copy_cmd)
    
def main():

    mdf = Move_Data_File()
    l = task.LoopingCall(mdf.handle_file_transfer)
    l.start(mdf._timeout) # call every sixty seconds

    reactor.run()

if __name__ == '__main__':
    main()
