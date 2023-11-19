### Program directory
Each directory is a relatively independent sub-module, used to complete an independent function, such as: data crawling, process mining, etc. Global configuration item information is in the `Config.py` script in each module. Note: `Config.py` of each module is not interoperable!

#### Database related
Dataset is available at https://figshare.com/articles/dataset/Dataset_for_replication_package_of_mining_PRs/24587457

1. In the attached dataset.zip pressed package, each project has two `sql` files, corresponding to three types of data, as follows. in

2. `*_self.sql`: basic information of PR in the project, such as: PR creator, creation event, closing time, included commits, etc.
3. `*_event_log.sql`: event information contained in PR in the project


#### Public module

1. DataAcquire: Acquire experimental data. Use API to crawl PR event logs and calculate two types of privilege escalation personnel based on the logs
2. Utils: Tools, such as time conversion, log file reading, database reading and writing
3. Kappa: Use Kappa to calculate the consistency of two people’s classification results of abnormal root causes.
#### Work: "Process Abnormal PR Identification" related modules

1. ProcessMining: data preprocessing, process discovery, consistency testing
2. LabelData: Semantic anomaly identification
3. ProcessAnomalyPR: Control flow anomaly identification and abnormal result summary
4. NormalProcessModel: Mining normal process models and extracting typical features of the models


#### DataAcquire module-----data acquisition and processing

#### Module function description

##### Obtain experimental data: Use Timeline API to crawl PR event logs

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1687137009109-b19e3b44-6c81-4859-af55-7bb969d3b3ab.png#averageHue=%232b3646&clientId=uecda5481-cc36-4&from=paste&height=175&id=u078e0252&originHeight=227&originWidth=241&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=9321&status=done&style=none&taskId=u68034fdf-2693-460c-ace7-e7411b3b6d8&title=&width=185.3846221844828)

##### Directory Description

1. `event_log` saves the event log after initial processing. Note: The original event logs crawled by the API are stored directly in the database
2. `role_change` saves the information of the person with elevated privileges
##### Step 1: Crawl data

1. `crawl_pr_data.py` uses [Pulls API](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#get-a-pull-request) to crawl PR Basic data. PR basic data is **pre-data** and must be crawled first. PR basic data uses
2. `timeline_api.py` uses [Timeline API](https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28) to crawl PR event logs.
3. After the above two types of data are crawled, they will be saved directly to the database without forming a csv file.
##### Step 2: Preliminary data processing

1. `extract_event_log.py`
   1. Input: None, read data directly from the database
   2. Output: Save to the `event_log` directory in the form of csv file
   3. Function: Initial processing of PR event logs, that is, eliminating PRs that are still open, extracting key activities, and classifying activity types
##### Other script instructions

1. `Config.py` saves global variables, such as: file storage path
2. The `crawl_commit_data.py` script is responsible for crawling the specific information of the commit contained in the PR, which will be used when calculating features for anomaly detection.
#### ProcessMining module
##### Module function description
Functions: event log processing and grouping, process discovery, consistency check, calculation of variant information. Introduced in sequence according to the script execution process

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1685157553639-a2a2c96a-fcb7-4ba3-89c4-95188f7ba966.png#averageHue=%23262c33&clientId=uf9bdc17f-df9c-4&from=paste&height=248&id=u07e0213c&originHeight=322&originWidth=366&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=21550&status=done&style=none&taskId=uf5f11ae9-9aa0-4c79-b34e-0006a8eea28&title=&width=281.53847186523114)

##### Directory introduction

1. `process_log` saves the preprocessed event log (one file for each project)
2. `scene_process_log` saves the preprocessed event log (one file for each PR collaboration scene)
3. `process_model` saves the process model and contains two subdirectories
   1. `bpmn`: Save the process model file in `bpmn` format
   2. `petri-net`: Save process model files in `petri-net` format
4. `model_evaluation` saves the quality evaluation results of the process model
5. `conformance_check` saves the results of the consistency check and contains two subdirectories
   1. Alignments: Results obtained using the `alignments` consistency check algorithm
   2. tbr: Results obtained using the `token-based replay` consistency check algorithm
##### Step 1: Data filtering and grouping

1. `event_log_process.py`
   1. Enter: `../DataAcquire/event_log/`
   2. Output: `process_log` directory
   3. Function
      1. Filter cases containing low-frequency behavior (ReopenPR) and only retain **key activities**
      2. Format the contents of the event log
2. `scene_process_log.py` (a combination of fork/unfork, merge/close, divide PR into four categories)
   1. Input: `process_log` directory
   2. Output: `scene_process_log` directory
   3. Function:
      1. Eliminate cyclic structures: combine the same type of activities performed continuously by the same person into one
      2. Data grouping: Group the cases according to different collaboration scenarios, namely fork_merge, fork_close and other four collaboration scenarios.
##### Step 2: Build a quasi-normal model

1. `process_discovery.py` script
   1. Input: `scene_process_log` directory
   2. Output: `petri_net` and `bpmn` subdirectories in the `process_model` directory, two representations of the same model
   3. Function: Build from event logs
##### Step 3: Consistency check

1. `conformance_checking_*.py`
   1. Input: `scene_process_log` log file directory, `process_model/petri_net` model file directory
   2. Output: `conformance_check/alignments` directory, consistency check results
   3. Function:
      1. `conformance_checking_train.py` and `conformance_checking_test.py` conduct consistency tests on the case sets corresponding to high-frequency process variants (80%) and low-frequency process variants (20%) respectively.
      2. `conformance_checking_result_merge.py` merges the results of train and test into one file, as follows

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1687141595299-4ef275cd-9391-4554-ab00-6a88cd05f0e8.png#averageHue=%232c3545&clientId=uecda5481-cc36-4&from=paste&height=129&id=u3c46bb7c&originHeight=168&originWidth=314&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=7095&status=done&style=none&taskId=ua602e9bb-26e1-4e28-8e83-37c64a7ceed&title=&width=241.53847039803983)
##### Other script instructions

1. `Config.py` saves global variables, such as: file storage path, minimum overall coverage threshold, etc.
#### LabelData module
##### Module function description
Function: Identify four types of semantic anomalies. The red boxes mark the four types of semantic anomalies that are not currently considered.

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1685158184878-dd9aa6a9-19fa-4af8-ac6e-98c5c5de048e.png#averageHue=%2329323f&clientId=uf9bdc17f-df9c-4&from=paste&height=249&id=uaa3d0b6c&originHeight=324&originWidth=349&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=21967&status=done&style=none&taskId=u363f964a-019c-4470-b8ea-cb823e94522&title=&width=268.46154830864936)
##### Directory Description

1. `anomaly_pr`: saves four types of semantic anomaly recognition results
2. `cluster`: Saves the activity transition information in each case. **Activity transition (also called edge vector)** is an activity pair in the form of "Activity A→Activity B", such as: Case <A,B ,C> corresponds to two edge vectors A→B, B→C
##### Step 1: Calculate the edge vector in the case

1. `trace_cluster.py`
   1. Enter: `../ProcessMining/scene_process_log` directory
   2. Output: `cluster` directory, which saves the occurrence number information of all edge vectors in the case
   3. Function: Count the number of occurrences of edge vectors in each case.
##### Step 2: Identify semantic anomalies

1. `no_reviewer_response_but_close.py`, `no_reviewer_response_but_merge.py`, `review_approved_but_close.py`, `review_rejected_but_merge.py`
   1. Input: `cluster` directory
   2. Output: `anomaly_pr` directory
   3. Function: The four scripts respectively correspond to four types of semantic anomaly recognition. During the recognition, the email information of the persons related to the anomaly will also be recorded.

#### ProcessAnomalyPR module
##### Introduction to module functions
Function: Process abnormal PR identification module

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1685167747822-84222e41-0102-4b0f-abd1-03c20ec6c5b4.png#averageHue=%23282e36&clientId=uf9bdc17f-df9c-4&from=paste&height=247&id=uae1cc214&originHeight=450&originWidth=382&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=29266&status=done&style=none&taskId=uc19ebfbd-ff42-4d3b-b93d-96d05bf08e4&title=&width=209.89011758883353)
##### Directory introduction

1. `log_variant` directory: saves process variant information
2. `process_anomaly_pr` directory: saves process anomaly PR identification results
3. `summaly` directory: save experimental result data
4. `figure` directory: saves the drawing information of the experimental results
##### Step 1: Calculate process variant information

1. `LogVariant.py`
   1. Input: `scene_process_log` directory
   2. Output: `log_variant` directory
   3. Function: Calculate the **process variant** information corresponding to each case in the specific `scene` event log, and use it for subsequent analysis of the cause of control flow exceptions
##### Step 2: Identify `Control Flow Anomaly`

1. `control_flow_anomaly_pr.py`
   1. Enter: `../ProcessMining/conformance_check/alignments`
   2. Output: `process_anomaly_pr/control_flow_anomaly_pr.xls`
   3. Function:
      1. Identify control flow anomalies, cal_control_flow_anomaly_pr() function, that is, filter out cases below the minimum fit threshold from conformance_check_test
      2. Analysis of control flow exception causes, check_alignment() function
##### Step 3: Summarize the `semantic anomaly` recognition results

2. `semantic_anomaly_pr`
   1. Enter: `../LabelData/anomaly_pr` directory
   2. Output: `process_anomaly_pr/semantic_anomaly_pr.xls`
   3. Function: Summarize the four **Semantic Anomaly** recognition results into one file
##### Step 4: Summarize the recognition results of `Control Flow Anomaly` and `Semantic Anomaly`

3. `process_anomaly_pr.py`
   1. Input: `process_anomaly_pr` directory
   2. Output: `process_anomaly_pr/process_anomaly_pr.xls`
   3. Function: Summarize control flow exception and semantic exception results into one file
##### Step 5: Statistics of the distribution of the number of abnormal PRs

4. `statistic_anomaly_num.py`
   1. Input: `process_anomaly` directory
   2. Output: `summary` directory
   3. Function
      1. Statistics on the distribution of the number of abnormal control flow PRs in the project
      2. Statistical distribution of the number of semantic anomaly PRs in projects
      3. Reasons why PR is closed in statistical semantic anomaly PR

#### NormalProcessModel module
##### Module function
Function: Use the normal case set obtained after eliminating control flow anomalies and semantic anomalies to build a normal process model (**clustering/non-clustering**)

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1685169812517-860f0239-db3f-40e6-bdfe-9903f40bcfcc.png#averageHue=%23292e36&clientId=uf9bdc17f-df9c-4&from=paste&height=266&id=u11c75b32&originHeight=485&originWidth=390&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=31083&status=done&style=none&taskId=u8b40d080-874d-4cb6-bb4c-7c0a84f7bd6&title=&width=214.28572214566773)
##### Directory introduction

1. `normal_process_log` directory: saves normal case sets
2. `normal_cluster` directory: saves the edge vector information of normal cases
3. `process_model` directory: saves normal mode
4. `model_evaluation` directory: saves the quality evaluation results of normal mode (no clustering)
5. `cluster_model_evaluation` directory: saves the quality evaluation results of normal mode (clustering)
6. `transition_freq.py` directory: saves typical feature information extracted in normal mode, that is, high-frequency activity changes
##### Step 1: Extract normal case set

1. `normal_event_log.py`
   1. Enter: `../ProcessMining/scene_process_log` directory
   2. Output: `normal_process_log` directory
   3. Function: Eliminate control flow anomalies and semantic anomalies to obtain a normal case set
##### Step 2: Construct normal mode (no clustering)

1. `process_discovery.py`
   1. Input: `normal_process_log` directory
   2. Output:
      1. Model files: `petri_net` and `bpmn` subdirectories in the `process_model` directory
      2. Model evaluation file: `model_evaluation` directory
   3. Function: case set **not clustered**, mining process model
##### Step 3: Construct normal mode (clustering)

1. `normal_trace_cluster.py`
   1. Input: `normal_process_log` directory
   2. Output: `normal_cluster` directory
   3. Function: Count the number of occurrences of edge vectors in each case. For example: Case <A,B,C> corresponds to two edge vectors A→B, B→C
2. `process_discovery_cluster.py`
   1. Input: `normal_process_log` directory, `normal_cluster` directory
   2. Output:
      1. Model files: `petri_net` and `bpmn` subdirectories in the `process_model` directory
      2. Model evaluation file: `cluster_model_evaluation` directory, pay attention to the difference between the above non-clustering saving paths
   3. Function: case set ** clustering **, mining process model
##### Step 4: Extract typical features of the normal model

1. `transition_freq.py`
   1. Input: `normal_cluster` directory
   2. Output:
      1. Side frequency information: `transition_freq` directory
      2. Typical characteristics: `summary/transiton_percent.xls` file
   3. Function:
      1. Statistical side frequency information
      2. Extract typical features of the normal model (side frequency set exceeding the minimum thresh

#### Kappa
##### Module function description
Use Kappa to calculate the consistency of two people’s classification results of abnormal root causes

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1980167/1685173943057-069001ac-ca59-4468-8ed8-fd584059514a.png#averageHue=%23272c34&clientId=uf9bdc17f-df9c-4&from=paste&height=95&id=uaa45f908&originHeight=173&originWidth=393&originalType=binary&ratio=1.2999999523162842&rotation=0&showTitle=false&size=9175&status=done&style=none&taskId=u33b6c992-bc58-4297-b72a-b41b000f63f&title=&width=215.93407385448057)
##### Directory Description

1. `anomaly_pr` directory: process anomaly PR identification results
2. `output` directory: save experimental result data
##### Script Description

1. `kappa_semantic_anomaly.py` calculates the Kappa coefficient