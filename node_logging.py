from apscheduler.schedulers.blocking import BlockingScheduler
import scan_nodes as sn
import time, config
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move, copy
import analyze_logs as al
import os, traceback, sys

class Node_Logging():

  def __init__(self):
    self._timeout = 5 * 60.0 # Five @ Sixty seconds
    self._do_refresh_graph = True
    self._refresh_graph_timeout = 60 * 60 #### 1440 * 60 # 24 hours

  def check_for_node_log_dir(self):
    if not os.path.exists('node_logs'):
      os.makedirs('node_logs')

  def take_network_snapshot(self):
    self.check_for_node_log_dir()
    FILE_SIZE_LIMIT = 999999999  # 999MB
    timestamp = str(round(time.time()))
    d = date.fromtimestamp(time.time())
    pretty_date = "%s%s%s" % (d.year,d.month,d.day)
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)
    filename = 'network.log'
    log_dir = 'node_logs/'
    file_path = log_dir+filename
    append_param = 'a'

    # Finalize file_name
    # append_param has been initialized to a
    # If the file exists
    if os.path.exists(file_path):
      # If the filesize exceeds the limit
      if os.stat(file_path).st_size >= FILE_SIZE_LIMIT:
        # Move the file and rename it with today's date
        move(file_path,file_path[:-4]+pretty_date+file_path[-4:])
        append_param = 'w'
    else:
      append_param = 'w'

    # Try retreiving the active nodes in the network
    try:
      active_nodes = sn.get_active_node_list()
    except:
      print(pt + " - Error getting active nodes.. probably network connection")

    # Try writing the data to the file
    try:
      with open(file_path,append_param,encoding="UTF-8") as f:
        # Check that there are nodes on the network..
        if active_nodes is not None and len(active_nodes) > 0:
          # Is this the first line of the file? If so, write the header
          if append_param == 'w':
            f.write("%s\n" % (",".join(["timestamp"]+list(x for x in active_nodes[0].keys()))))
          # Write all the data for each node. Include the timestamp this data set
          for node in active_nodes:
            f.write("%s\n" % (",".join([timestamp]+list(str(x) for x in node.values()))))
    except:
      print("file_path:"+file_path)
      print("append_param:"+append_param)
      traceback.print_exc(file=sys.stdout)
      print(pt + " - Error with writing the file...")

  def refresh_graph(self):
    filename_subtasks_success_graph = ''
    filename_network_summary_graph = ''
    filename_change_in_successes = ''
    a = al.Analyze_Logs()
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)

    print("Begin refresh_graph: "+pt)
    try:
      filename_subtasks_success_graph = a.print_node_success_over_time_graph(a.d, 1)
      filename_network_summary_graph = a.print_network_summary_over_time_graph(a.d, 5)
      # filename_change_in_successes = a.print_change_in_subtask_success_graph(a.d, 1)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      copy(filename_subtasks_success_graph,config.kascheri12_github_io_dir+filename_subtasks_success_graph)
      copy(filename_network_summary_graph,config.kascheri12_github_io_dir+filename_network_summary_graph)
      # copy(filename_change_in_successes,config.kascheri12_github_io_dir+filename_change_in_successes)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      od = os.getcwd()
      os.chdir(config.kascheri12_github_io_dir)
      os.system('git checkout master')
      os.system('git add ' + filename_subtasks_success_graph)
      os.system('git add ' + filename_network_summary_graph)
      # os.system('git add ' + filename_change_in_successes)
      os.system('git commit -m "automated commit for golem-network-graphs"')
      os.system('git push')
      os.chdir(od)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print("End refresh_graph: "+time.strftime("%Y%m%d-%H:%M%Z",time.localtime()))

def main():

    nl = Node_Logging()
    l = task.LoopingCall(nl.take_network_snapshot)
    l.start(nl._timeout) # call every sixty seconds

    if nl._do_refresh_graph:
      rg = task.LoopingCall(nl.refresh_graph)
      rg.start(nl._refresh_graph_timeout)

    reactor.run()

if __name__ == '__main__':
    main()
