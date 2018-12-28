# golem_util

This library has been composed to log historical network snapshots of golem network and analyze that data, creating datatables and graphs deployed to a webserver.

## Installation

In order to use the Node_Logging class

## Classes in the library

  * DB
    * Purpose: This class is responsible for handling the database connection and basic query and fetch operations.
    * Installation:
      * Setup and install a mysql database server
      * Configure a database (ex.`golem_util_01`) and user with permissions to database
      * Create table with below structure:
        ```sql
        create table golem_network
        (
          unique_node_id                        int(11)       NOT NULL   auto_increment
          ,snapshot_date                         datetime      NOT NULL  
          ,node_id                               varchar(200)  NOT NULL
          ,node_name                             varchar(200)      default NULL
          ,node_version                          varchar(100)      default NULL
          ,last_seen                             bigint(20)        default NULL
          ,os                                    varchar(50)       default NULL
          ,ip                                    varchar(100)      default NULL
          ,start_port                            varchar(20)       default NULL
          ,end_port                              varchar(20)       default NULL
          ,performance_general                   float             default NULL
          ,performance_blender                   float             default NULL
          ,performance_lux                       float             default NULL
          ,allowed_resource_size                 double            default 0
          ,allowed_resource_memory               double            default 0
          ,cpu_cores                             int(11)           default NULL
          ,min_price                             double            default 0
          ,max_price                             double            default 0
          ,subtasks_success                      int(11)           default NULL
          ,subtasks_error                        int(11)           default NULL
          ,subtasks_timeout                      int(11)           default NULL
          ,p2p_protocol_version                  varchar(100)      default NULL
          ,task_protocol_version                 varchar(100)      default NULL
          ,tasks_requested                       int(11)           default NULL
          ,known_tasks                           int(11)           default NULL
          ,supported_tasks                       int(11)           default NULL
          ,rs_tasks_cnt                          int(11)           default NULL
          ,rs_finished_task_cnt                  int(11)           default NULL
          ,rs_requested_subtasks_cnt             int(11)           default NULL
          ,rs_collected_results_cnt              int(11)           default NULL
          ,rs_verified_results_cnt               int(11)           default NULL
          ,rs_timed_out_subtasks_cnt             int(11)           default NULL
          ,rs_not_downloadable_subtasks_cnt      int(11)           default NULL
          ,rs_failed_subtasks_cnt                int(11)           default NULL
          ,rs_work_offers_cnt                    int(11)           default NULL
          ,rs_finished_ok_cnt                    int(11)           default NULL
          ,rs_finished_ok_total_time             float             default NULL
          ,rs_finished_with_failures_cnt         int(11)           default NULL
          ,rs_finished_with_failures_total_time  float             default NULL
          ,rs_failed_cnt                         int(11)           default NULL
          ,rs_failed_total_time                  float             default NULL
          ,os_system                             varchar(100)  NOT NULL 
          ,os_release                            varchar(100)  NOT NULL 
          ,os_version                            varchar(100)  NOT NULL 
          ,os_windows_edition                    varchar(100)  NOT NULL 
          ,os_linux_distribution                 varchar(100)  NOT NULL 
          ,primary key(unique_node_id,snapshot_date)
        );
        
        create table golem_network_globe
        (
          ip                            varchar(20)  NOT NULL
          ,port                         int(10)      NOT NULL
          ,node_id                      varchar(100) NOT NULL
          ,node_name                    varchar(100)
          ,version                      varchar(50)
          ,latitude                     varchar(50)
          ,longitude                    varchar(50)
        );
        ```
      * Copy `config.example.py` to `config.py` and change to appropriate values
      * At this point, you should be able to successfully instantiate a DB object used in following classes

  * Node_Logging
    * Purpose: This class is used to log snapshots of active nodes into a mysql database. The snapshot interval can be configured in the private static variables of the object. 
    * Reference: Scan_Nodes
    * Usage:
    
      ```
      python node_logging.py
      ```
      
  * Golem_Graphing
    * Purpose: This class is responsible for building and publishing graphs repeatedly. The interval may be changed in the private variables. This class utilizes Analyze_Data above to refresh different subsections of the front-end.
    * Reference: Analyze_Data
    * Usage:
      
      ```
      python golem_graphing.py
      ```
