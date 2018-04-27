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

  def daily_graph_refresh(self):
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)
    print("Begin daily_graph_refresh: "+pt)
    filename_daily_aggregate_totals_10_days = ''
    filename_daily_avg_nodes_connected_10_days = ''
    filename_summary_over_last_10_days = ''
    filename_network_summary_graph_10_days = ''
    a = al.Analyze_Logs()

    try:
      filename_daily_aggregate_totals_10_days = a.print_daily_aggregate_totals(10)
      filename_daily_avg_nodes_connected_10_days = a.print_daily_avg_nodes_connected(10)
      filename_summary_over_last_10_days = a.print_summary_over_last_days_graph(10)
      filename_network_summary_graph_10_days = a.print_network_summary_over_time_graph(10)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      copy(filename_daily_aggregate_totals_10_days,config.kascheri12_github_io_dir+filename_daily_aggregate_totals_10_days)
      copy(filename_daily_avg_nodes_connected_10_days,config.kascheri12_github_io_dir+filename_daily_avg_nodes_connected_10_days)
      copy(filename_summary_over_last_10_days,config.kascheri12_github_io_dir+filename_summary_over_last_10_days)
      copy(filename_network_summary_graph_10_days,config.kascheri12_github_io_dir+filename_network_summary_graph_10_days)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      od = os.getcwd()
      os.chdir(config.kascheri12_github_io_dir)
      os.system('git pull')
      os.system('git checkout master')
      os.system('git add ' + filename_daily_aggregate_totals_10_days)
      os.system('git add ' + filename_daily_avg_nodes_connected_10_days)
      os.system('git add ' + filename_summary_over_last_10_days)
      os.system('git add ' + filename_network_summary_graph_10_days)
      os.system('git commit -m "automated commit for daily-golem-graphs"')
      os.system('git push')
      os.chdir(od)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print("End daily_graph_refresh: "+pt)

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
