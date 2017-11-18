import csv, os, time, sys, plotly
from distutils.version import LooseVersion
import pandas as pd
from datetime import datetime as dt
from random import *
import igraph as ig
import plotly.graph_objs as go

class Analyze_Logs:
  def __init__(self):
    pass

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

  def print_3d_file(self):
    filename="golem-network-3d.html"
    d = load_data()
    jf = build_json_data_object(d)
    N=len(jf['nodes'])
    L=len(jf['links'])
    Edges=[(jf['links'][k]['source'], jf['links'][k]['target']) for k in range(L)]

    G=ig.Graph(Edges, directed=False)

    labels=[]
    group=[]
    for node in jf['nodes']:
      labels.append(node['name'])
      group.append(node['group'])

    layt=G.layout('kk', dim=3)

    # print([layt[k][0] for k in range(N)])

    Xn = [layt[k][0] for k in range(N)] # x-coordinates of nodes
    Yn = [layt[k][1] for k in range(N)] # y-coordinates
    Zn = [layt[k][2] for k in range(N)] # z-coordinates
    Xe=[]
    Ye=[]
    Ze=[]
    for e in Edges:
      Xe+=[layt[e[0]][0],layt[e[1]][0], None]# x-coordinates of edge ends
      Ye+=[layt[e[0]][1],layt[e[1]][1], None]
      Ze+=[layt[e[0]][2],layt[e[1]][2], None]

    trace1=go.Scatter3d(x=Xe,
                   y=Ye,
                   z=Ze,
                   mode='lines',
                   line=go.Line(color='rgb(125,125,125)', width=1),
                   hoverinfo='none'
                   )
    trace2=go.Scatter3d(x=Xn,
                   y=Yn,
                   z=Zn,
                   mode='markers',
                   name='actors',
                   marker=go.Marker(symbol='dot',
                                 size=6,
                                 color=group,
                                 colorscale='Viridis',
                                 line=go.Line(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=labels,
                   hoverinfo='text'
                   )

    axis=dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
            )

    layout = go.Layout(
           title="Network of nodes connected and computing subtasks on the Golem Network (3D visualization)",
           width=1000,
           height=1000,
           showlegend=False,
           scene=go.Scene(
             xaxis=go.XAxis(axis),
             yaxis=go.YAxis(axis),
             zaxis=go.ZAxis(axis),
          ),
       margin=go.Margin(
          t=100
      ),
      hovermode='closest',
      annotations=go.Annotations([
             go.Annotation(
             showarrow=False,
              text="Data source: <a href='http://stats.golem.network/'>Golem Network</a>",
              xref='paper',
              yref='paper',
              x=0,
              y=0.1,
              xanchor='left',
              yanchor='bottom',
              font=go.Font(
              size=14
              )
              )
          ]),    )

    data=go.Data([trace1, trace2])
    fig=go.Figure(data=data, layout=layout)

    plotly.offline.plot(fig, filename=filename, auto_open=True)

  def build_json_data_object(self,d):
    max_timestamp = max(sorted(list(set([x[0] for x in d['data']]))))
    nodes_and_success_dict = get_distinct_successes_dict(d)
    all_max_success = get_max_successes(d)
    my_dict = {
      'nodes' : get_nodes_list(d,max_timestamp,nodes_and_success_dict,all_max_success),
      'links' : get_links_list(d,max_timestamp,nodes_and_success_dict,all_max_success)
    }
    return my_dict

  def get_target(self,targets,key):
    sl = sorted([(x,y) for x,y in targets.items() if y > 0])
    r = randint(1,len(sl))
    return r-1

  def get_links_list(self,d,max_timestamp,nodes_and_success_dict,all_max_success):
    list_of_links = []
    for key in nodes_and_success_dict.keys():
      r = randint(0,2)
      for i in range(r):
        list_of_links.append({"source":list(nodes_and_success_dict.keys()).index(key),"target":get_target(nodes_and_success_dict,key)})
    return list_of_links

  def get_nodes_list(self,d,max_timestamp,nodes_and_success_dict,all_max_success):
    import numpy as np
    sl = [x for x in nodes_and_success_dict.values()]
    avg = np.mean(sl)
    node_list = []
    for record in d['data']:
      name = get_node_name(record)
      if name not in [x['name'] for x in node_list]:
        node_dict = {
            'name':get_node_name(record),
            'group':get_node_group(record,d,avg,nodes_and_success_dict[name])
        }
        node_list.append(node_dict)
    return node_list

  def get_node_group(self,node,d,avg,max_success_for_node):
    if max_success_for_node >= avg + avg * .9:
      return 10
    if max_success_for_node >= avg + avg * .7:
      return 9
    if max_success_for_node >= avg + avg * .5:
      return 8
    if max_success_for_node >= avg + avg * .3:
      return 7
    if max_success_for_node >= avg + avg * .1:
      return 6
    if max_success_for_node >= avg:
      return 5
    if max_success_for_node >= avg - avg * .3:
      return 4
    if max_success_for_node >= avg - avg * .5:
      return 3
    if max_success_for_node >= avg - avg * .7:
      return 2
    if max_success_for_node >= avg - avg * .9:
      return 1
    if max_success_for_node > 0:
      return 1
    else:
      return 0


  def get_distinct_successes_dict(self,d):
    dist_nodes = {}
    for record in d['data']:
      name = get_node_name(record)
      if dist_nodes.get(name) is None:
        dist_nodes[name] = get_max_success_for_node(record,d)
    return dist_nodes

  def get_max_success_for_node(seflf,node,d):
    return max([x[3] for x in d['data'] if x[5] == node[5]])

  def get_max_successes(self,d):
    return max([x[3] for x in d['data']])

  def get_node_name(self,header,node):
    id_index = header.index('node_id')
    nn_index = header.index('node_name')
    name = str(node[nn_index])+"("+node[id_index][:10]+")"
    return name

  def build_y_axis_dict(self,d,x_axis,ts_index,success_index):
    SUCCESS_THRESHOLD = 5
    nodes = d
    y_axis_dict = {}

    for timestamp in x_axis:
      # for each record in the list of data points cooresponding to the timestamp
      # and the node's total success are greater than the threshold
      for record in [x for x in nodes['data'] if x[ts_index] == timestamp and float(x[success_index]) >= SUCCESS_THRESHOLD]:
        # Define the key as the node's name plus first 10 characters of the node_id
        key = self.get_node_name(nodes['header'],record)
        # Check if this dict key exists in the dict of nodes to be plotted
        # Init dict value as list
        if y_axis_dict.get(key) is None:
          y_axis_dict[key] = []
        # Append the specific x-y coordinate with the formatted
        # timestamp and the number of successful subtasks
        y_axis_dict[key].append([self.get_formatted_time(timestamp),record[success_index] or None])
    return y_axis_dict

  def print_node_success_over_time_graph(self,d):
    filename = 'golem-network-success-report.html'

    # load distinct list of timestamps from column 0.
    ts_index = d['header'].index('timestamp')
    success_index = d['header'].index('subtasks_success')
    x_axis = sorted(list(set([x[ts_index] for x in d['data']])))
    y_axis_dict = self.build_y_axis_dict(d,x_axis,ts_index,success_index)
    traces = []
    lt = time.localtime()
    pt = "%s%s%s-%s:%s%s" % (lt.tm_year,lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,time.tzname[0])

    # For each node to be plotted
    for key in sorted(y_axis_dict.keys()):
      # Append a scatter plot for the specific node based on time and subtasks successes
      traces.append(go.Scatter(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      mode='lines',
      connectgaps=False,
      name=key
      ))
    
    layout = dict(title = 'Golem Network Successful Subtask Computations by Node as of ' + pt,
              xaxis = dict(title = 'Time'),
              yaxis = dict(title = 'Successful Subtask Computations on Golem Network'),
              )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filename, auto_open=False)
    return filename

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

    # Eliminate null values in the timestamp column
    ts_index = header.index('timestamp')
    try:
      nr[ts_index] = int(row[ts_index])
    except IndexError:
      nr[ts_index] = 0
    # Eliminate null values in subtasks_success column
    ss_index = header.index('subtasks_success')
    try:
      nr[ss_index] = float(row[ss_index])
    except IndexError:
      nr[ss_index] = 0
    return nr

  def load_new_data(self):
    all_data = {
      'data':[],
      'header':[]
    }
    for filename in [x for x in os.listdir('node_logs/') if x.find('network') != -1 or x.find('old_logs.log') != -1]:
      try:
        with open('node_logs/'+filename,'rt') as f:
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
            else:
              all_data['data'].append(self.clean_data_row(all_data['header'],row))
      except:
        print("Error in load_new_data - for %s in network.log files" % (filename))
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
    from os import remove
    from shutil import move

    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:126])+''.join(r[127:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp', 'node_logs/'+filename)

  def last_fix_maybe(self,filenames):
    from os import remove
    from shutil import move

    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:122])+filename[:-4]+''.join(r[132:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp','node_logs/'+filename)

  def fix_files(self,filenames):
    from os import remove
    from shutil import move

    for filename in filenames:
      with open('node_logs/'+filename,'rt') as f:
        r = f.read()
        with open('node_logs/'+filename+'.tmp','w') as f2:
          f2.write(''.join(r[:121])+"\n"+''.join(r[122:]))
      remove('node_logs/'+filename)
      move('node_logs/'+filename+'.tmp', 'node_logs/'+filename)
