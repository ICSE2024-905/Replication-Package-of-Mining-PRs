from utils.file_utils import create_dir_if_not_exist


PR_TYPES = ["fork_merge", "fork_close", "unfork_merge", "unfork_close"]

SCENE_PROCESS_LOG_DIR = "../ProcessMining/scene_process_log"

NORMAL_PROCESS_LOG_DIR = "normal_process_log"

PROCESS_MODEL_DIR = "process_model"
BPMN_DIR = f"{PROCESS_MODEL_DIR}/bpmn"
PETRI_NET_DIR = f"{PROCESS_MODEL_DIR}/petri_net"

MODEL_EVALUATION_DIR = f"model_evaluation"
CLUSTER_MODEL_EVALUATION_DIR = f"cluster_model_evaluation"

NORMAL_CLUSTER_DIR = "normal_cluster"

TRANSITION_FREQ_DIR = "transition_freq"

SUMMARY_DIR = "summary"


create_dir_if_not_exist(NORMAL_PROCESS_LOG_DIR)

create_dir_if_not_exist(PROCESS_MODEL_DIR)
create_dir_if_not_exist(BPMN_DIR)
create_dir_if_not_exist(PETRI_NET_DIR)

create_dir_if_not_exist(MODEL_EVALUATION_DIR)
create_dir_if_not_exist(CLUSTER_MODEL_EVALUATION_DIR)

create_dir_if_not_exist(NORMAL_CLUSTER_DIR)

create_dir_if_not_exist(TRANSITION_FREQ_DIR)

create_dir_if_not_exist(SUMMARY_DIR)
