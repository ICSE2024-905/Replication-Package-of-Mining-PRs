from utils.file_utils import create_dir_if_not_exist

PR_TYPES = ["fork_merge", "fork_close", "unfork_merge", "unfork_close"]

EVENT_LOG_DIR = "../DataAcquire/event_log"
SCENE_PROCESS_LOG_DIR = "../ProcessMining/scene_process_log"
NORMAL_PROCESS_LOG_DIR = "../ProcessMining/normal_process_log"

ANOMALY_PR_DIR = "anomaly_pr"
CLUSTER_DIR = "cluster"
NORMAL_CLUSTER_DIR = "normal_cluster"
EDGE_FREQ_DIR = "edge_freq"

create_dir_if_not_exist(ANOMALY_PR_DIR)
create_dir_if_not_exist(CLUSTER_DIR)
create_dir_if_not_exist(NORMAL_CLUSTER_DIR)
create_dir_if_not_exist(EDGE_FREQ_DIR)