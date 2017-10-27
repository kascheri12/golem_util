
import csv
import os
import pandas as pd
import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt

def __main__(argv):
  do_histogram()
  
def do_histogram():
  d = load_data()
  write_data_to_file(d)
  col_names = ['Account ID','Line Item','Start Time','End Time','Project','Measurement1','Measurement1 Total Consumption','Measurement1 Units','Cost','Currency','Project Number','Project ID','Project Name','Project Labels','Description']
  data = pd.read_csv('charges/tmp_all.csv',names=col_names)
  data.hist()
  plt.show()
  
    
def graph_cost():
  cost_list = []
  item_list = []
  d = load_data()
  for i in range(len(d['filenames'])):
    for item in d[d['filenames'][i]]:
      cost = item[d['headers'][i].index('Cost')]
      item = item[d['headers'][i].index('Line Item')]
      if float(cost) > .001:
        cost_list.append(cost)
        item_list.append(item)
  # Create a trace
  trace = go.Scatter(
      x = item_list,
      y = cost_list,
      mode = 'markers'
  )
  data = [trace]
  # Plot and embed in ipython notebook!
  plotly.offline.plot(data, filename='basic-scatter')

  
def write_data_to_file(data):
  with open('charges/tmp_all.csv','w') as f:
    wr = csv.writer(f)
    for file_item in data['filenames']:
      for row in data[file_item]:
        wr.writerow(row)

def print_data(d,sort_method=None,ascending=False):
  cols=d['headers'][0]
  pd.set_option('display.max_columns',0)
  pd.set_option('display.max_colwidth',25)
  pd.options.display.float_format = '{:.7f}'.format
  df = pd.DataFrame(d,columns=cols)
  if sort_method is not None:
    df1 = df.sort_values(sort_method,ascending=ascending)
    print(df1)
  else:
    print(df)
    
def load_data():
  d = load_raw_data()
  cd = cleanse_data(d)
  d['output20170921'] = cd[0]
  d['output20170922'] = cd[1]
  return d

def cleanse_data(d):
  data_set = []
  new_d = []
  for row in d['output20170921']:
    for j in range(len(row)):
      if j not in (8,9,10):
        new_d.append(row)
  data_set.append(new_d)
  new_d = []
  for row in d['output20170922']:
    for j in range(len(row)):
      if j not in (8,9,10):
        new_d.append(row)
  data_set.append(new_d)
  return data_set

def load_raw_data():
  all_data = {
    'filenames' : [],
    'headers' : []
  }
  for filename in os.listdir('charges/'):
    with open('charges/'+filename,'rt') as f:
      fname = filename.replace("-","").replace(".csv","")
      reader = csv.reader(f,delimiter=',')
      first_row = True
      d = []
      for row in reader:
        if first_row:
          first_row = False
          all_data['headers'].append(row)
        else:
          d.append(row)
      all_data['filenames'].append(fname)
      all_data[fname] = d
  return all_data

if __name__ == '__main__':
  __main__(sys.argv[1:])
