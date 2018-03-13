import csv, os, time, sys, plotly, traceback
from distutils.version import LooseVersion
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from random import *
import igraph as ig
from plotly import tools
import plotly.graph_objs as go
from os import remove
from shutil import move


class Analyze_Logs:
  
  def __init__(self):
    self.d = self.load_data()

  def load_header_indices(self,header):
    # Inices are constant throughout
    self._ts_index = header.index('timestamp')
    self._pg_index = header.index('performance_general')
    self._pb_index = header.index('performance_blender')
    self._pl_index = header.index('performance_lux')
    self._ars_index = header.index('allowed_resource_size')
    self._arm_index = header.index('allowed_resource_memory')
    self._cc_index = header.index('cpu_cores')
    self._ss_index = header.index('subtasks_success')
    self._id_index = header.index('node_id')
    self._nn_index = header.index('node_name')
    
  def print_nodes(self,d,sort_method=None,ascending=False):
    cols = ['timestamp','version','node_name','subtasks_success','os','node_id','performance_lux','performance_blender','performance_general','cpu_cores']
    pd.set_option('display.max_columns',0)
    pd.set_option('display.max_colwidth',25)
    pd.options.display.float_format = '{:.5f}'.format
    df = pd.DataFrame(d,columns=cols)
    if sort_method is not None:
      df1 = df.sort_values(sort_method,ascending=ascending)
      print(df1)
    else:
      print(df)

  def get_distinct_successes_dict(self,d):
    dist_nodes = {}
    for record in d['data']:
      name = self.get_node_name(d['header'],record)
      if dist_nodes.get(name) is None:
        dist_nodes[name] = self.get_max_success_for_node(record,d)
    return dist_nodes

  def get_max_success_for_node(seflf,node,d):
    return max([x[self._ss_index] for x in d['data'] if x[self._id_index] == node[self._id_index]])

  def get_max_successes(self,d):
    return max([x[3] for x in d['data']])

  def get_node_name(self,header,node):
    name = str(node[self._nn_index])+"("+node[self._id_index][:20]+")"
    return name

  def get_nodes_in_snapshot(self,timestamp):
    SUCCESS_THRESHOLD = 5
    node_list = [x for x in self.d['data'] if x[self._ts_index] == timestamp]
    sl = []
    for x in node_list:
      try:
        if float(x[self._ss_index]) >= SUCCESS_THRESHOLD:
          sl.append(x)
      except ValueError:
        pass
    return sl

  def build_y_axis_dict(self,d,x_axis):
    nodes = d
    y_axis_dict = {}

    for timestamp in x_axis:
      # for each record in the list of data points cooresponding to the timestamp
      # and the node's total success are greater than the threshold
      nodes_in_snapshot = self.get_nodes_in_snapshot(timestamp)
      for record in nodes_in_snapshot:
        # Define the key as the node's name plus first xx characters of the node_id
        key = self.get_node_name(nodes['header'],record)
        # Check if this dict key exists in the dict of nodes to be plotted
        # Init dict value as list
        if y_axis_dict.get(key) is None:
          y_axis_dict[key] = []
        # Append the specific x-y coordinate with the formatted
        # timestamp and the number of successful subtasks
        y_axis_dict[key].append([self.get_formatted_time(timestamp),record[self._ss_index] or None])
    return y_axis_dict

  def build_y_axis_dict_for_network_summary(self,d,x_axis):
    y_axis_dict = {    
        'Node Count':[],
        'Allowed Resource Size':[],
        'Allowed Resource Memory':[],
        'CPU Cores':[]
    }
    nodes = d
    key_names = [x for x in y_axis_dict.keys()]
    
    for timestamp in x_axis:
      connected_nodes = [x for x in nodes['data'] if x[self._ts_index] == timestamp]
      formatted_ts = self.get_formatted_time(timestamp)
      
      node_count = len(connected_nodes)
      y_axis_dict[key_names[0]].append([formatted_ts,node_count])
      
      summary_allowed_resources = sum([int(x[self._ars_index]) for x in connected_nodes if x[self._ars_index] != ''])
      y_axis_dict[key_names[1]].append([formatted_ts,summary_allowed_resources])
      
      summary_allowed_memory = sum([int(x[self._arm_index]) for x in connected_nodes if x[self._arm_index] != ''])
      y_axis_dict[key_names[2]].append([formatted_ts,summary_allowed_memory])
      
      summary_cpu_cores = sum([int(x[self._cc_index]) for x in connected_nodes if x[self._cc_index] != ''])
      y_axis_dict[key_names[3]].append([formatted_ts,summary_cpu_cores])
    return y_axis_dict

  def build_y_axis_dict_for_change_in_subtasks(self,x_axis):
    nodes = self.d
    y_axis_dict = {
        'Node Count':[],
        'Subtask Computation Change between logs':[],
        'Subtask Computation Change in 1 hour':[],
        'Subtask Computation Change in 24 hours':[],
        'Subtask Computation Change in 7 days':[]
    }
    key_names = [x for x in y_axis_dict.keys()]
    subtotal_1_hr, subtotal_24_hr, subtotal_7_day = 0, 0, 0
    i_1_hr, i_24_hr, i_7_day = 0, 0, 0
    
    for i in range(len(x_axis)):
      timestamp = x_axis[i]
      cn = [x for x in nodes['data'] if x[self._ts_index] == timestamp]
      formatted_ts = self.get_formatted_time(timestamp)
      
      node_count = len(cn)
      y_axis_dict[key_names[0]].append([formatted_ts,node_count])
      subtotal_current = sum([float(x[self._ss_index]) for x in cn])
      
      if i == 0:
        y_axis_dict[key_names[2]].append([formatted_ts,subtotal_current])
        y_axis_dict[key_names[3]].append([formatted_ts,subtotal_current])
        y_axis_dict[key_names[4]].append([formatted_ts,subtotal_current])
        
      if i > 0:
        cnp = [x for x in nodes['data'] if x[self._ts_index] == x_axis[i-1]]
        subtotal_prev = sum([float(x[self._ss_index]) for x in cnp])
        y_axis_dict[key_names[1]].append([formatted_ts,subtotal_current-subtotal_prev])
        
        
      #if the time between timestamp and x_axis[i_1_hr]
      # is greater than 1hr then do the computation and
      # mark x,y coordinates
      if i>0 and (timestamp - x_axis[i_1_hr]) >= 3600:
        # calculate sum of subtasks completed in network from all timestamps
        # between i_1_hr and the current timestamp
        sub_cur = subtotal_1_hr + sum([float(x[self._ss_index]) for x in cn])
        
        # subtract the value just calculated above for the subtasks completed
        # from the previously appended value in y_axis_dict
        y_axis_dict[key_names[2]].append([formatted_ts,sub_cur - y_axis_dict[key_names[2]][-1][1]])
        
        # set the new index for i_1_hr
        i_1_hr = i
        subtotal_1_hr = 0
      else:
        subtotal_1_hr += subtotal_current
  
        
      if i>0 and (timestamp - x_axis[i_24_hr]) >= 86400:
        sub_cur = subtotal_24_hr + sum([float(x[self._ss_index]) for x in cn])
        y_axis_dict[key_names[3]].append([formatted_ts, sub_cur - y_axis_dict[key_names[3]][-1][1]])
        i_24_hr = i
        subtotal_24_hr = 0
      else:
        subtotal_24_hr += subtotal_current
      
      if i>0 and (timestamp - x_axis[i_7_day]) >= 604800:
        sub_cur = subtotal_7_day + sum([float(x[self._ss_index]) for x in cn])
        y_axis_dict[key_names[4]].append([formatted_ts, sub_cur - y_axis_dict[key_names[4]][-1][1]])
        i_7_day = i
        subtotal_7_day = 0
      else:
        subtotal_7_day += subtotal_current
        
    return y_axis_dict
  
  def build_x_axis(self,d,log_cutoff_date=dt(2017,1,1)):
    x_axis = sorted(list(set([x[self._ts_index] for x in d['data'] if dt.fromtimestamp(x[self._ts_index]) > log_cutoff_date])))
    return x_axis

  def print_change_in_subtask_success_graph(self,d,days_since_cutoff):
    filename = 'golem-network-change-in-subtask-success.html'
    log_cutoff_date = dt.today() - timedelta(days=days_since_cutoff)
    
    x_axis = self.build_x_axis(d,log_cutoff_date)
    y_axis_dict = self.build_y_axis_dict_for_change_in_subtasks(x_axis)
    traces = []
    lt = time.localtime()
    pt = "%s%s%s-%s:%s%s" % (lt.tm_year,lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,time.tzname[0])
    
    for key in y_axis_dict.keys():
      traces.append(go.Scatter(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      mode='lines',
      connectgaps=False,
      name=key
      ))
    layout = dict(title = 'Golem Network Change in Subtask Success',
                xaxis = dict(title = 'Time'),
                yaxis = dict(title = 'Change in Successful Subtask Computations on Golem Network')
                )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filename, auto_open=False)
    self.inject_google_analytics(filename)
    return filename

  def print_network_summary_over_time_graph(self,d,days_since_cutoff):
    filename = 'golem-network.html'
    log_cutoff_date = dt.today() - timedelta(days=days_since_cutoff)
    
    x_axis = self.build_x_axis(d,log_cutoff_date)
    y_axis_dict = self.build_y_axis_dict_for_network_summary(d,x_axis)
    traces = []
    lt = time.localtime()
    pt = "%s%s%s-%s:%s%s" % (lt.tm_year,lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,time.tzname[0])
    
    for key in y_axis_dict.keys():
      traces.append(go.Scatter(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      mode='lines',
      name=key
      ))
      
    fig = tools.make_subplots(rows=5, cols=1, specs=[[{}], [{}], [{}], [{}], [{}]],
                              shared_xaxes=True,
                              vertical_spacing=1)
    
    fig.append_trace(traces[0], 5, 1) # Node_Count
    fig.append_trace(traces[3], 4, 1) # CPU_Cores
    fig.append_trace(traces[2], 3, 1) # Resource Memory
    fig.append_trace(traces[1], 2, 1) # Resource Size
    
    

    fig['layout'].update(title='Golem Network Statistics Summary',
        xaxis=dict(
          rangeselector=dict(
            buttons=list([
              dict(count=4,
                 label='4hr',
                 step='hour',
                 stepmode='backward'),
              dict(count=24,
                 label='24hr',
                 step='hour',
                 stepmode='backward'),
              dict(count=10,
                 label='10d',
                 step='day',
                 stepmode='backward'),
              dict(count=20,
                 label='20d',
                 step='day',
                 stepmode='backward'),
              dict(count=1,
                 label='1m',
                 step='month',
                 stepmode='backward'),
              dict(count=3,
                 label='3m',
                 step='month',
                 stepmode='backward'),
              dict(count=6,
                 label='6m',
                 step='month',
                 stepmode='backward'),
              dict(step='all')
            ])
          ),
          rangeslider=dict(),
          type='date',
          domain=[0.02,1.0]
        ),
        yaxis = dict(side='right',
                    anchor='x'),
        yaxis2 = dict(side='left',
                    position='0'),
        yaxis3 = dict(side='left',
                    position='0'),
        yaxis4 = dict(side='left',
                    position='0'),
        yaxis5 = dict(side='left',
                    anchor='y5'))
    
    plotly.offline.plot(fig, filename=filename, auto_open=False)
    self.inject_google_analytics(filename)
    return filename

  def print_node_success_over_time_graph(self,d,days_since_cutoff):
    filename = 'golem-network-success-report.html'
    log_cutoff_date = dt.today() - timedelta(days=days_since_cutoff)
    
    x_axis = self.build_x_axis(d,log_cutoff_date)
    y_axis_dict = self.build_y_axis_dict(d,x_axis)
    traces = []
    lt = time.localtime()
    pt = time.strftime("%Y%m%d-%H:%M%Z",lt)

    # For each node to be plotted
    for key in sorted(y_axis_dict.keys()):
      # Append a scatter plot for the specific node based on time and subtasks successes
      traces.append(go.Scatter(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      mode='lines',
      connectgaps=None,
      name=key
      ))
    
    layout = dict(title = 'Golem Network Successful Subtask Computations by Node as of ' + pt,
              xaxis = dict(title = 'Time'),
              yaxis = dict(title = 'Successful Subtask Computations on Golem Network')
              )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filename, auto_open=False)
    self.inject_google_analytics(filename)
    return filename

  def inject_google_analytics(self,filename):
    analytics_string = '''
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-109439081-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'UA-109439081-1');
        </script>
        '''
    with open(filename,'rt') as f:
      r = f.read()
      with open(filename+'.tmp','w') as f2:
        f2.write(''.join(r[:-14])+analytics_string+''.join(r[-14:]))
    remove(filename)
    move(filename+'.tmp', filename)

  def get_formatted_time(self,timestamp):
    t = time.localtime(timestamp)
    # return time.strftime("%Y%m%d|%H:%M:%S",time.localtime(t))
    return dt(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)

  def find_max_version_nodes(self,d_in):
    max_version = find_max_version(d_in)
    mnl = []
    for node in d_in['data']:
      if node[1] == max_version:
        mnl.append(node)
    return mnl

  def find_max_version(self,d_in):
    versions_list = filter(None,[x[1] for x in d_in['data']])
    vl = sorted(versions_list, key=LooseVersion)
    return vl[-1]

  def load_data(self):
    d = self.load_new_data()
    return d

  def clean_data_row(self,header,row):
    nr = row

    try:
      nr[self._ts_index] = int(row[self._ts_index])
    except IndexError:
      nr[self._ts_index] = 0
    # Eliminate null values in subtasks_success column
    ss_index = header.index('subtasks_success')
    try:
      nr[ss_index] = float(row[ss_index])
    except IndexError:
      nr[ss_index] = 0
    except ValueError:
      nr[ss_index] = 0
    return nr

  def load_new_data(self):
    print("Begin load_new_data. Loading each file into data")
    all_data = {
      'data':[],
      'header':[]
    }
    for filename in [x for x in os.listdir('node_logs/') if x.find('network') != -1 or x.find('old_logs.log') != -1]:
      try:
        with open('node_logs/'+filename,'rt',encoding="UTF-8") as f:
          print("reading: "+filename)
          reader = csv.reader(f,delimiter=',')
          d = []
          first_row = True
          for row in reader:
            # This call is to check whether column 3, node_id exists.
            # Might not be needed anymore. It was caused by empty files that were written during network outage.
            # I've since added try/catch so those files won't exist in the future.
            row[3]
            if first_row:
              first_row = False
              all_data['header'] = row
              self.load_header_indices(all_data['header'])
            else:
              all_data['data'].append(self.clean_data_row(all_data['header'],row))
      except:
        print("Error in load_new_data - for %s in network.log files" % (filename))
        traceback.print_exc(file=sys.stdout)
    print("End load_new_data.")
    return all_data

  def load_raw_data(self):
    all_data = {
      'filenames':[],
      'data':[],
      'header':[]
    }
    for filename in [x for x in os.listdir('node_logs/') if x.find('network') == -1 and x.find('.DS_Store') == -1]:
      try:
        with open('node_logs/'+filename,'rt') as f:
          reader = csv.reader(f,delimiter=',')
          d = []
          first_row = True
          for row in reader:
            try:
              row[3]
              if first_row:
                first_row = False
                all_data['header'] = row
              else:
                all_data['data'].append(row)
            except:
              print("error loading row: ")
          all_data['filenames'].append(filename)
      except IndexError:
        print("Catching exception because file is empty and no data found.")
    return all_data

  def format_old_log_data(self):
    filename = "old_logs.log"
    directory = "node_logs/"
    filepath = directory + filename
    d = load_raw_data()
    new_header = load_new_data()['header']
    nodes_to_write = []
    for i in range(len(d['data'])):
      new_node = []
      for j in range(len(new_header)):
        try:
          h_index = d['header'].index(new_header[j])
        except ValueError:
          h_index = -1
        if h_index > -1:
          new_node.append(d['data'][i][h_index])
        else:
          new_node.append('')
      nodes_to_write.append(new_node)
    try:
      with open(filepath,'w') as f:
        f.write("%s\n" % (','.join(new_header)))
        for node in nodes_to_write:
          f.write("%s\n" % (','.join(node)))
    except:
      print("Error writing the new log file with old log data")

  def fix_files_again(self,filenames):
    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:126])+''.join(r[127:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp', 'node_logs/'+filename)

  def last_fix_maybe(self,filenames):
    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:122])+filename[:-4]+''.join(r[132:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp','node_logs/'+filename)

  def fix_files(self,filenames):
    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:121])+"\n"+''.join(r[122:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp', 'node_logs/'+filename)
