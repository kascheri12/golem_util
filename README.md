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
          unique_node_id                        int(11)       NO    PRI  NULL  auto_increment
          ,snapshot_date                         datetime      NO    PRI  NULL
          ,node_id                               varchar(200)  NO         NULL
          ,node_name                             varchar(200)  YES        NULL
          ,node_version                          varchar(100)  YES        NULL
          ,last_seen                             bigint(20)    YES        NULL
          ,os                                    varchar(50)   YES        NULL
          ,ip                                    varchar(100)  YES        NULL
          ,start_port                            varchar(20)   YES        NULL
          ,end_port                              varchar(20)   YES        NULL
          ,performance_general                   float         YES        NULL
          ,performance_blender                   float         YES        NULL
          ,performance_lux                       float         YES        NULL
          ,allowed_resource_size                 double        YES        0
          ,allowed_resource_memory               double        YES        0
          ,cpu_cores                             int(11)       YES        NULL
          ,min_price                             double        YES        0
          ,max_price                             double        YES        0
          ,subtasks_success                      int(11)       YES        NULL
          ,subtasks_error                        int(11)       YES        NULL
          ,subtasks_timeout                      int(11)       YES        NULL
          ,p2p_protocol_version                  varchar(100)  YES        NULL
          ,task_protocol_version                 varchar(100)  YES        NULL
          ,tasks_requested                       int(11)       YES        NULL
          ,known_tasks                           int(11)       YES        NULL
          ,supported_tasks                       int(11)       YES        NULL
          ,rs_tasks_cnt                          int(11)       YES        NULL
          ,rs_finished_task_cnt                  int(11)       YES        NULL
          ,rs_requested_subtasks_cnt             int(11)       YES        NULL
          ,rs_collected_results_cnt              int(11)       YES        NULL
          ,rs_verified_results_cnt               int(11)       YES        NULL
          ,rs_timed_out_subtasks_cnt             int(11)       YES        NULL
          ,rs_not_downloadable_subtasks_cnt      int(11)       YES        NULL
          ,rs_failed_subtasks_cnt                int(11)       YES        NULL
          ,rs_work_offers_cnt                    int(11)       YES        NULL
          ,rs_finished_ok_cnt                    int(11)       YES        NULL
          ,rs_finished_ok_total_time             float         YES        NULL
          ,rs_finished_with_failures_cnt         int(11)       YES        NULL
          ,rs_finished_with_failures_total_time  float         YES        NULL
          ,rs_failed_cnt                         int(11)       YES        NULL
          ,rs_failed_total_time                  float         YES        NULL
          ,os_system                             varchar(100)  NO         NULL
          ,os_release                            varchar(100)  NO         NULL
          ,os_version                            varchar(100)  NO         NULL
          ,os_windows_edition                    varchar(100)  NO         NULL
          ,os_linux_distribution                 varchar(100)  NO         NULL
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
