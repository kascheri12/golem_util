import subprocess, time, requests, json, config, os

class Load_Requestor_Data():

  def __init__(self):
    self.prep_build_graphs_dir()

  def prep_build_graphs_dir(self):
    if not os.path.isdir(config.build_graphs_dir):
      os.mkdir(config.build_graphs_dir)

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
            nni[item.split(": ")[0]] = item.split(": ")[1].replace('\'','').replace('\\','')
          except:
            nni[item.split(": ")[0]] = None
        node_list_obj.append(nni)
    return node_list_obj

  def get_count_of_occurances_of_ip(self, nlo, nip):
    return len([x for x in nlo if x['node_ip_address'] == nip])

  def get_max_performance_of_node(self, nlo, nip):
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

  def get_pretty_time(self):
    lt = time.localtime()
    return time.strftime("%Y%m%d%H%M",lt)

  def save_json_file_of_subtask_data(self):
    nlo = self.build_final_obj()
    with open(config.build_graphs_dir + self.get_pretty_time() + "_providor_node_data.json", 'w') as f:
      json.dump(nlo,f)


def main():

  lrd1 = Load_Requestor_Data()
  lrd1.save_json_file_of_subtask_data()
  
if __name__ == '__main__':
    main()
