from utils.file_utils import create_dir_if_not_exist

HIGH_RISK_THRESHOLD = 0.4

PROCESS_LOG_DIR = "../ProcessMining/process_log"
ROLE_CHANGE_DIR = "../DataAcquire/role_change"
PROCESS_ANOMALY_PR_DIR = "../ProcessAnomalyPR/process_anomaly_pr"

SUMMARY_DIR = "summary"
FIGURE_DIR = "figure"
FEATURE_DIR = "feature"

create_dir_if_not_exist(SUMMARY_DIR)
create_dir_if_not_exist(FIGURE_DIR)
create_dir_if_not_exist(FEATURE_DIR)