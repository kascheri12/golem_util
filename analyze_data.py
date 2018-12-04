import csv, os, time, sys, plotly, traceback, codecs, db, math
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
import load_data as ld


class Analyze_Data:

  def __init__(self,env):
    self.conn = db.DB(env)

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

  def print_golem_network_dashboard_page(self):
    print("Starting print_golem_network_dashboard_page : " + self.get_pretty_time())
    filename = 'Golem-Network-Dashboard.md'
    filepath = 'build_graphs/'+filename
    
    mdf_content = self.build_dashboard_file_content()
    
    mdf = open(filepath,'w')
    mdf.write(mdf_content)
    mdf.close()
    return filename
  
  def print_all_nodes_latest_snapshot(self):
    print("Starting print_all_nodes_latest_snapshot : " + self.get_pretty_time())
    filename = 'All-Nodes-Latest-Snapshot.md'
    filepath = 'build_graphs/'+filename
    
    mdf_content = self.build_all_nodes_latest_snapshot_file_content()
    
    mdf = open(filepath,'w')
    mdf.write(mdf_content)
    mdf.close()
    return filename
    
  def build_all_nodes_latest_snapshot_file_content(self):
    base_md_string = self.return_base_md_page_string()
    return base_md_string.format(title='All Nodes Latest Snapshot',datatables=self.build_markup_for_all_nodes_latest_snapshot_tabledata())
    
  def build_dashboard_file_content(self):
    old_dashboard_string = self.return_old_golem_network_dashboard_markup()
    qr = self.query_subtasks_success_change_past_date_limit(1)[1][0]
    dashboard_file_content = old_dashboard_string.format( \
      datatables=self.build_markup_for_all_network_tabledata() \
      ,gauge_percent_change_subtasks_success_past_day_value = qr[2] \
      ,gauge_percent_change_subtasks_timeout_past_day_value = qr[4] \
      ,gauge_percent_change_subtasks_error_past_day_value = qr[6])
    return dashboard_file_content
  
  def build_markup_for_all_nodes_latest_snapshot_tabledata(self):
    return self.build_html_markup_for_all_nodes()
    
  def build_markup_for_all_network_tabledata(self):
    rv_html = ""
    table_categories = ['subtasks_success'
        ,'subtasks_error','subtasks_timeout'
        ,'tasks_requested','rs_tasks_cnt'
        ,'rs_finished_task_cnt','rs_requested_subtasks_cnt'
        ,'rs_collected_results_cnt','rs_verified_results_cnt'
        ,'rs_timed_out_subtasks_cnt','rs_not_downloadable_subtasks_cnt'
        ,'rs_failed_subtasks_cnt','rs_work_offers_cnt'
        ,'rs_finished_ok_cnt'
        ,'rs_finished_with_failures_cnt'
        ,'rs_failed_cnt','cpu_cores']
    rv_html += self.build_html_markup_for_perc_change()
    for category in table_categories:
      rv_html += self.build_html_markup_for_table_category(category)
    return rv_html

  def build_html_markup_for_all_nodes(self):
    rv_html = """
<div class='col-xs-12 col-lg-12' style='margin-top:10px;background-color:floralwhite;'>
  <h3>All nodes latest snapshot</h3>
  <table class='all_nodes_dt table compact display nowrap table-bordered table-sm' width='100%'>
    <thead>
      {thead}
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
</div>
"""

  def build_html_markup_for_perc_change(self):
    rv_html = """
<div class='col-xs-12 col-sm-12 col-lg-12 col-xl-12' style='padding:10px;'>
  <h4>Percent change of total subtasks success by day</h4>
  <table id='perc-change-subtasks-success' class='table display nowrap table-bordered table-sm' width='100%'>
    <thead>
      {thead}
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
</div>
"""
    qr = self.query_subtasks_success_change_past_date_limit(20)
    header_table_markup = self.build_thead_from_results(qr[0])
    body_table_markup = self.build_tbody_from_results(qr[1])
    return rv_html.format(thead=header_table_markup,tbody=body_table_markup)
    
  def build_html_markup_for_table_category(self,category):
    rv_html = """
<div class='col-xs-12 col-lg-6 col-xl-4' style='padding:10px;'>
  <h5>Top {} {}</h5>
  <table class='top_dt table display nowrap table-bordered table-sm' width='100%'>
    <thead>
      {}
    </thead>
    <tbody>
      {}
    </tbody>
  </table>
</div>
"""
    query_res = self.query_top_results_category(50,category)
    header_table_markup = self.build_thead_from_results(query_res[0])
    body_table_markup = self.build_tbody_from_results(query_res[1])
    if category == 'subtasks_success':
      return rv_html.format(50,'Subtasks Success',header_table_markup,body_table_markup)
    elif category == 'rs_tasks_cnt':
      return rv_html.format(50,'RS Tasks Count',header_table_markup,body_table_markup)
    elif category == 'rs_finished_task_cnt':
      return rv_html.format(50,'RS Finished Task Count',header_table_markup,body_table_markup)
    elif category == 'rs_finished_ok_cnt':
      return rv_html.format(50,'RS Finished Ok Count',header_table_markup,body_table_markup)
    elif category == 'subtasks_error':
      return rv_html.format(50,'Subtasks Error',header_table_markup,body_table_markup)
    elif category == 'subtasks_timeout':
      return rv_html.format(50,'Subtasks Timeout',header_table_markup,body_table_markup)
    elif category == 'cpu_cores':
      return rv_html.format(50,'CPU Core Count',header_table_markup,body_table_markup)
    return ""
  
  def build_thead_from_results(self, header_list):
    rv_markup = ""
    for item in header_list:
      rv_markup += "<th scope='col'>{}</th>".format(item)
    return "<tr>{}</tr>".format(rv_markup)

  def build_tbody_from_results(self, data_rows):
    rv_markup = ""
    is_first_column = True
    tr_html = "<tr>{}</tr>"
    for row in data_rows:
      item_row = ""
      for item in row:
        if is_first_column:
          is_first_column = False
          item_row += format("<td scope='row'>{}</td>".format(item))
        else:
          item_row += format("<td>{}</td>".format(item))
      rv_markup += tr_html.format(item_row)
    return rv_markup

  def query_all_nodes_latest_snapshot(self):
    query_all_nodes_last_seen_state = """
    select substr(n1.node_id,1,10) short_node_id
            ,n2.snapshot_date
            ,n2.node_name
            ,n2.node_version
            ,n2.last_seen
            ,n2.os
            ,n2.os_system
            ,n2.os_release
            ,n2.os_version
            ,n2.os_windows_edition
            ,n2.os_linux_distribution
            ,n2.ip
            ,n2.start_port
            ,n2.end_port
            ,n2.performance_general
            ,n2.performance_blender
            ,n2.performance_lux
            ,n2.allowed_resource_size
            ,n2.allowed_resource_memory
            ,n2.cpu_cores
            ,n2.min_price
            ,n2.max_price
            ,n2.subtasks_success
            ,n2.subtasks_error
            ,n2.subtasks_timeout
            ,n2.p2p_protocol_version
            ,n2.task_protocol_version
            ,n2.tasks_requested
            ,n2.known_tasks
            ,n2.supported_tasks
            ,n2.rs_tasks_cnt
            ,n2.rs_finished_task_cnt
            ,n2.rs_requested_subtasks_cnt
            ,n2.rs_collected_results_cnt
            ,n2.rs_verified_results_cnt
            ,n2.rs_timed_out_subtasks_cnt
            ,n2.rs_not_downloadable_subtasks_cnt
            ,n2.rs_failed_subtasks_cnt
            ,n2.rs_work_offers_cnt
            ,n2.rs_finished_ok_cnt
            ,n2.rs_finished_ok_total_time
            ,n2.rs_finished_with_failures_cnt
            ,n2.rs_finished_with_failures_total_time
            ,n2.rs_failed_cnt
            ,n2.rs_failed_total_time
    from (
      select node_id,
        max(snapshot_date) snapshot_date
      from network_01
      group by node_id) n1
    INNER JOIN network_01 n2
        ON n2.node_id = n1.node_id
        and n2.snapshot_date = n1.snapshot_date;
    """
    self.conn.query(query_all_nodes_last_seen_state)
    return (self.conn.fetchfields(),self.conn.fetchall())
    

  def query_top_results_category(self,num_of_res,category):
    query = """
select n1.mss {}
        , n2.node_name
        , substr(n1.node_id,1,10) short_node_id
        , n2.snapshot_date
        , n2.cpu_cores
        , n2.allowed_resource_size
        , n2.allowed_resource_memory
from (
  select node_id,
    max(snapshot_date) snapshot_date,
    max({}) mss
  from network_01
  group by node_id
  order by mss desc
  LIMIT {}) n1
inner join network_01 n2
  on n2.node_id = n1.node_id
  and n2.snapshot_date = n1.snapshot_date
order by n1.mss desc, n1.snapshot_date asc;
"""
    self.conn.query(query.format(category,category,num_of_res))
    return (self.conn.fetchfields(),self.conn.fetchall())
    
  def return_old_golem_network_dashboard_markup(self):
    rv = """---
title: Dashboard
---

# Golem Network Dashboard

<br />

#### Percentage change in subtasks success past day

<details>
<summary><strong>Details</strong></summary>

  <p>This value represents the percentage change of the sum of subtasks_success of active nodes in the latest snapshot and the same metric from yesterday's last snapshot.</p>

  <h5>Analysis</h5>

  <p>There are many reasons for drastic movement here even if the same extreme movement is not reflected in the node count.</p>

  <p>A single node with a large number of subtasks_success might exit the network for a time and this would demonstrate a dtrasitc decrease in this metric but the overall node count would not change so drastically.</p>
</details>

<br />

<div class="row">
  <div class='col-xs-12 col-lg-4'>
    <div id='preview' style='position:relative;float:left;display:block;'>
      <canvas style='position:relative;display:inline-block;' id='gauge_percent_change_subtasks_success_past_day'></canvas>
      <span style='position:absolute;text-align:center;left:0;right:0;bottom:0;' id='snap_gauge_percent_change_subtasks_success_past_day'></span>
    </div>
  </div>
  <div class='col-xs-12 col-lg-4'>
    <div id='preview' style='position:relative;float:left;display:block;'>
      <canvas style='position:relative;display:inline-block;' id='gauge_percent_change_subtasks_timeout_past_day'></canvas>
      <span style='position:absolute;text-align:center;left:0;right:0;bottom:0;' id='snap_gauge_percent_change_subtasks_timeout_past_day'></span>
    </div>
  </div>
  <div class='col-xs-12 col-lg-4'>
    <div id='preview' style='position:relative;float:left;display:block;'>
      <canvas style='position:relative;display:inline-block;' id='gauge_percent_change_subtasks_error_past_day'></canvas>
      <span style='position:absolute;text-align:center;left:0;right:0;bottom:0;' id='snap_gauge_percent_change_subtasks_error_past_day'></span>
    </div>
  </div>
</div>


<script>
  $(document).ready(function() {{
    init_gauge('gauge_percent_change_subtasks_success_past_day',{gauge_percent_change_subtasks_success_past_day_value});
    init_gauge('gauge_percent_change_subtasks_timeout_past_day',{gauge_percent_change_subtasks_timeout_past_day_value});
    init_gauge('gauge_percent_change_subtasks_error_past_day',{gauge_percent_change_subtasks_error_past_day_value});
  }});
  
</script>

<br />

[comment]: <> (Inject of data tables)
<div class='row'>
{datatables}
</div>

<br /><br />
### [All Nodes by Latest Snapshop](All-Nodes-Latest-Snapshot)

<br /><br />
<div id="Count-of-distinct-nodes-connected-by-date"></div>

### Count of distinct nodes connected by date

<details>
<summary><strong>Details</strong></summary>

<p>This one is pretty straight-forward. Snapshots only include active nodes, inactive node data is not being collected during a snapshot.</p>

<p>
Pseudo code:
<ul>
  <li>[get_avg_nodes_connected_on_date(date)](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L625)</li>
  <ul>
    <li>Find all_dist_timestamps_logged_on_date from all_nodes_logged_on_date</li>
    <li>return len(all_nodes_logged_on_date) / len(all_timestamps_logged_on_date)</li>
  </ul>
</ul>
</p>
</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/nodes_connected_by_date.html"></iframe>

<br /><br />
<div id="Count-of-distinct-nodes-connected-by-date"></div>

### Top 50 successful subtasks past 90 days

<details>
<summary><strong>Details</strong></summary>

<p>This graph is of the top 50 highest successful subtask counts, inspecting each nodes' value over the past ninety days.</p>

</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/top_50_subtasks_success_by_date.html"></iframe>

<details>
<summary>Show other graphs</summary>

<div id="Golem-Network-Summary"></div>

### Golem Network Summary

<details>
<summary><strong>Details</strong></summary>

<p>This is a summary of some standard resources along with a basic active node count. The three values for CPU Cores, Allowed Resource Memory, and Allowed Resource Size are found based on summing the corresponding values of the active nodes in a snapshot and dividing each by the number of snapshots.</p>

</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/golem-network.html"></iframe>


<div id="Average-Daily-Subtasks-Totals"></div>

### Average Daily Subtask Totals

<details>
<summary><strong>Details</strong></summary>

<p>This is a summary of some standard resources along with a basic active node count. The three values for CPU Cores, Allowed Resource Memory, and Allowed Resource Size are found based on summing the corresponding values of the active nodes in a snapshot and dividing each by the number of snapshots.</p>

<p>This one shows the average values per day of snapshots of new unique nodes, subtasks requested, and subtasks computed on the date. Many nodes can come and go throughout the day so I thought that an average amongst the snapshots collected per day would work as a standard daily metric for these graphs.</p>

<p>The function that builds these values is [get_avg_daily_subtask_totals()](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L701).</p>
<p>
Here's pseudo code for the functions:
<ul>
  <li>[get_avg_requested_subtasks_on_date(list_nodes_on_date,distinct_timestamps_on_date)](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L646)</li>
  <ul>
    <li>total_count_requested_subtasks = sum( requested_subtasks ) in list_nodes_on_date</li>
    <li>return total_count_requested_subtasks / len(distinct_timestamp_on_date)</li>
  </ul>
  <li>[get_avg_subtasks_completed_on_date(list_nodes_on_date,distinct_timestamps_on_date)](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L650)</li>
  <ul>
    <li>total_count_requested_subtasks = sum( requested_subtasks ) in list_nodes_on_date</li>
    <li>return total_count_subtasks_success / len(distinct_timestamps_on_date)</li>
  </ul>
</ul>
</p>

<p>The reason that the average total completed subtasks on a given date is greater than the average requested subtasks is because this is only a snapshot in time of the nodes that are connected. A node that has completed subtasks for another might still be connected to the network while the requested has since left the network thereby removing that count from future snapshots while it is disconnected.</p>

</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/avg_daily_subtasks_totals.html"></iframe>


<div id="Average-Daily-Failed-Totals"></div>

### Average Daily Failed Totals
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/avg_daily_failed_totals.html"></iframe>

<div id="Average-New-Unique-Node-Count-per-Day"></div>

### Average New Unique Node Count per Day

<details>
<summary><strong>Details</strong></summary>

<p>Node ID's collected and referenced below are only ones collected in the time that I've been collecting data.</p>

<p>
Pseudo code:
<ul>
  <li>[get_avg_new_unique_node_count_on_date(date)](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L630)</li>
  <ul>
    <li>Gather lists of distinct_node_ids_logged_on_date, distinct_timestamps_on_date, and distinct_node_ids_logged_before_date</li>
    <li>Get new_unique_nodes_on_date from distinct_node_ids_logged_on_date that are not in distinct_node_ids_logged_before_date</li>
    <li>return len(new_unique_nodes_on_date)/len(distinct_timestamps_on_date)</li>
  </ul>
</ul>
</p>
</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/avg_daily_unique_totals.html"></iframe>


<div id="New-Unique-Node-Count-per-Snapshot"></div>

### New Unique Node Count per Snapshot

<details>
<summary><strong>Details</strong></summary>

<p>This one takes the longest to build because of the iterative nature of continuing to compare a growing list of values in the past that are not newly unique nodes anymore.</p>
<p>
Pseudo code:
<ul>
  <li>[build_y_axis_dict_for_new_unique_over_last_days(x_axis)](https://github.com/kascheri12/golem_util/blob/4b40695b16f120776a49613bf94678f732ef2b93/analyze_data.py#L258)</li>
  <ul>
    <li>Iterate throughout each timestamp on the x_axis</li>
    <ul>
      <li>Find distinct_ids_before_ts</li>
      <li>Then find new_nodes_this_ts from all_nodes_this_ts not in distinct_id_before_ts</li>
      <li>Find cnt_distinct_ts_for_new_nodes</li>
      <li>avg_new_for_ts = len(new_nodes_this_ts) / cnt_distinct_ts_for_new_nodes</li>
    </ul>
  </ul>
</ul>
</p>
</details>
<br />
<iframe style="width:100%;height:600px" src="https://kascheri12.github.io/graphs/new_unique_node_count_per_snapshot.html"></iframe>

</details>
"""
    return rv


  def return_base_md_page_string(self):
    rv = """---
title: {title}
---

# {title}

<br /><br />

[comment]: <> (Inject of data tables)
<div class='row'>
{datatables}
</div>

<br /><br />
"""
    return rv

  def query_subtasks_success_change_past_date_limit(self,limit_num):
    query_percentage_increase = """
    select 
        date(n2.snapshot_date) snapshot_date
        , sum(n2.subtasks_success) sum_subtasks_success
        , ((sum(n2.subtasks_success) / a.sss) - 1) * 100 percent_increase_prev_day_subtask_success
        , sum(n2.subtasks_error) sum_subtasks_error
        , ((sum(n2.subtasks_error) / a.sse) - 1) * 100 percent_increase_prev_day_subtask_error
        , sum(n2.subtasks_timeout) sum_subtasks_timeout
        , ((sum(n2.subtasks_timeout) / a.sst) - 1) * 100 percent_increase_prev_day_subtask_timeout
    from (
      select date(snapshot_date),
              max(snapshot_date) msd
      from network_01
      group by date(snapshot_date)) n1
    inner join network_01 n2
      on n2.snapshot_date = n1.msd
    LEFT join (select sum(n2.subtasks_success) sss
                    , sum(n2.subtasks_error) sse
                    , sum(n2.subtasks_timeout) sst
                    , date(n2.snapshot_date) sd
                from (
                  select date(snapshot_date),
                          max(snapshot_date) msd
                  from network_01
                  group by date(snapshot_date)) n1
                inner join network_01 n2
                  on n2.snapshot_date = n1.msd
                group by n2.snapshot_date, date(n2.snapshot_date)) a
      on a.sd = date(n2.snapshot_date) - INTERVAL 1 DAY
    group by n2.snapshot_date, date(n2.snapshot_date), a.sss, a.sse, a.sst
    order by date(n2.snapshot_date) desc
    LIMIT {limit_num};
    """
    self.conn.query(query_percentage_increase.format(limit_num=limit_num))
    return (self.conn.fetchfields(),self.conn.fetchall())
    
  def print_meter_subtasks_success_change_past_day(self):
    print("Starting print_meter_subtasks_success_change_past_day - " + self.get_pretty_time())
    filename = 'meter_subtasks_success_change_past_day.html'
    filepath = 'build_graphs/'+filename

    qr = self.query_subtasks_success_change_past_date_limit(1)
    percentage = float(qr[1][0][2])
    
    base_chart = {
        "values": [40, 10, 10, 10, 10, 10, 10],
        "domain": {"x": [0, .48]},
        "marker": {
            "colors": [
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)'
            ],
            "line": {
                "width": 1
            }
        },
        "name": "Gauge Subtasks Success change past day",
        "hole": .4,
        "type": "pie",
        "direction": "clockwise",
        "rotation": 108,
        "showlegend": False,
        "hoverinfo": "none",
        "textinfo": "none"
    }
    meter_chart = {
        "values": [50, 10, 10, 10, 10, 10],
        "labels": ["Percentage change sum of subtasks success", "Extreme Decrease", "Decrease", "Neutral", "Increase", "Extreme Increase"],
        "marker": {
            'colors': [
                'rgb(255, 255, 255)',
                'rgb(255,0,0)',
                'rgb(255,153,51)',
                'rgb(255,255,0)',
                'rgb(155,205,50)',
                'rgb(0,255,0)'
            ]
        },
        "domain": {"x": [0, 0.48]},
        "name": "Gauge",
        "hole": .4,
        "type": "pie",
        "direction": "clockwise",
        "rotation": 90,
        "showlegend": False,
        "textinfo": "label",
        "textposition": "inside",
        "hoverinfo": "none"
    }
    
    if percentage > 50:
      percentage = 50
    my_raw_value = 90 + (percentage * 1.8);
    degrees = 180 - my_raw_value
    radians = degrees * math.pi / 180;
    h = 0.24
    k = 0.5
    aX = h + h*(0.025 * math.cos((degrees-90) * math.pi / 180))
    aY = k + h*(0.025 * math.sin((degrees-90) * math.pi / 180))
    bX = h + h*(-0.025 * math.cos((degrees-90) * math.pi / 180))
    bY = k + h*(-0.025 * math.sin((degrees-90) * math.pi / 180))
    cX = h + h*(math.cos((radians)))
    cY = k + h*(math.sin((radians)))

    path = "M {} {} L {} {} L {} {} Z".format(aX,aY,bX,bY,cX,cY)

    layout = {
        'width': 1200,
        'height': 600,
        'xaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'shapes': [
            {
                'type': 'path',
                'path': path,
                'fillcolor': 'rgba(44, 160, 101, 0.5)',
                'line': {
                    'width': 0.5
                },
                'xref': 'paper',
                'yref': 'paper'
            }
        ],
        'annotations': [
            {
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.23,
                'y': 0.45,
                'text': str(percentage)+"%",
                'showarrow': False
            }
        ]
    }

    # we don't want the boundary now
    base_chart['marker']['line']['width'] = 0

    fig = {"data": [base_chart, meter_chart],
           "layout": layout}
    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename

  def print_avg_daily_subtasks_totals(self,num_days_included):
    print("Starting print_avg_daily_subtasks_totals - " + self.get_pretty_time())
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

  def print_top_50_subtasks_success_by_date(self,num_days_included):
    print("Starting top_50_subtasks_success_by_date - " + self.get_pretty_time())
    filename = 'top_50_subtasks_success_by_date.html'
    filepath = 'build_graphs/'+filename      
    query_top_50_subtasks_success_by_date = """
select max(n3.subtasks_success) subtasks_success
        , substr(n1.node_id,1,10) short_node_id
        , n2.node_name
        , date(n3.snapshot_date) snapshot_date
        , n1.node_id
from (
  select node_id,
    max(snapshot_date) snapshot_date,
    max(subtasks_success) mss
  from network_01
  group by node_id
  order by mss desc
  LIMIT 50) n1
inner join network_01 n2
  on n2.node_id = n1.node_id
  and n2.snapshot_date = n1.snapshot_date
inner join network_01 n3
  on n3.node_id = n1.node_id
  and n3.snapshot_date > (n1.snapshot_date - INTERVAL {interval} DAY)
group by n1.node_id, n2.node_name, date(n3.snapshot_date)
order by 4 desc,1;
"""
    self.conn.query(query_top_50_subtasks_success_by_date.format(interval=num_days_included))
    qr = self.conn.fetchall()
    dd = list(sorted(list(set([x[3] for x in qr]))))
    node_ids = list(set([x[4] for x in qr]))
    traces = []
    for node in node_ids:
      traces.append(go.Scatter(
        x = [dt.strftime(x,'%Y-%m-%d') for x in dd],
        y = list(sorted([x[0] for x in qr if x[4] == node])),
        name = list(set([x[2] for x in qr if x[4] == node]))[0]
      ))
    data = traces

    # Edit the layout
    layout = dict(title = 'Top 50 Subtasks Success By Date',
                  xaxis = dict(title = 'Date'),
                  yaxis = dict(title = 'Subtasks Success'),
                  )

    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename=filepath, auto_open=False)
    self.inject_google_analytics(filepath)
    return filename

  def print_nodes_connected_by_date(self,num_days_included):
    print("Starting print_nodes_connected_by_date - " + self.get_pretty_time())
    filename = 'nodes_connected_by_date.html'
    filepath = 'build_graphs/'+filename
    # log_cutoff_date = dt.today() - timedelta(days=num_days_included)

    query_daily_distinct_count = """
    select date(snapshot_date) snapshot_date
      , count(distinct node_id) distinct_cnt 
    from network_01
    where date(snapshot_date) > (date(snapshot_date) - INTERVAL {interval} DAY)
    group by date(snapshot_date);
    """
    self.conn.query(query_daily_distinct_count.format(interval=num_days_included))
    qr = self.conn.fetchall()
    
    traces = []
    traces.append(go.Bar(
    x = [x[0] for x in qr],
    y = [x[1] for x in qr],
    name='Distinct Nodes Connected by Date (Past {interval} days)'.format(interval=num_days_included)
    ))

    layout = go.Layout(
        title='Distinct Nodes Connected by Date (Past {interval} days)'.format(interval=num_days_included),
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Distinct count of nodes',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        bargap=0.15
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
      if not math.isnan(x):
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

  def scratch_sql(self):
    conn = db.DB()
    my_query = """
    select max(rs_finished_task_cnt) max_ts_finished_task_cnt
      , substr(node_id,1,10) node_id
      , node_name 
    from network_01 
    group by node_id, node_name 
    order by max(rs_finished_task_cnt) desc 
    limit 20;
    """
    query_percentage_increase = """
    select sum(n2.subtasks_success)
        , ((sum(n2.subtasks_success) / a.sss) - 1) * 100 percentage_increase_over_yesterday
        , date(n2.snapshot_date)
    from (
      select date(snapshot_date),
              max(snapshot_date) msd
      from network_01
      group by date(snapshot_date)) n1
    inner join network_01 n2
      on n2.snapshot_date = n1.msd
    LEFT join (select sum(n2.subtasks_success) sss
                    , date(n2.snapshot_date) sd
                from (
                  select date(snapshot_date),
                          max(snapshot_date) msd
                  from network_01
                  group by date(snapshot_date)) n1
                inner join network_01 n2
                  on n2.snapshot_date = n1.msd
                group by n2.snapshot_date, date(n2.snapshot_date)) a
      on a.sd = date(n2.snapshot_date) - INTERVAL 1 DAY
    group by n2.snapshot_date, date(n2.snapshot_date), a.sss;
    """
    query_top_50_subtasks_success_past_90_days = """
    select max(n3.subtasks_success) subtasks_success
            , substr(n1.node_id,1,10) short_node_id
            , n2.node_name
            , date(n3.snapshot_date) snapshot_date
    from (
      select node_id,
        max(snapshot_date) snapshot_date,
        max(subtasks_success) mss
      from network_01
      group by node_id
      order by mss desc
      LIMIT 50) n1
    inner join network_01 n2
      on n2.node_id = n1.node_id
      and n2.snapshot_date = n1.snapshot_date
    inner join network_01 n3
      on n3.node_id = n1.node_id
      and n3.snapshot_date > (n1.snapshot_date - INTERVAL 90 DAY)
    group by n1.node_id, n2.node_name, date(n3.snapshot_date)
    order by 4,1;
    """
    query_subtasks_success_top_50 = """
    select n1.mss subtasks_success
            , substr(n1.node_id,1,10) short_node_id
            , n2.node_name
            , n2.snapshot_date
            , n2.cpu_cores
            , n2.allowed_resource_size
            , n2.allowed_resource_memory
    from (
      select node_id,
        max(snapshot_date) snapshot_date,
        max(subtasks_success) mss
      from network_01
      group by node_id
      order by mss desc
      LIMIT 50) n1
    inner join network_01 n2
      on n2.node_id = n1.node_id
      and n2.snapshot_date = n1.snapshot_date
    order by n1.mss desc, n1.snapshot_date asc;
    """
    query_daily_distinct_count = """
    select date(snapshot_date) snapshot_date
      , count(distinct node_id) distinct_cnt 
    from network_01 
    group by date(snapshot_date);
    """
    query_all_nodes_last_seen_state = """
    select substr(n1.node_id,1,10) short_node_id
        , n2.node_name
        , n2.snapshot_date
        , n2.cpu_cores
        , n2.allowed_resource_size
        , n2.allowed_resource_memory
        -- , n1.node_id
    from (
      select node_id,
        max(snapshot_date) snapshot_date
      from network_01
      group by node_id) n1
    INNER JOIN network_01 n2
        ON n2.node_id = n1.node_id
        and n2.snapshot_date = n1.snapshot_date
    LIMIT 20;
    """
    query_node_by_name = """
    select 
    n2.unique_node_id
    ,n2.snapshot_date
    ,n2.node_id
    ,n2.node_name
    -- ,n2.node_version
    -- ,n2.last_seen
    -- ,n2.os
    -- ,n2.ip
    -- ,n2.start_port
    -- ,n2.end_port
    -- ,n2.performance_general
    -- ,n2.performance_blender
    -- ,n2.performance_lux
    -- ,n2.allowed_resource_size
    -- ,n2.allowed_resource_memory
    -- ,n2.cpu_cores
    -- ,n2.min_price
    -- ,n2.max_price
    -- ,n2.subtasks_success
    -- ,n2.subtasks_error
    -- ,n2.subtasks_timeout
    -- ,n2.p2p_protocol_version
    -- ,n2.task_protocol_version
    -- ,n2.tasks_requested
    -- ,n2.known_tasks
    -- ,n2.supported_tasks
    -- ,n2.rs_tasks_cnt
    -- ,n2.rs_finished_task_cnt
    -- ,n2.rs_requested_subtasks_cnt
    -- ,n2.rs_collected_results_cnt
    -- ,n2.rs_verified_results_cnt
    -- ,n2.rs_timed_out_subtasks_cnt
    -- ,n2.rs_not_downloadable_subtasks_cnt
    -- ,n2.rs_failed_subtasks_cnt
    -- ,n2.rs_work_offers_cnt
    -- ,n2.rs_finished_ok_cnt
    -- ,n2.rs_finished_ok_total_time
    -- ,n2.rs_finished_with_failures_cnt
    -- ,n2.rs_finished_with_failures_total_time
    -- ,n2.rs_failed_cnt
    -- ,n2.rs_failed_total_time
    -- ,n2.os_system
    -- ,n2.os_release
    -- ,n2.os_version
    -- ,n2.os_windows_edition
    -- ,n2.os_linux_distribution
    from (select node_id
                , max(snapshot_date) msd
                from network_01
                where 1=1
                -- and node_id = ''
                and node_name = 'kascheri12'
                group by node_id
                ) n1
    inner join network_01 n2
      ON n2.node_id = n1.node_id
      and n2.snapshot_date = n1.msd
    where 1 = 1;
    """
    conn.query(my_query)
    
