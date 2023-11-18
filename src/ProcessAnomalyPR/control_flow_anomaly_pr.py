import pandas as pd
from ProcessAnomalyPR.Config import *


'''

Function: Filter out abnormal control flow PRs based on thresholds
'''
def detect_control_flow_anomaly_pr(threshold):
    df_anomaly = pd.DataFrame()
    for scene in PR_TYPES:
        input_path = f"{ALIGNMENTS_DIR}/test_data/{scene}_alignments.csv"
        df = pd.read_csv(input_path)
        df['scene'] = scene
        df_filter = df.loc[df['fitness'] < threshold]

        variant_path = f"../ProcessMining/log_variant/{scene}_log_variant.csv"
        df_variant = pd.read_csv(variant_path)
        df_merge = pd.merge(df_filter, df_variant, how='left', on='case_id')

        df_anomaly = pd.concat([df_anomaly, df_merge], ignore_index=True)

    output_path = f"{PROCESS_ANOMALY_PR_DIR}/control_flow_anomaly_pr.xls"
    df_anomaly.to_excel(output_path, index=False, header=True)


'''
Function: formatted output alignment information
'''
def check_alignment(case_id):
    def parse_str(s):
        import re
        pattern = re.compile(r'\(.*?\)')
        result = pattern.findall(s)
        for r in result:
            r = r.replace("'", "")
            pair = r[1:-1].split(",")
            print('{:15}'.format(pair[0]) + " " + '{:15}'.format(pair[1]))
    input_path = f"{PROCESS_ANOMALY_PR_DIR}/control_flow_anomaly_pr.xls"
    df = pd.read_excel(input_path)
    case = df.loc[df['case_id'] == case_id]
    if case.shape[0] == 0:
        print(f"{case_id} No corresponding alignment information found")
        return
    alignment = case['alignment'].iloc[0]

    parse_str(alignment)


if __name__ == '__main__':
    # detect_control_flow_anomaly_pr(0.6)

    check_alignment("tensorflow#49562")

