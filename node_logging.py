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

  _timeout = 30 * 60.0 # Thirty @ Sixty seconds
  _refresh_graph_timeout = 240 * 60 # 4 hours

  def __init__(self):
    pass

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
      with open(file_path,append_param) as f:
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

  # 20171118 - Not used anymore
  def add_node_count_log(self):
    timestamp = str(round(time.time()))
    try:
      with open('node_logs/'+timestamp+'.log','w') as f:
        active_nodes = sn.get_active_node_list()
        if len(active_nodes) > 0:
          f.write("timestamp,version,node_name,subtasks_success,os,node_id,performance_lux,performance_blender,performance_general,cpu_cores\n")
          for node in active_nodes:
            f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (timestamp,str(node['version']),str(node['node_name']),str(node['subtasks_success']),node['os'],str(node['node_id']),str(node['performance_lux']),str(node['performance_blender']),str(node['performance_general']),str(node['cpu_cores'])))
    except:
      print("Error somewhere... probably network connection.")

  def refresh_graph(self):
    filename = ''
    d = []
    a = al.Analyze_Logs()
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)

    try:
      d = a.load_data()
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error retreiving data<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error retreiving data<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      filename = a.print_node_success_over_time_graph(d)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error creating graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      copy(filename,config.kascheri12_github_io_file_loc)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error printing and/or moving graph<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    try:
      od = os.getcwd()
      os.chdir(config.kascheri12_github_io_dir)
      os.system('git checkout master')
      os.system('git add ' + config.kascheri12_github_io_filename)
      os.system('git commit -m "automated commit for golem-network-graph"')
      os.system('git push')
      os.chdir(od)
    except:
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")
      traceback.print_exc(file=sys.stdout)
      print(pt + " - >>>>>>>>>>>>>>>>>>>>>>>>>>>Error during git process<<<<<<<<<<<<<<<<<<<<<<<<<<<")

def main():

    nl = Node_Logging()
    l = task.LoopingCall(nl.take_network_snapshot)
    l.start(nl._timeout) # call every sixty seconds

    rg = task.LoopingCall(nl.refresh_graph)
    rg.start(nl._refresh_graph_timeout)

    reactor.run()

if __name__ == '__main__':
    main()
