from apscheduler.schedulers.blocking import BlockingScheduler
import scan_nodes as sn
import time
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move
import analyze_logs as al
import os, traceback, sys

timeout = 5.0 # Thirty @ Sixty seconds

def main():
    l = task.LoopingCall(take_network_snapshot)
    l.start(timeout) # call every sixty seconds

    rg = task.LoopingCall(refresh_graph)
    rg.start(timeout)
    
    reactor.run()

def check_for_node_log_dir():
  if not os.path.exists('node_logs'):
    os.makedirs('node_logs')

def take_network_snapshot():
  check_for_node_log_dir()
  FILE_SIZE_LIMIT = 999999999  # 999MB
  timestamp = str(round(time.time()))
  d = date.fromtimestamp(time.time())
  pretty_date = "%s%s%s" % (d.year,d.month,d.day)
  filename = 'network.log'
  log_dir = 'node_logs/'
  file_path = log_dir+filename
  append_param = 'a'
  
  # Finalize file_name
  # If filesize exceeds the limit
  if os.path.exists(file_path):
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
    print("Error getting active nodes.. probably network connection")

  # Try writing the data to the file
  try:
    with open(file_path,append_param) as f:
      # Check that there are nodes on the network..
      if len(active_nodes) > 0:
        # Is this the first line of the file? If so, write the header
        if append_param == 'w':
          f.write("%s\n" % (",".join(["timestamp"]+list(x for x in active_nodes[0].keys()))))
        # Write all the data for each node. Include the timestamp this data set
        for node in active_nodes:
          f.write("%s\n" % (",".join([timestamp]+list(str(x) for x in node.values()))))
  except:
    print("Error with writing the file...")
    print("file_path:"+file_path)
    print("append_param:"+append_param)
    traceback.print_exc(file=sys.stdout)

def add_node_count_log():
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


def refresh_graph():
  try:
    d = al.load_data()
  except:
    print("Error retreiving data")
    traceback.print_exc(file=sys.stdout)

  try:
    filename = al.print_node_success_over_time_graph(d)
  except:
    print("Error creating graph")
    traceback.print_exc(file=sys.stdout)

  try:
    move(filename,'/Volumes/C/wamp64/www/kennethascheri/public_html/golem/index.html')
  except:
    print("Error printing and/or moving graph.")
    traceback.print_exc(file=sys.stdout)
    

if __name__ == '__main__':
    main()
