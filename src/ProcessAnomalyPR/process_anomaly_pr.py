import pandas as pd
from ProcessAnomalyPR.Config import *


'''
Feature: Merge control flow/semantic exception PR
'''
def process_anomaly_pr():
    semantic_anomaly_pr_path = f"{PROCESS_ANOMALY_PR_DIR}/semantic_anomaly_pr.xls"
    df_semantic = pd.read_excel(semantic_anomaly_pr_path)
    df_semantic['semantic_anomaly'] = 1

    control_flow_anomaly_pr_path = f"{PROCESS_ANOMALY_PR_DIR}/control_flow_anomaly_pr.xls"
    df_control = pd.read_excel(control_flow_anomaly_pr_path)
    df_control['control_flow_anomaly'] = 1
    df_control = df_control[['case_id', 'control_flow_anomaly']]
    df_merge = pd.merge(df_semantic, df_control, how='outer', on='case_id')

    alignment_path = f"{ALIGNMENTS_DIR}/alignments_total_result.csv"
    df_alignment = pd.read_csv(alignment_path)
    df_alignment = df_alignment[['case_id', 'fitness', 'scene']]
    df_merge = pd.merge(df_merge, df_alignment, how='left', on='case_id')

    output_path = f"{PROCESS_ANOMALY_PR_DIR}/process_anomaly_pr.xls"
    df_merge.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    process_anomaly_pr()
