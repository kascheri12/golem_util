import subprocess, time

class Load_Requestor_Data():

  def __init__(self):
    self.d = self.load_new_data()

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
    
  def build_final_obj(self):
    nlo = self.build_node_list_obj_from_requests()
    nnl = [{'ip_address':x} for x in set([m['node_ip_address'] for m in nlo])]
    req_str = "http://api.ipstack.com/{0}?access_key=c43656dc64550aaaa42dfb34c29c9afb"
    for n in nnl:
      geojson = requests.get(req_str.format(n['ip_address']))
      n['longitude'] = geojson['longitude']
      n['latitude'] = geojson['latitude']
    print(nnl[0])


    
    
