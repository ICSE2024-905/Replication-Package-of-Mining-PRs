from utils.file_utils import create_dir_if_not_exist

SEMANTIC_TYPE = ['obsolete', 'conflict', 'superseded', 'duplicate', 'superfluous', 'deferred', 'tests failed',
                 'incorrect implementation', 'merged', 'low priority', 'mistake', 'invalid', 'unknown']

ANOMALY_PR_PATH = "anomaly_pr"
ANOMALY_PR_MA_PATH = ANOMALY_PR_PATH + "/anomaly_pr_ma"
ANOMALY_PR_YANG_PATH = ANOMALY_PR_PATH + "/anomaly_pr_yang"
ANOMALY_PR_MERGE_PATH = ANOMALY_PR_PATH + "/anomaly_pr_merge"

OUTPUT_PATH = "output"

create_dir_if_not_exist(OUTPUT_PATH)

