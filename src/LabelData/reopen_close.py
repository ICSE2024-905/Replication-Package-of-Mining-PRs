import pandas as pd
import json
from datetime import timedelta
from LabelData.Config import *
from utils.url_utils import get_user_email, get_committer_info


'''

Function: Get ClosePR user information based on the description in the ClosePR event
'''
def get_user_info_who_close_pr(person, description_str):
    close_flag = False
    description = json.loads(description_str)
    if description['commit_url'] is not None:
        close_flag = True
    if close_flag:
        user_name, user_email = get_committer_info(description['commit_url'])
    else:
        user_name = person
        user_email = get_user_email(person)
    return user_name, user_email


'''
Feature: The last reviewer gave it a pass, but the PR was still closed (and there was no PR tag, and the PR tag is also an explanation)
Points that can be improved:
1. Have you considered the situation where the PR creator actively closes the PR (for some reason, the PR creator does not want to merge?)
2. If you see a situation that occurs frequently (such as: zookeeper-1597), the project maintainer applies the current changes through another commit after closing the PR (the current PR is referenced in the commit message). If so, it needs to be updated. timeline-api, add reference event
3. Check whether there is a corresponding Comment (IssueComment with the same time) when ClosePR, and explain the reason for closing in the Comment.
'''
def reopen_close(repo: str, scene: str):
    anomaly_pr = []
    input_path = f"{CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    if 'ReopenPR_ClosePR' not in df.columns:
        return anomaly_pr
    log_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    df_log = pd.read_csv(log_path, parse_dates=['time:timestamp'])
    df_check = df.loc[(df['ReopenPR_ClosePR'] > 0) & (df['repo'] == repo)]
    for index, row in df_check.iterrows():
        pr_number = int(row['pr_number'])
        group = df_log.loc[df_log['case:concept:name'] == pr_number]
        df_reopen = group.loc[group['concept:name'] == 'ReopenPR']
        user_name = df_reopen['people'].iloc[0]
        user_email = get_user_email(user_name)
        reopen_time = df_reopen['time:timestamp'].iloc[0]
        search_time = reopen_time - timedelta(seconds=3)
        df_reopen_comment = group.loc[(group['time:timestamp'] >= search_time)
                               & (group['concept:name'] == 'IssueComment')
                               & (group['people'] == user_name)]
        reopen_comment = df_reopen_comment['message'].iloc[0] if (df_reopen_comment.shape[0] > 0) else None
        df_close = group.loc[group['concept:name'] == 'ClosePR']
        person = df_close['people'].iloc[-1]
        description_str = df_close['description'].iloc[-1]
        maintainer_name, maintainer_email = get_user_info_who_close_pr(person, description_str)
        df_close_comment = group.loc[(group['concept:name'] == 'IssueCommentSupplement')
                                     & (group['people'] == maintainer_name)]
        close_comment = df_close_comment['message'].iloc[0] if (df_close_comment.shape[0] > 0) else None
        reopen_comment_flag = df_reopen_comment.shape[0] > 0
        close_comment_flag = df_close_comment.shape[0] > 0
        pr_type = 0
        if reopen_comment_flag or close_comment_flag:
            pr_type = 1
        else:
            pr_type = 2
        anomaly_pr.append([repo, pr_number, pr_type,
                           reopen_comment, user_name, user_email,
                           close_comment, maintainer_name, maintainer_email])
    return anomaly_pr


def auto_analysis():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    anomaly_pr = []
    for pro in projects:
        repo = pro.split('/')[1]
        result1 = reopen_close(repo, "fork_close")
        result2 = reopen_close(repo, "unfork_close")
        anomaly_pr.extend(result1)
        anomaly_pr.extend(result2)
        print(f"{repo} process done")
    df_file = pd.DataFrame(data=anomaly_pr, columns=['repo', 'pr_number', 'pr_type',
                                                     'reopen_comment', 'user_name', 'user_email',
                                                     'close_comment', 'maintainer_name', 'maintainer_email'])
    output_path = f"{ANOMALY_PR_DIR}/reopen_close.csv"
    df_file.to_csv(output_path, index=False, header=True, encoding='utf-8-sig')


if __name__ == '__main__':
    auto_analysis()
