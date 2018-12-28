import subprocess, time, requests, json, config, os, db, re

class Golem_Network_Globe():

  def __init__(self):
    self.conn = db.DB()

  def query_all_globe_db(self):
    query = "select * from network_globe_01;"
    self.conn.query(query)
    return (self.conn.fetchfields(),self.conn.fetchall())

  def build_list_known_nodes(self):
    # The following line executes the command `golemcli --mainnet network dht` and excludes the header and footer content
    # The results are stored in a list, each row of the results is the first array, the columns of each row are an array also
    # ex.. list_known_nodes[0][0] : output: 192.101.100.1
    mspace = re.compile(r'\s{2,}')
    list_known_nodes = [mspace.split(x) for x in [y for y in str(subprocess.check_output(['golemcli','--mainnet','network','dht'])).split("\\n")[2:-1]]]
    # Not all nodes have names, insert a blank column for the ones without names
    for i in range(len(list_known_nodes)):
      if len(list_known_nodes[i]) == 4:
        list_known_nodes[i].insert(4,'')
    return list_known_nodes

  def add_update_globe_db(self):
    # Query list of db records from Globe table
    qr = self.query_all_globe_db()[1]
    # Get build_list_known_nodes results
    list_known_nodes = self.build_list_known_nodes()
    
    # Iterate through list of known nodes
    for node in list_known_nodes:
      # Get list of qr nodes in latest known nodes snapshot
      does_exist = [x for x in qr if x[2] == node[2]]
      if len(does_exist) > 0:
        # Refresh lat/long if IP has changed
        if does_exist[0][0] != node[0]:
          # Find lat/long associated with new IP
          print('Old IP:{}  | Old Lat:{}  | Old Long:{}'.format(does_exist[0][0],does_exist[0][5],does_exist[0][6]))
          (does_exist[0][5],does_exist[0][6]) = self.get_lat_long_for_ip(node[0])
          print('New IP:{}  | New Lat:{}  | New Long:{}'.format(does_exist[0][0],does_exist[0][5],does_exist[0][6]))
        # Found existing node_id; update ip, port, name, version, lat, long in db
        # print('Verify New IP:{}  | New Lat:{}  | New Long:{}'.format(does_exist[0][0],does_exist[0][5],does_exist[0][6]))
        self.conn.update_known_node_in_globe_db((node[0],node[1],node[3],node[4],does_exist[0][5],does_exist[0][6],node[2]))
      else:
        (lat,long) = self.get_lat_long_for_ip(node[0])
        # Node ID not found in db, insert record
        self.conn.insert_known_node_into_globe_db((*tuple(node),lat,long))
    
    # List of nodes from db not known anymore
    not_known_anymore = [x for x in qr if x[2] not in [a[2] for a in list_known_nodes]]
    for n in not_known_anymore:
      # Delete these id's from db, they're not known nodes anymore
      self.conn.delete_node_from_globe_db((n[2],))
  
  def get_lat_long_for_ip(self,ip):
    req_str = "http://api.ipstack.com/{}?access_key=c43656dc64550aaaa42dfb34c29c9afb"
    geojson = requests.get(req_str.format(ip)).json()
    return (round(geojson['latitude'],9),round(geojson['longitude'],9))

  def save_json_file_of_network_globe_data(self):
    filename = "network_data.json"
    data_file = self.build_data_file_content()
    with open(config.build_graphs_dir + filename, 'w') as f:
      json.dump(data_file,f)
    return filename
    
  def build_data_file_content(self):
    q = "select latitude,longitude,case when count(*) > 5 then 5 else count(*) end size from network_globe_01 group by latitude,longitude order by size;"
    self.conn.query(q)
    res = self.conn.fetchall()
    rv = [{'latitude':x[0],'longitude':x[1],'size':x[2]} for x in res]
    return rv

def main():

  gng = Golem_Network_Globe()
  gng.add_update_globe_db()
  
if __name__ == '__main__':
  main()
