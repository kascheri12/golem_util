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
    timestamp = str(round(time.time()))
    d = date.fromtimestamp(time.time())
    pretty_date = "%s%s%s" % (d.year,d.month,d.day)
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)
    db_timestamp = time.strftime('%Y-%m-%d %H:%M:%S',lt)
    active_nodes = []

    # Try retreiving the active nodes in the network
    try:
      active_nodes = sn.get_active_node_list()
    except:
      print(pt + " - Error getting active nodes.. probably network connection")
    
    # Try writing the data to the database
    if active_nodes is not None and len(active_nodes) > 0:
      conn = db.DB("PROD")
      for node in active_nodes:
        try:
          conn.insert_node_record_data((db_timestamp, *tuple(str(node.values()))[:-1]))
        except:
          print("Could not insert records for %")

def main():

    nl = Node_Logging()
    l = task.LoopingCall(nl.take_network_snapshot)
    l.start(nl._timeout) # call every sixty seconds

    reactor.run()

if __name__ == '__main__':
    main()
