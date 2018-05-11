import csv, os, time, sys, plotly, traceback, codecs
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
from math import isnan
import load_data as ld


class Analyze_Data:

  def __init__(self, v_ld=None):
    if v_ld is not None:
      self._ld = v_ld
      self._d = self._ld.get_data()
    else:
      self._ld = ld.Load_Data()
      self._d = self._ld.get_data()
    
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
    d = self.load_data()
    jf = self.build_json_data_object(d)
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
    max_timestamp = max(sorted(list(set([x[self._ld._ts_index] for x in d['data']]))))
    nodes_and_success_dict = self.get_distinct_successes_dict(d)
    all_max_success = self.get_max_successes(d)
    my_dict = {
      'nodes' : self.get_nodes_list(d,max_timestamp,nodes_and_success_dict,all_max_success),
      'links' : self.get_links_list(d,max_timestamp,nodes_and_success_dict,all_max_success)
    }
    return my_dict

  def get_target(self,targets,key):
    sl = sorted([(x,y) for x,y in targets.items() if y > 0])
    r = randint(1,len(sl))
    return r-1
  
  def get_pretty_time(self):
    lt = time.localtime()
    return time.strftime("%Y%m%d-%H:%M %Z",lt)
  
  def get_links_list(self,d,max_timestamp,nodes_and_success_dict,all_max_success):
    list_of_links = []
    for key in nodes_and_success_dict.keys():
      r = randint(0,2)
      for i in range(r):
        list_of_links.append({"source":list(nodes_and_success_dict.keys()).index(key),"target":self.get_target(nodes_and_success_dict,key)})
    return list_of_links

  def get_nodes_list(self,d,max_timestamp,nodes_and_success_dict,all_max_success):
    import numpy as np
    sl = [x for x in nodes_and_success_dict.values()]
    avg = np.mean(sl)
    node_list = []
    for record in d['data']:
      name = self.get_node_name(record)
      if name not in [x['name'] for x in node_list]:
        node_dict = {
            'name':self.get_node_name(record),
            'group':self.get_node_group(record,d,avg,nodes_and_success_dict[name])
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
      name = self.get_node_name(d['header'],record)
      if dist_nodes.get(name) is None:
        dist_nodes[name] = self.get_max_success_for_node(record,d)
    return dist_nodes

  def get_max_success_for_node(seflf,node,d):
    return max([x[self._ld._ss_index] for x in d['data'] if x[self._ld._id_index] == node[self._ld._id_index]])

  def get_max_successes(self,d):
    return max([x[3] for x in d['data']])

  def get_node_name(self,header,node):
    name = str(node[self._ld._nn_index])+"("+node[self._ld._id_index][:10]+")"
    return name

  def build_y_axis_dict_for_network_summary(self,x_axis):
    y_axis_dict = {
        'Node Count':[],
        # 'Performance General':[],
        # 'Performance Blender':[],
        # 'Performance LuxRender':[],
        'Allowed Resource Size':[],
        'Allowed Resource Memory':[],
        'CPU Cores':[]
    }
    key_names = [x for x in y_axis_dict.keys()]

    for timestamp in x_axis:
      connected_nodes = [x for x in self._d['data'] if x[self._ld._ts_index] == timestamp]
      formatted_ts = self.get_formatted_time(timestamp)

      node_count = len(connected_nodes)
      y_axis_dict[key_names[0]].append([formatted_ts,node_count])

      # summary_perf_gen = sum([float(x[self._ld._pg_index]) for x in connected_nodes])
      # y_axis_dict[key_names[1]].append([formatted_ts,summary_perf_gen])
      #
      # summary_perf_blend = sum([float(x[self._ld._pb_index]) for x in connected_nodes])
      # y_axis_dict[key_names[2]].append([formatted_ts,summary_perf_blend])
      #
      # summary_perf_lux = sum([float(x[self._ld._pl_index]) for x in connected_nodes])
      # y_axis_dict[key_names[3]].append([formatted_ts,summary_perf_lux])

      summary_allowed_resources = sum([int(x[self._ld._ars_index]) for x in connected_nodes if x[self._ld._ars_index] != ''])
      y_axis_dict[key_names[1]].append([formatted_ts,summary_allowed_resources])

      summary_allowed_memory = sum([int(x[self._ld._arm_index]) for x in connected_nodes if x[self._ld._arm_index] != ''])
      y_axis_dict[key_names[2]].append([formatted_ts,summary_allowed_memory])

      summary_cpu_cores = sum([int(x[self._ld._cc_index]) for x in connected_nodes if x[self._ld._cc_index] != ''])
      y_axis_dict[key_names[3]].append([formatted_ts,summary_cpu_cores])
    return y_axis_dict

  def build_y_axis_dict_for_new_unique_over_last_days(self,x_axis):
    y_axis_dict = {
      'Unique Node Count':[]
    }

    key_names = [x for x in y_axis_dict.keys()]

    for timestamp in x_axis:
      fts = self.get_formatted_time(timestamp)
      distinct_ids_before_ts = list(set([x[self._ld._id_index] for x in self._d['data'] if x[self._ld._ts_index] < timestamp]))
      new_nodes_this_ts = [x for x in self._d['data'] if x[self._ld._ts_index] == timestamp and x[self._ld._id_index] not in distinct_ids_before_ts]
      cnt_distinct_ts_for_new_nodes = len(list(set([x[self._ld._ts_index] for x in new_nodes_this_ts])))
      if cnt_distinct_ts_for_new_nodes:
        avg_new_for_ts = len(new_nodes_this_ts) / cnt_distinct_ts_for_new_nodes
        # The first timestamp will have every node being counted, we don't want to include that value in the chart. 
        if avg_new_for_ts < 500:
          y_axis_dict[key_names[0]].append([fts,avg_new_for_ts])

    return y_axis_dict

  def build_x_axis(self,log_cutoff_date=dt(2017,1,1)):
    x_axis = sorted(list(set([x[self._ld._ts_index] for x in self._d['data'] if dt.fromtimestamp(x[self._ld._ts_index]) > log_cutoff_date])))
    return x_axis

  def print_new_unique_over_last_days_graph(self,days_since_cutoff):
    print("Starting print_new_unique_over_last_days_graph - " + self.get_pretty_time())
    filename = 'new_unique_node_count_per_snapshot.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=days_since_cutoff)

    x_axis = self.build_x_axis(log_cutoff_date)
    y_axis_dict = self.build_y_axis_dict_for_new_unique_over_last_days(x_axis)
    traces = []

    for key in y_axis_dict.keys():
      traces.append(go.Bar(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      name=key
      ))

    layout = go.Layout(
        title='New Unique Nodes per Snapshot',
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename

  def print_avg_daily_subtask_totals(self,num_days_included):
    print("Starting print_avg_daily_subtask_totals - " + self.get_pretty_time())
    filename = 'avg_daily_subtasks_totals.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=num_days_included)

    y_axis_dict = self.get_avg_daily_subtask_totals(log_cutoff_date)
    traces = []
    
    for key in y_axis_dict.keys():
      traces.append(go.Bar(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      name=key
      ))

    layout = go.Layout(
        title='Average Daily Subtask Totals',
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename
    
  def print_avg_daily_failed_totals(self,num_days_included):
    print("Starting print_avg_daily_failed_totals - " + self.get_pretty_time())
    filename = 'avg_daily_failed_totals.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=num_days_included)
  
    y_axis_dict = self.get_avg_daily_failed_totals(log_cutoff_date)
    traces = []
    
    for key in y_axis_dict.keys():
      traces.append(go.Bar(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      name=key
      ))
    
    layout = go.Layout(
        title='Average Daily Failed Totals',
        xaxis=dict(
          tickfont=dict(
              size=14,
              color='rgb(107, 107, 107)'
          )
        ),
        yaxis=dict(
          title='',
          titlefont=dict(
              size=16,
              color='rgb(107, 107, 107)'
          ),
          tickfont=dict(
              size=14,
              color='rgb(107, 107, 107)'
          )
        ),
        legend=dict(
          x=0,
          y=1.0,
          bgcolor='rgba(255, 255, 255, 0)',
          bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
  
    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename
  
  def print_avg_daily_unique_node_totals(self,num_days_included):
    print("Starting print_avg_daily_unique_node_totals - " + self.get_pretty_time())
    filename = 'avg_daily_unique_totals.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=num_days_included)

    y_axis_dict = self.get_avg_daily_unique_node_totals(log_cutoff_date)
    traces = []
    
    for key in y_axis_dict.keys():
      traces.append(go.Bar(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      name=key
      ))

    layout = go.Layout(
        title='Average Daily Unique Node Totals',
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename

  def print_network_summary_over_time_graph(self,days_since_cutoff):
    print("Starting print_network_summary_over_time_graph - " + self.get_pretty_time())
    filename = 'golem-network.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=days_since_cutoff)

    x_axis = self.build_x_axis(log_cutoff_date)
    y_axis_dict = self.build_y_axis_dict_for_network_summary(x_axis)
    traces = []
    
    for key in y_axis_dict.keys():
      traces.append(go.Scatter(
      x = [x[0] for x in y_axis_dict[key]],
      y = [x[1] for x in y_axis_dict[key]],
      mode='lines',
      connectgaps=False,
      name=key
      ))

    fig = tools.make_subplots(rows=5, cols=1, specs=[[{}], [{}], [{}], [{}], [{}]],
                              shared_xaxes=True, shared_yaxes=True,
                              vertical_spacing=0.00001)

    fig.append_trace(traces[0], 5, 1) # Node_Count
    fig.append_trace(traces[3], 4, 1) # CPU_Cores
    fig.append_trace(traces[2], 3, 1) # Resource Memory
    fig.append_trace(traces[1], 2, 1) # Resource Size

    fig['layout'].update(title='Golem Network Resources Summary',
        xaxis = dict(title = 'Time'),
        yaxis = dict(title = 'Summarization Metric'))

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename

  def print_avg_daily_nodes_connected(self,num_days_included):
    print("Starting print_avg_daily_nodes_connected - " + self.get_pretty_time())
    filename = 'daily_avg_nodes_connected_'+str(num_days_included)+'_days.html'
    filepath = 'build_graphs/'+filename
    log_cutoff_date = dt.today() - timedelta(days=num_days_included)

    traces = []
    plot_pairs = []
    list_of_dates = sorted(self.get_list_of_dates_for_data(log_cutoff_date))
    for d in list_of_dates:
      plot_pairs.append([d,self.get_avg_nodes_connected_on_date(d)])

    traces.append(go.Bar(
    x = [x[0] for x in plot_pairs],
    y = [x[1] for x in plot_pairs],
    name='Avg Nodes Connected'
    ))

    layout = go.Layout(
        title='Daily Average Nodes Connected',
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )

    data = traces
    fig = dict(data=data,layout=layout)

    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
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

  def get_list_of_dates_for_data(self, cutoff_date):
    return list(set([self.get_date_from_timestamp(x[self._ld._ts_index]) for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) > dt.date(cutoff_date)]))

  def get_avg_nodes_connected_on_date(self, td):
    all_nodes_logged_on_date = [x for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == td]
    all_timestamps_logged_on_date = list(set([x[self._ld._ts_index] for x in all_nodes_logged_on_date]))
    return len(all_nodes_logged_on_date) / len(all_timestamps_logged_on_date)

  def get_avg_new_unique_node_count_on_date(self, td):
    distinct_node_ids_logged_on_date = list(set([x[self._ld._id_index] for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == td]))
    distinct_timestamps_on_date = list(set([x[self._ld._ts_index] for x in [x for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == td]]))
    distinct_node_ids_logged_before_date = list(set([x[self._ld._id_index] for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) < td]))
    new_unique_nodes_on_date = [x for x in distinct_node_ids_logged_on_date if x not in distinct_node_ids_logged_before_date]
    return len(new_unique_nodes_on_date)/len(distinct_timestamps_on_date)

  def get_float_value(self, f):
    try:
      x = float(f)
      if not isnan(x):
        return x
    except ValueError:
      return 0
    return 0

  def get_avg_requested_subtasks_on_date(self, lnod, dtod):
    total_count_requested_subtasks = sum([self.get_float_value(x[self._ld._rs_rs_index]) for x in lnod])
    return total_count_requested_subtasks / len(dtod)

  def get_avg_subtasks_completed_on_date(self, lnod, dtod):
    total_count_subtasks_success = sum([self.get_float_value(x[self._ld._ss_index]) for x in lnod])
    return total_count_subtasks_success / len(dtod)
    
  def get_avg_collected_results_on_date(self, lnod, dtod):
    tccr = sum([self.get_float_value(x[self._ld._rs_cr_index]) for x in lnod])
    return tccr / len(dtod)
      
  def get_avg_failed_on_date(self, lnod, dtod):
    tfod = sum([self.get_float_value(x[self._ld._rs_fc_index]) for x in lnod])
    return tfod / len(dtod)

  def get_avg_failed_subtasks_on_date(self, lnod, dtod):
    tfsd = sum([self.get_float_value(x[self._ld._rs_fs_index]) for x in lnod])
    return tfsd / len(dtod)

  def get_avg_finished_task_on_date(self, lnod, dtod):
    tftd = sum([self.get_float_value(x[self._ld._rs_ft_index]) for x in lnod])
    return tftd / len(dtod)
      
  def get_avg_finished_with_fail_on_date(self, lnod, dtod):
    tffd = sum([self.get_float_value(x[self._ld._rs_ff_index]) for x in lnod])
    return tffd / len(dtod)
    
  def get_avg_not_downloadable_subtasks_on_date(self, lnod, dtod):
    tndd = sum([self.get_float_value(x[self._ld._rs_nd_index]) for x in lnod])
    return tndd / len(dtod)

  def get_avg_tasks_on_date(self, lnod, dtod):
    ttd = sum([self.get_float_value(x[self._ld._rs_tc_index]) for x in lnod])
    return ttd / len(dtod)
      
  def get_date_from_timestamp(self, d1):
    return dt.date(dt.fromtimestamp(d1))

  def get_avg_daily_unique_node_totals(self,cutoff_date):
    dailytot = {
      'New Unique':[]
    }
    
    list_of_dates = sorted(self.get_list_of_dates_for_data(cutoff_date))
    for d in list_of_dates:
      lnod = [x for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == d]
      if lnod:
        dtod = list(set([x[self._ld._ts_index] for x in lnod]))
        
      if list_of_dates.index(d) > 0:
        dailytot['New Unique'].append([d,self.get_avg_new_unique_node_count_on_date(d)])
      
    return dailytot

  def get_avg_daily_subtask_totals(self,cutoff_date):
    dailytot = {
      'Requested Subtasks':[],
      'Subtasks Completed':[]
      # 'Collected Results':[]
      # 'Finished Task':[],
      # 'Tasks':[],
      # 'Verified Results':[],
      # 'Subtasks':[],
      # 'Tasks Requested':[],
    }

    list_of_dates = sorted(self.get_list_of_dates_for_data(cutoff_date))
    for d in list_of_dates:
      lnod = [x for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == d]
      if lnod:
        dtod = list(set([x[self._ld._ts_index] for x in lnod]))
        
      dailytot['Requested Subtasks'].append([d,self.get_avg_requested_subtasks_on_date(lnod,dtod)])
      dailytot['Subtasks Completed'].append([d,self.get_avg_subtasks_completed_on_date(lnod,dtod)])
      # dailytot['Collected Results'].append([d,self.get_avg_collected_results_on_date(lnod,dtod)])
      # dailytot['Finished Task'].append([d,self.get_avg_finished_task_on_date(lnod,dtod)])
      # dailytot['Tasks'].append([d,self.get_avg_tasks_on_date(lnod,dtod)])

    return dailytot

  def get_avg_daily_failed_totals(self,cutoff_date):
    dailytot = {
      # 'Collected Results':[]
      # 'Finished Task':[],
      # 'Tasks':[],
      # 'Verified Results':[],
      # 'Subtasks':[],
      # 'Tasks Requested':[],
      'Failed':[],
      'Failed Subtasks':[],
      'Finished With Failures':[],
      'Not Downloadable Subtasks':[],
      'Timed Out Subtasks':[],
      'Tasks Error':[],
      'Tasks Timeout':[]
    }

    list_of_dates = sorted(self.get_list_of_dates_for_data(cutoff_date))
    for d in list_of_dates:
      lnod = [x for x in self._d['data'] if self.get_date_from_timestamp(x[self._ld._ts_index]) == d]
      if lnod:
        dtod = list(set([x[self._ld._ts_index] for x in lnod]))
        
      dailytot['Failed'].append([d,self.get_avg_failed_on_date(lnod,dtod)])
      dailytot['Failed Subtasks'].append([d,self.get_avg_failed_subtasks_on_date(lnod,dtod)])
      dailytot['Finished With Failures'].append([d,self.get_avg_finished_with_fail_on_date(lnod,dtod)])
      dailytot['Not Downloadable Subtasks'].append([d,self.get_avg_not_downloadable_subtasks_on_date(lnod,dtod)])
      

    return dailytot
