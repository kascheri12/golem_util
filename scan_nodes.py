
import sys, csv, time, requests
import numpy as np
import pandas as pd
import datetime as dt
from math import floor

dump_url = "https://stats.golem.network/dump"

def __main__(argv):
  load_print_kascheri_data()

def add_node_count_log():
  with open('node_count.log','a') as f:
    f.write("%s|%s\n" % (str(time.time()),get_active_node_count()))

def get_active_node_list():
  return load_recent_data()

def get_active_node_count():
  return len(load_recent_data())

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
  seen_at = dt.datetime.fromtimestamp(get_float(t)*.001)
  now = dt.datetime.now()
  its_been = (now - seen_at)
  return str(its_been)

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
    now = dt.datetime.now()
    try:
      node_last_seen = dt.datetime.fromtimestamp(get_float(c[3])*.001)
    except:
      print('Skipping: %s, last_seen: %s' % (c[0][:10], c[3]))
      continue
    if (now - node_last_seen).seconds > 300:
      continue
    for i in range(len(header)):
      node[header[i]] = c[i]
    node['last_seen_calc'] = calc_last_seen_time(node['last_seen'])
    node['performance_general'] = str(get_float(node['performance_general']))
    node['performance_blender'] = str(get_float(node['performance_blender']))
    node['performance_lux'] = str(get_float(node['performance_lux']))
    node['allowed_resource_size'] = str(get_float(node['allowed_resource_size']))
    node['allowed_resource_memory'] = str(get_float(node['allowed_resource_memory']))
    node['min_price'] = str(get_float(node['min_price']))
    node['max_price'] = str(get_float(node['max_price']))
    node['subtasks_success'] = str(get_float(node['subtasks_success']))
    node['subtasks_error'] = str(get_float(node['subtasks_error']))
    node['subtasks_timeout'] = str(get_float(node['subtasks_timeout']))
    node['tasks_requested'] = str(get_float(node['tasks_requested']))
    node['known_tasks'] = str(get_float(node['known_tasks']))
    node['supported_tasks'] = str(get_float(node['supported_tasks']))
    node['rs_tasks_cnt'] = str(get_float(node['rs_tasks_cnt']))
    node['rs_finished_task_cnt'] = str(get_float(node['rs_finished_task_cnt']))
    node['rs_requested_subtasks_cnt'] = str(get_float(node['rs_requested_subtasks_cnt']))
    node['rs_collected_results_cnt'] = str(get_float(node['rs_collected_results_cnt']))
    node['rs_verified_results_cnt'] = str(get_float(node['rs_verified_results_cnt']))
    node['rs_timed_out_subtasks_cnt'] = str(get_float(node['rs_timed_out_subtasks_cnt']))
    node['rs_not_downloadable_subtasks_cnt'] = str(get_float(node['rs_not_downloadable_subtasks_cnt']))
    node['rs_failed_subtasks_cnt'] = str(get_float(node['rs_failed_subtasks_cnt']))
    node['rs_work_offers_cnt'] = str(get_float(node['rs_work_offers_cnt']))
    node['rs_finished_ok_cnt'] = str(get_float(node['rs_finished_ok_cnt']))
    node['rs_finished_with_failures_cnt'] = str(get_float(node['rs_finished_with_failures_cnt']))
    node['rs_failed_cnt'] = str(get_float(node['rs_failed_cnt']))
    data_o.append(node)
  return data_o

def get_float(s):
  try:
    return float(s)
  except ValueError:
    return 0.0


if __name__ == "__main__":
    __main__(sys.argv[1:])
