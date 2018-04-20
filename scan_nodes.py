
import sys
import csv
import numpy as np
import pandas as pd
import requests
import time
from math import floor

dump_url = "https://stats.golem.network/dump"

def __main__(argv):
  load_print_kascheri_data()

def add_node_count_log():
  with open('node_count.log','a') as f:
    f.write("%s|%s\n" % (str(time.time()),get_active_node_count()))

def get_active_node_list():
  return filter_latest_minutes(load_recent_data(),5)

def get_active_node_count():
  return len(filter_latest_minutes(load_recent_data(),5))

def load_print_kascheri_data():
  sort_by = ['last_seen']
  ascending = [False]
  print_nodes(load_kascheri_data(),sort_by,ascending)

def load_print_recent_data_by_success():
  sort_by = ['subtasks_success','last_seen']
  ascending = [False,False]
  print_nodes(filter_latest_minutes(load_recent_data(),5),sort_by,ascending)

def load_print_recent_data_by_performance():
  sort_by = ['performance_blender','last_seen']
  ascending = [False, False]
  print_nodes(filter_latest_minutes(load_recent_data(),5),sort_by,ascending)

def valid_seconds(s):
  try:
    return int(s)
  except ValueError:
    return 999999999

def filter_latest_minutes(d,minutes):
  dn = []
  for item in d:
    if float(calc_last_seen_time(item['last_seen'])['seconds']) <= minutes*60:
      dn.append(item)
  return dn

def print_nodes(d,sort_method=None,ascending=False):
  cols = ['node_name','instance_name','os','last_seen_calc','last_seen','digital_loc','physical_loc','version','performance_blender','tasks_requested','subtasks_success']
  pd.set_option('display.max_columns',0)
  pd.set_option('display.max_colwidth',25)
  pd.options.display.float_format = '{:.5f}'.format
  df = pd.DataFrame(d,columns=cols)
  if sort_method is not None:
    df1 = df.sort_values(sort_method,ascending=ascending)
    print(df1)
  else:
    print(df)

def calc_last_seen_time(t):
  seen_at = t
  its_been = round(time.time()) - float(valid_seconds(seen_at))/1000
  last_seen_obj = {
    'seconds' : its_been
    ,'minutes' : its_been/60
    ,'hours' : its_been/60/60
    ,'days' : its_been/60/60/24
    ,'years' : its_been/60/60/24/365.25
  }
  return last_seen_obj

def last_seen_obj_to_string(obj):
  os = ""

  if floor(obj['years']) >= 1:
     os = "{:1.0f}y:".format(floor(obj['years']))
     obj['days'] -= 365 * floor(obj['years'])
  if floor(obj['days']) >= 1:
    os += "{:1.0f}d:".format(floor(obj['days']))
    obj['hours'] -= 24 * floor(obj['days'])
  if floor(obj['hours']) >= 1:
    os += "{:1.0f}h:".format(floor(obj['hours']))
    obj['minutes'] -= (24 * floor(obj['days']) + 60 * floor(obj['hours']))
  if floor(obj['minutes']) >= 1:
    os += "{:1.0f}m:".format(floor(obj['minutes']))
    obj['seconds'] -= (24 * floor(obj['days']) + 60 * floor(obj['hours']) + 60 * floor(obj['minutes']))
  os+="{:1.0f}s".format(obj['seconds'])
  return os

def load_recent_data():
  return load_realtime_data()

def load_kascheri_data():
  context = []
  rtd = load_realtime_data()
  kd = None #load_kascheri_node_info()
  for i in range(len(kd)):
    context.append(kd[i].copy())
    for r in rtd:
      if r['node_name'] == kd[i]['node_name']:
        context[i].update(r)
  return context

def find_max_time(data):
  max_time = None
  for node in data:
    if node['last_seen'] is not 'NaN' and float(node['last_seen']) > 0:
      if max_time is not None:
        if max_time < node['last_seen']:
          max_time = node['last_seen']
      else:
        max_time = node['last_seen']
  return max_time

def find_min_time(data):
  min_time = None
  for node in data:
    if node['last_seen'] is not 'NaN' and float(node['last_seen']) > 0:
      if min_time is not None:
        if min_time > node['last_seen']:
          min_time = node['last_seen']
      else:
        min_time = node['last_seen']
  return min_time

def load_realtime_data():
  d_file = requests.get(dump_url)
  data_t = []
  data_o = []

  t = d_file.text.split('\n')
  header = t[0].split(',')
  t.pop(0)
  t.pop(len(t)-1)
  for row in t:
    c = row.split(',')
    node = {}
    for i in range(len(header)):
      node[header[i]] = c[i]
    node['last_seen_calc'] = last_seen_obj_to_string(calc_last_seen_time(node['last_seen']))
    node['subtasks_success'] = get_float(node['subtasks_success'])
    node['tasks_requested'] = get_float(node['tasks_requested'])
    node['performance_blender'] = get_float(node['performance_blender'])
    node['performance_lux'] = get_float(node['performance_lux'])
    node['performance_general'] = get_float(node['performance_general'])
    node['known_tasks'] = get_float(node['known_tasks'])
    node['supported_tasks'] = get_float(node['supported_tasks'])
    data_o.append(node)
  return data_o

def get_float(s):
  try:
    return float(s)
  except ValueError:
    return 0.0


if __name__ == "__main__":
    __main__(sys.argv[1:])
