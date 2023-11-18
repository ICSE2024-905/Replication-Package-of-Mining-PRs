import pandas as pd
from TOPSIS.Config import *



def score_control_flow_anomaly_pr():
    def helper(fitness):
        if fitness < 0.12:
            return 5
        elif fitness < 0.24:
            return 4
        elif fitness < 0.36:
            return 3
        elif fitness < 0.48:
            return 2
        elif fitness < 0.60:
            return 1
    input_path = f"{PROCESS_ANOMALY_PR_DIR}/control_flow_anomaly_pr.xls"
    df = pd.read_excel(input_path)
    df = df[['case_id', 'fitness']]
    df['score'] = df['fitness'].apply(lambda x: helper(x))
    return df


def score_semantic_anomaly_pr():
    def helper(semantic_type, category):
        if semantic_type == 'no_reviewer_response_but_close':
            if category == 'merged':
                return 3
            elif category == 'unknown':
                return 2
            else:
                return 1
        elif semantic_type == 'review_approved_but_close':
            if category == 'merged':
                return 2
            elif category == 'unknown':
                return 3
            else:
                return 1
        elif semantic_type == 'no_reviewer_response_but_merge':
            return 4
        elif semantic_type == 'review_rejected_but_merge':
            return 5

    input_path = f"{PROCESS_ANOMALY_PR_DIR}/semantic_anomaly_pr.xls"
    df = pd.read_excel(input_path)
    df['case_id'] = df.apply(lambda x: str(x['repo']) + '#' + str(x['pr_number']), axis=1)
    df['score'] = df.apply(lambda x: helper(x['semantic_type'], x['category']), axis=1)
    return df




def cal_semantic_anomaly_score(role, semantic_anomaly_pr_list, df_semantic_score):
    semantic_anomaly_score = 0
    if len(semantic_anomaly_pr_list) > 0:
        semantic_anomaly_score = df_semantic_score.loc[df_semantic_score['case_id'].isin(semantic_anomaly_pr_list)]['score'].sum()
    if role == 'Maintainer':
        pass
    elif role == 'Reviewer':
        semantic_anomaly_score = semantic_anomaly_score / 2
    return semantic_anomaly_score


def cal_control_flow_anomaly_score(role, control_flow_anomaly_pr_list, df_control_flow_score):
    control_flow_anomaly_score = 0
    if len(control_flow_anomaly_pr_list) > 0:
        control_flow_anomaly_score = df_control_flow_score.loc[df_control_flow_score['case_id'].isin(control_flow_anomaly_pr_list)]['score'].sum()
    return control_flow_anomaly_score


def cal_pr_list(repo, pr_str):
    pr_list = pr_str.split('#') if not pd.isna(pr_str) else []
    case_id_list = [f"{repo}#{pr}" for pr in pr_list]
    return case_id_list


def score_behavior_risk():
    df_control_flow_score = score_control_flow_anomaly_pr()
    df_semantic_score = score_semantic_anomaly_pr()

    input_path = f"{SUMMARY_DIR}/role_change_info.xls"
    df_role = pd.read_excel(input_path)
    df_role['semantic_anomaly_pr'] = df_role['semantic_anomaly_pr'].astype(str)
    for index, row in df_role.iterrows():
        role = row['change_role']

        control_flow_anomaly_pr_list = cal_pr_list(row['repo'], row['control_flow_anomaly_pr'])
        control_flow_anomaly_score = cal_control_flow_anomaly_score(role, control_flow_anomaly_pr_list, df_control_flow_score)
        df_role.loc[index, 'control_flow_anomaly_score'] = control_flow_anomaly_score

        semantic_anomaly_pr_list = cal_pr_list(row['repo'], row['semantic_anomaly_pr'])
        semantic_anomaly_score = cal_semantic_anomaly_score(role, semantic_anomaly_pr_list, df_semantic_score)
        df_role.loc[index, 'semantic_anomaly_score'] = semantic_anomaly_score

        df_role.loc[index, 'total_score'] = control_flow_anomaly_score + semantic_anomaly_score

    output_path = f"{SUMMARY_DIR}/score_behavior_risk.xls"
    df_role.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    score_behavior_risk()