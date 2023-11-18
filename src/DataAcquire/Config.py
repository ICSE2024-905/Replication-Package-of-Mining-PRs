from utils.file_utils import create_dir_if_not_exist

DAYS_OFFSET = 90
PR_TYPES = ["fork_merge", "fork_close", "unfork_merge", "unfork_close"]

# Other module directory paths
PROCESS_LOG_DIR = "../ProcessMining/process_log"

# Current module directory path
EVENT_LOG_DIR = "event_log"
ROLE_CHANGE_DIR = "role_change"

create_dir_if_not_exist(EVENT_LOG_DIR)
create_dir_if_not_exist(ROLE_CHANGE_DIR)

