import pandas as pd
from ProcessAnomalyPR.Config import *


'''

Function: Statistics on the distribution of the number of abnormal control flow PRs in the project
'''
def repo_control_flow_anomaly_pr_num(projects):
    input_path = f"{PROCESS_ANOMALY_PR_DIR}/control_flow_anomaly_pr.xls"
    df = pd.read_excel(input_path)
    df['repo'] = df['case_id'].apply(lambda x: x.split("#")[0])
    df['pr_number'] = df['case_id'].apply(lambda x: x.split("#")[1])

    datas = []
    for pro in projects:
        repo = pro.split("/")[1]
        df_repo = df.loc[df['repo'] == repo]
        total_control_flow_anomaly_pr = df_repo.shape[0]
        repo_anomaly_pr = {'repo': repo, 'total_control_flow_anomaly_pr': total_control_flow_anomaly_pr}
        for index, row in df_repo.iterrows():
            labels = row['category'].split(", ")
            for label in labels:
                if label in repo_anomaly_pr:
                    repo_anomaly_pr[label] += 1
                else:
                    repo_anomaly_pr[label] = 1
        datas.append(repo_anomaly_pr)

    output_path = f"{SUMMARY_DIR}/repo_control_flow_anomaly_pr_num.xls"
    df_file = pd.DataFrame(data=datas)
    df_file.fillna(0, inplace=True)
    df_file.to_excel(output_path, index=False, header=True)


'''
Function: Statistics of the distribution of the number of semantic anomaly PRs in projects
'''
def repo_semantic_anomaly_pr_num(projects, semantic_anomaly_types):
    input_path = f"{PROCESS_ANOMALY_PR_DIR}/semantic_anomaly_pr.xls"
    df = pd.read_excel(input_path)
    df['repo'] = df['case_id'].apply(lambda x: x.split("#")[0])
    df.fillna(0, inplace=True)
    datas = []
    for pro in projects:
        repo = pro.split("/")[1]
        repo_anomaly_pr = {'repo': repo}
        for anomaly_type in semantic_anomaly_types:
            df_filter = df.loc[(df['repo'] == repo) & (df[anomaly_type] > 0)]
            repo_anomaly_pr[anomaly_type] = df_filter.shape[0]
        datas.append(repo_anomaly_pr)

    df_file = pd.DataFrame(data=datas)
    output_path = f"{SUMMARY_DIR}/repo_semantic_anomaly_pr_num.xls"
    df_file.to_excel(output_path, index=False, header=True)


'''
Function: In statistical semantic exception PR, the reason why PR is closed
'''
def reason_why_pr_closed():
    input_path1 = f"../LabelData/anomaly_pr_yang/no_reviewer_response_but_close.xls"
    input_path2 = f"../LabelData/anomaly_pr_yang/review_approved_but_close.xls"
    df1 = pd.read_excel(input_path1)
    df2 = pd.read_excel(input_path2)
    df1['category'] = df1['reason'].apply(lambda x: x.split("-")[0])
    df2['category'] = df2['reason'].apply(lambda x: x.split("-")[0])
    close_type = ['conflict', 'deferred', 'duplicate', 'incorrect implementation', 'merged', 'obsolete',
                  'superfluous', 'superseded', 'tests failed', 'low priority', 'mistake', 'invalid', 'unknown']
    datas = []
    for t in close_type:
        type_num_1 = df1.loc[df1['category'] == t].shape[0]
        type_num_2 = df2.loc[df2['category'] == t].shape[0]
        datas.append([t, type_num_1, type_num_2])
    output_path = f"{SUMMARY_DIR}/reason_why_pr_closed.xls"
    df_file = pd.DataFrame(data=datas, columns=['close_reason', 'no_reviewer_response_but_close', 'review_approved_but_close'])
    df_file.to_excel(output_path, index=False, header=True)


'''
Function: In the PR of statistical semantic anomalies, the person role information of the PR is incorporated
'''
def role_relation_in_merged_pr():
    datas = []
    for t in semantic_anomaly_types:
        input_path = f"../LabelData/anomaly_pr/{t}.xls"
        df = pd.read_excel(input_path)
        maintainer_is_contributor = df.loc[df['pr_subtype'] == 1].shape[0]
        maintainer_is_reviewer = df.loc[df['pr_subtype'] == 2].shape[0]
        maintainer_is_others = df.loc[df['pr_subtype'] == 3].shape[0]
        datas.append({
            'semantic_anomaly_type': t,
            'maintainer_is_contributor': maintainer_is_contributor,
            'maintainer_is_reviewer': maintainer_is_reviewer,
            'maintainer_is_others': maintainer_is_others
        })

    df_file = pd.DataFrame(data=datas)
    output_path = f"{SUMMARY_DIR}/role_relation_in_merged_pr.xls"
    df_file.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    semantic_anomaly_types = ["no_reviewer_response_but_close", "no_reviewer_response_but_merge",
                     "review_approved_but_close", "review_rejected_but_merge"]

    repo_control_flow_anomaly_pr_num(projects)
    # repo_semantic_anomaly_pr_num(projects, semantic_anomaly_types)

    # reason_why_pr_closed()
    # role_relation_in_merged_pr()