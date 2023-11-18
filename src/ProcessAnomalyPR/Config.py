from utils.file_utils import create_dir_if_not_exist

PR_TYPES = ["fork_merge", "fork_close", "unfork_merge", "unfork_close"]

ALIGNMENTS_DIR = f"../ProcessMining/conformance_check/alignments"

PROCESS_ANOMALY_PR_DIR = "process_anomaly_pr"
SUMMARY_DIR = "summary"
FIGURE_DIR = "figure"
LOG_VARIANTS_DIR = "log_variant"

create_dir_if_not_exist(PROCESS_ANOMALY_PR_DIR)
create_dir_if_not_exist(SUMMARY_DIR)
create_dir_if_not_exist(FIGURE_DIR)
create_dir_if_not_exist(LOG_VARIANTS_DIR)