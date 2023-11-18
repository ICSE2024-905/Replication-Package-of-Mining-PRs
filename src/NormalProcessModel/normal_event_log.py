import pandas as pd
from NormalProcessModel.Config import *
from utils.log_utils import log_info, get_event_log_from_file


def extra_normal_event_log():
    anomaly_pr_path = f"../ProcessAnomalyPR/process_anomaly_pr/process_anomaly_pr.xls"
    df_anomaly = pd.read_excel(anomaly_pr_path)

    for scene in PR_TYPES:
        log_path = f"{SCENE_PROCESS_LOG_DIR}/{scene}_process_log.csv"
        df_log = get_event_log_from_file(log_path)
        log_info(df_log)

        anomaly_case_ids = df_anomaly.loc[df_anomaly['scene'] == scene]['case_id'].tolist()
        df_normal = df_log.loc[~df_log['case:concept:name'].isin(anomaly_case_ids)]
        log_info(df_normal)

        output_path = f"{NORMAL_PROCESS_LOG_DIR}/{scene}_process_log.csv"
        df_normal.to_csv(output_path, index=False, header=True)

        print(f"{scene} process done")


if __name__ == '__main__':
    extra_normal_event_log()