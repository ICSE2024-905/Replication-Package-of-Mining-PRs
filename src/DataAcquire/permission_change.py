import pandas as pd
import os
from datetime import datetime, timedelta
from utils.pr_self_utils import get_all_pr_number_between
from DataAcquire.Config import *


'''
Function: Filter out all change information that obtained reviewer permissions for the first time
'''
def cal_reviewer_change(df: pd.DataFrame):
    role_change = []
    df_reviewer = df.loc[df['concept:name'].isin(['ReviewApproved', 'ReviewRejected'])]
    for person, group in df_reviewer.groupby('people'):
        group.sort_values(by='time:timestamp', inplace=True)
        row = group.iloc[0]
        role_change.append([row['people'], row['case:concept:name'], row['time:timestamp'], 'Reviewer'])
    return role_change


'''
Function: Filter out all change information that obtained maintainer permissions for the first time
'''
def cal_maintainer_change(df: pd.DataFrame):
    role_change = []
    maintainer_info = []
    for pr_number, group in df.groupby("case:concept:name"):
        df_creator = group.loc[group['concept:name'] == 'OpenPR']
        df_closer = group.loc[group['concept:name'] == 'ClosePR']
        if df_creator.shape[0] == 0 or df_closer.shape[0] == 0:
            continue
        df_closer = df_closer.sort_values(by='time:timestamp')
        creator = df_creator.iloc[0]
        closer = df_closer.iloc[-1]
        if creator['people'] != closer['people']:
            maintainer_info.append([closer['people'], closer['case:concept:name'], closer['time:timestamp']])
    df_maintainer_1 = pd.DataFrame(data=maintainer_info, columns=['people', 'case:concept:name', 'time:timestamp'])

    df_maintainer_2 = df.loc[df['concept:name'] == 'MergePR']
    df_maintainer_2 = df_maintainer_2[['people', 'case:concept:name', 'time:timestamp']]

    df_maintainer = pd.concat([df_maintainer_1, df_maintainer_2], ignore_index=True)
    for person, group in df_maintainer.groupby('people'):
        group.sort_values(by='time:timestamp', inplace=True)
        row = group.iloc[0]
        role_change.append([row['people'], row['case:concept:name'], row['time:timestamp'], 'Maintainer'])

    return role_change


'''
Function: Filter out all change information that obtains committer permission for the first time
'''
def cal_committer_change(df: pd.DataFrame):
    role_change = []
    df_committer = df.loc[df['concept:name'].isin(['SubmitCommit', 'Revise', 'OpenPR'])]
    for person, group in df_committer.groupby('people'):
        group.sort_values(by='time:timestamp', inplace=True)
        row = group.iloc[0]
        role_change.append([row['people'], row['case:concept:name'], row['time:timestamp'], 'Committer'])
    return role_change


'''

Function: Automation of permission change identification process
'''
def cal_permission_change(repo: str):
    role_change = []

    input_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
    df = pd.read_csv(input_path, parse_dates=['time:timestamp'])

    reviewer_change = cal_reviewer_change(df)
    maintainer_change = cal_maintainer_change(df)
    # committer_change = cal_committer_change(df)
    role_change.extend(reviewer_change)
    role_change.extend(maintainer_change)
    # role_change.extend(committer_change)

    if len(role_change) == 0:
        print(f"{repo} don't detect any permission change")
        return

    output_path = f"{ROLE_CHANGE_DIR}/{repo}_role_change.csv"
    df_file = pd.DataFrame(data=role_change, columns=['people', 'change_pr_number', 'change_role_time', 'change_role'])
    df_file.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


'''
Function: Determine all PRs that a specific person participated in within a period of time after the permissions were changed (and the new permissions were used in these PRs)
'''
def cal_involved_pr(repo: str, person: str, change_pr_number: int, change_role_time: datetime, change_role: str):
    end_time = change_role_time + timedelta(days=DAYS_OFFSET)
    pr_number_list = get_all_pr_number_between(repo, change_role_time, end_time)

    role_info_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
    df = pd.read_csv(role_info_path, parse_dates=['time:timestamp'])
    pr_df = df.loc[(df['people'] == person) & df['case:concept:name'].isin(pr_number_list)]

    if change_role == 'Committer':
        pr_df = pr_df.loc[pr_df['concept:name'].isin(['SubmitCommit', 'Revise', 'OpenPR'])]
    elif change_role == 'Reviewer':
        pr_df = pr_df.loc[pr_df['concept:name'].isin(['ReviewApproved', 'ReviewRejected', 'ReviewComment'])]
    elif change_role == 'Maintainer':
        pr_df = pr_df.loc[pr_df['concept:name'].isin(['MergePR', 'ClosePR'])]
    else:
        print("Wrong character information")

    involved_pr_list = pr_df['case:concept:name'].unique().tolist()
    if change_pr_number not in involved_pr_list:
        involved_pr_list.insert(0, change_pr_number)
    return "#".join(str(x) for x in involved_pr_list)


'''
Function: Determine all persons whose permissions have changed in a warehouse, all PRs they participated in within a period of time after the permissions were changed, and use the new permissions in these PRs
'''
def add_involved_pr_after_permission_change(repo: str):
    role_change_path = f"{ROLE_CHANGE_DIR}/{repo}_role_change.csv"
    if not os.path.exists(role_change_path):
        print(f"{role_change_path} don't exist")
        return
    df_role_change = pd.read_csv(role_change_path, parse_dates=['change_role_time'])
    df_role_change['involved_pr_after_permission_change'] = df_role_change.apply(
        lambda x: cal_involved_pr(repo, x['people'], x['change_pr_number'], x['change_role_time'], x['change_role']),
        axis=1)
    df_role_change.to_csv(role_change_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in ['apache/zookeeper']:
        repo = pro.split('/')[1]
        cal_permission_change(repo)
        add_involved_pr_after_permission_change(repo)
        print(f"repo#{repo} process done")
