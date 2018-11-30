from apscheduler.schedulers.blocking import BlockingScheduler
import scan_nodes as sn
import time, config, db
from datetime import date
from twisted.internet import task
from twisted.internet import reactor
from shutil import move
import os, traceback, sys

class Node_Logging():

  def __init__(self):
    self._timeout = 5 * 60.0 # Five @ Sixty seconds

  def take_network_snapshot(self):
    if not os.path.exists('node_logs'):
      os.makedirs('node_logs')
    FILE_SIZE_LIMIT = 999999999  # 999MB
    timestamp = str(round(time.time()))
    d = date.fromtimestamp(time.time())
    pretty_date = "%s%s%s" % (d.year,d.month,d.day)
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)
    db_timestamp = time.strftime('%Y-%m-%d %H:%M:%S',lt)
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
    
    # Try writing the data to the database
    try:
      if active_nodes is not None and len(active_nodes) > 0:
        conn = db.DB()
        for node in active_nodes:
          conn.insert_node_record_data((db_timestamp, *tuple(node.values())[:-1]))
    except:
      print("Issues adding records to mysql database")

def main():

    nl = Node_Logging()
    l = task.LoopingCall(nl.take_network_snapshot)
    l.start(nl._timeout) # call every sixty seconds

    reactor.run()

if __name__ == '__main__':
    main()
