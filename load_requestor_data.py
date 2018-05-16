import subprocess, time, requests

class Load_Requestor_Data():

  def __init__(self):
    pass

  def build_node_list_obj_from_requests(self):
    list_of_task_ids = [j[0] for j in [x.split() for x in [y for y in str(subprocess.check_output(['golemcli','tasks','show'])).split("\\n")[2:-1]]]]
    task_list_obj = []
    node_list_obj = []
    dist_ip_list = []
    for t in list_of_task_ids:
      task_list_obj.append([j[-6:] for j in [x.split() for x in [y for y in str(subprocess.check_output(['golemcli','tasks','subtasks',t])).split("\\n")[2:-1]]] if len(j[0]) < 18])
    for task in task_list_obj:
      for st in task:
        subtask = [j for j in str(subprocess.check_output(['golemcli','subtasks','show',st[1]])).split("\\n")]
        ni = subtask[4:7]+subtask[10:12]+[subtask[13]]
        nni = {}
        for item in ni:
          try:
            nni[item.split(": ")[0]] = item.split(": ")[1].replace('\'','')
          except:
            nni[item.split(": ")[0]] = None
        node_list_obj.append(nni)
    return node_list_obj
    
  def get_count_of_occurances_of_ip(nlo, nip):
    return len([x for x in nlo if x['node_ip_address'] == nip])

  def get_max_performance_of_node(nlo, nip):
    return max([b['node_performance'] for b in [x for x in nlo if x['node_ip_address'] == nip]])
    
  def build_final_obj(self):
    nlo = self.build_node_list_obj_from_requests()
    nnl = [{'ip_address':x} for x in set([m['node_ip_address'] for m in nlo])]
    req_str = "http://api.ipstack.com/{0}?access_key=c43656dc64550aaaa42dfb34c29c9afb"
    for i in range(len(nnl)):
      geojson = requests.get(req_str.format(nnl[i]['ip_address'])).json()
      nnl[i]['longitude'] = geojson['longitude']
      nnl[i]['latitude'] = geojson['latitude']
      nnl[i]['max_performance'] = self.get_max_performance_of_node(nlo,nnl[i]['ip_address'])
      nnl[i]['count_of_occurances'] = self.get_count_of_occurances_of_ip(nlo,nnl[i]['ip_address'])
    return nnl
      
