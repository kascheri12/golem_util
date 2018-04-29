import time, config
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move, copy
import analyze_logs as al
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
    
  def daily_graph_refresh(self):
    print("Begin daily_graph_refresh: "+self.get_pretty_time())
    filenames = []
    a = al.Analyze_Logs()

    try:
      filenames.append(a.print_daily_aggregate_totals(10))
      filenames.append(a.print_daily_avg_nodes_connected(30))
      filenames.append(a.print_summary_over_last_days_graph(10))
      filenames.append(a.print_network_summary_over_time_graph(10))
      try:
        for fn in filenames:
          copy(fn,config.kascheri12_github_io_dir+fn)
        try:
          od = os.getcwd()
          os.chdir(config.kascheri12_github_io_dir)
          os.system('git pull')
          os.system('git checkout master')
          for fn in filenames:
            os.system('git add ' + fn)
          os.system('git commit -m "automated commit for daily-golem-graphs"')
          os.system('git push')
          os.chdir(od)
        except:
          print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
          traceback.print_exc(file=sys.stdout)
          print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      except:
        print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        traceback.print_exc(file=sys.stdout)
        print(self.get_pretty_time() + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
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
