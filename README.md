# golem_util
A utility library being built to track progress of the golem network


## Classes in the library

  * Create_Task
    * Purpose: This class is used to request tasks on the network. The class has a function to build a task json file from a template.
    * Pre-Req: There are some instructions [here](https://github.com/kascheri12/kascheri12.github.io/blob/master/pages/ubuntu_deployment.md#testing-golem) about testing.
    * Usage:
      
      ```
      python create_task.py
      ```

  * Node_Logging
    * Purpose: This class is used to log snapshots of active nodes into a flat file within sub-folder node_logs. The snapshot interval can be configured in the private variables of the object. 
    * Usage:
    
      ```
      python node_logging.py
      ```
  
  * Load_Data
    * Purpose: Utilized to load the data that was logged.
    * Usage:
    
      ```
      import load_data as ld
      load_data_ob = ld.Load_Data()
      ```
      
  
  * Analyze_Data
    * Purpose: This class is responsible for building graphs provided data. If a Load_Data object is not supplied on initialization, one will be loaded.
    * Usage:
    
      ```
      import analyze_data as ad
      analyze_data_obj = ad.Analyze_Data()
      ```
      
  * Golem_Graphing
    * Purpose: This class is responsible for building and publishing graphs repeatedly. The interval may be changed in the private variables. 
    * Usage:
      
      ```
      python golem_graphing.py
      ```
    
