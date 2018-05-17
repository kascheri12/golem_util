import time, config
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move, copy
import analyze_data as al
import os, traceback, sys

class Golem_Graphing():

  def __init__(self):
    self._do_data_cleanup = False
    self._do_data_cleanup_timeout = 180 * 60 ## minutes * 60 seconds
    self._do_daily_graph_refresh = True
    self._daily_refresh_graph_timeout = 24 * 60 * 60 # 24hrs * 60min * 60sec

  def data_cleanup(self):
    pass
  
  def get_pretty_time(self):
    lt = time.localtime()
    return time.strftime("%Y%m%d-%H:%M %Z",lt)

  def move_and_commit_graph(self,v_filepath):
    try:
      copy(config.build_graphs_dir+v_filepath,config.kascheri12_github_io_graphs_dir+v_filepath)
    except:
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      
    try:
      od = os.getcwd()
      os.chdir(config.kascheri12_github_io_dir)
      os.system('git pull')
      os.system('git checkout master')
      os.system('git add ' + config.kascheri12_github_io_graphs_dir+v_filepath)
      os.system('git commit -m "automated commit for ' + v_filepath.split("/")[-1] + '"')
      os.system('git push')
      os.chdir(od)
    except:
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    
  def daily_graph_refresh(self):
    print("Begin daily_graph_refresh: "+self.get_pretty_time())
    filenames = []
    a = al.Analyze_Data()

    try:
      self.move_and_commit_graph(a.print_avg_daily_subtasks_totals(90))
      self.move_and_commit_graph(a.print_avg_daily_nodes_connected(90))
      self.move_and_commit_graph(a.print_avg_daily_unique_node_totals(90))
      self.move_and_commit_graph(a.print_avg_daily_failed_totals(90))
      # self.move_and_commit_graph(a.print_network_summary_over_time_graph(30))
      # self.move_and_commit_graph(a.print_new_unique_over_last_days_graph(30))
    except:
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("End daily_graph_refresh: "+self.get_pretty_time())

def main():

    gg = Golem_Graphing()

    if gg._do_daily_graph_refresh:
      dgr = task.LoopingCall(gg.daily_graph_refresh)
      dgr.start(gg._daily_refresh_graph_timeout)

    if gg._do_data_cleanup:
      dc = task.LoopingCall(gg.data_cleanup)
      dc.start(gg._do_data_cleanup_timeout)

    reactor.run()

if __name__ == '__main__':
    main()
