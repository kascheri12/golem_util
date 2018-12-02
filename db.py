import mysql.connector
from mysql.connector import errorcode
import config, time

class DB():
  def __init__(self,env="TEST"):
    try:
      if env == "PROD":
        self._db = mysql.connector.connect(**config.db_config_prod)
      elif env == "TEST":
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
  
if __name__ == '__main__':
  main()
