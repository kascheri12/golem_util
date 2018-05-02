import csv, os, time, sys, traceback, codecs
from datetime import datetime as dt
from datetime import timedelta
from os import remove
from shutil import move


class Load_Data:

  def __init__(self):
    self.d = self.load_data()

  def get_data(self):
    return self.d

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
    try:
      nr[self._ss_index] = float(row[self._ss_index])
    except IndexError:
      nr[self._ss_index] = 0
    except ValueError:
      nr[self._ss_index] = 0
    except:
      nr[self._ss_index] = 0
    return nr

  def load_new_data(self):
    print("Begin load_new_data. Loading each file into data")
    all_data = {
      'data':[],
      'header':[]
    }
    for filename in [x for x in os.listdir('node_logs/') if x.find('network') != -1 or x.find('old_logs.log') != -1]:
      try:
        with codecs.open('node_logs/'+filename,'rb',"UTF-8") as f:
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
