from utils.file_utils import create_dir_if_not_exist

ANOMALY_PR_RATE_THRESHOLD = 0.2

# 其他模块目录路径
ROLE_CHANGE_DIR = "../DataAcquire/role_change"
ANOMALY_PR_DIR = "../ProcessAnomalyPR/process_anomaly_pr"
MULTI_MODEL_VOTE_DIR = "../AnomalyDetectionScene/output/multi_model_vote"


# 本模块目录路径
DATA_ANOMALY_DIR = "data_anomaly"
PROCESS_ANOMALY_DIR = "process_anomaly"
MERGE_ANOMALY_DIR = "merge_anomaly"
SUMMARY_DIR = "summary"
FIGURE_DIR = "figure"

create_dir_if_not_exist(DATA_ANOMALY_DIR)
create_dir_if_not_exist(PROCESS_ANOMALY_DIR)
create_dir_if_not_exist(MERGE_ANOMALY_DIR)
create_dir_if_not_exist(SUMMARY_DIR)
create_dir_if_not_exist(FIGURE_DIR)