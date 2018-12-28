import mysql.connector
from mysql.connector import errorcode
import config, time

class DB():
  def __init__(self):
    try:
      if config.db_prod:
        self._db = mysql.connector.connect(**config.db_config_prod)
      else:
        self._db = mysql.connector.connect(**config.db_config_test)
      self._cursor = self._db.cursor()
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
  def __enter__(self):
    return self
  def __exit__(self, exc_type, exc_val, exc_tb):
    self._db.close()
  @property
  def cursor(self):
    return self._cursor
  def query(self, sql, params=None):
    self.cursor.execute(sql, params or ())
  def fetchall(self):
    return self.cursor.fetchall()
  def fetchone(self):
    return self.cursor.fetchone()
  def fetchfields(self):
    return [i[0] for i in self.cursor.description]
  def insert_node_record_data(self,node_snapshot):
    insert_node_record_query = """ insert into network_01 (
                snapshot_date,
                node_id,
                node_name,
                node_version,
                last_seen,
                os,
                os_system,
                os_release,
                os_version,
                os_windows_edition,
                os_linux_distribution,
                ip,
                start_port,
                end_port,
                performance_general,
                performance_blender,
                performance_lux,
                allowed_resource_size,
                allowed_resource_memory,
                cpu_cores,
                min_price,
                max_price,
                subtasks_success,
                subtasks_error,
                subtasks_timeout,
                p2p_protocol_version,
                task_protocol_version,
                tasks_requested,
                known_tasks,
                supported_tasks,
                rs_tasks_cnt,
                rs_finished_task_cnt,
                rs_requested_subtasks_cnt,
                rs_collected_results_cnt,
                rs_verified_results_cnt,
                rs_timed_out_subtasks_cnt,
                rs_not_downloadable_subtasks_cnt,
                rs_failed_subtasks_cnt,
                rs_work_offers_cnt,
                rs_finished_ok_cnt,
                rs_finished_ok_total_time,
                rs_finished_with_failures_cnt,
                rs_finished_with_failures_total_time,
                rs_failed_cnt,
                rs_failed_total_time
                ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )"""
    try:
      self.query(insert_node_record_query,node_snapshot)
      self._db.commit()
    except mysql.connector.Error as e:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.insert_node_record_data() Exception thrown inserting record")
      print ("Error code: ", e.errno)        # error number
      print ("SQLSTATE value: ", e.sqlstate) # SQLSTATE value
      print ("Error message: ", e.msg)       # error message
    except:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.insert_node_record_data() Exception thrown inserting record")

  def update_known_node_in_globe_db(self,node_info):
    mq = """
    update network_globe_01 
        set ip = %s,
        port = %s,
        node_name = %s,
        version = %s,
        latitude = %s, 
        longitude = %s
    where node_id = %s;
    """
    try:
      self.query(mq,node_info)
      self._db.commit()
    except mysql.connector.Error as e:
      print(mq)
      print(node_info)
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.update_known_node_in_globe_db() Exception thrown")
      print ("Error code: ", e.errno)        # error number
      print ("SQLSTATE value: ", e.sqlstate) # SQLSTATE value
      print ("Error message: ", e.msg)       # error message
    except:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.update_known_node_in_globe_db() Exception thrown")
  
  def insert_known_node_into_globe_db(self,node_info):
    mq = """
    insert into network_globe_01 (ip,port,node_id,node_name,version,latitude,longitude) values (%s,%s,%s,%s,%s,%s,%s);
    """
    try:
      self.query(mq,node_info)
      self._db.commit()
    except mysql.connector.Error as e:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.insert_known_node_into_globe_db() Exception thrown inserting record")
      print ("Error code: ", e.errno)        # error number
      print ("SQLSTATE value: ", e.sqlstate) # SQLSTATE value
      print ("Error message: ", e.msg)       # error message
    except:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.insert_known_node_into_globe_db() Exception thrown inserting record")
  
  def delete_node_from_globe_db(self,node_id):
    mq = """
    delete from network_globe_01 where node_id = %s;
    """
    try:
      self.query(mq,node_id)
      self._db.commit()
    except mysql.connector.Error as e:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.delete_node_from_globe_db() Exception thrown")
      print ("Error code: ", e.errno)        # error number
      print ("SQLSTATE value: ", e.sqlstate) # SQLSTATE value
      print ("Error message: ", e.msg)       # error message
    except:
      print(mq)
      print(node_id)
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.delete_node_from_globe_db() Exception thrown")
  
  def init_globe_db(self):
    mq = """create table network_globe_01
            (
            ip                            varchar(20)  NOT NULL
            ,port                         int(10)      NOT NULL
            ,node_id                      varchar(100) NOT NULL
            ,node_name                    varchar(100)
            ,version                      varchar(50)
            ,latitude                     varchar(50)
            ,longitude                    varchar(50)
            );"""
    try:
      self.query(mq)
      self._db.commit()
    except mysql.connector.Error as e:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.init_globe_db() Exception thrown ")
      print ("Error code: ", e.errno)        # error number
      print ("SQLSTATE value: ", e.sqlstate) # SQLSTATE value
      print ("Error message: ", e.msg)       # error message
    except:
      et = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
      print(et+": DB.init_globe_db() Exception thrown ")
  
if __name__ == '__main__':
  main()
