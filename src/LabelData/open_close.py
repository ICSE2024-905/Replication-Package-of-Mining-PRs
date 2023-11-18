import pandas as pd
import json
from datetime import timedelta
from LabelData.Config import *
from utils.pr_self_utils import cal_pr_subtype, get_user_info_who_close_pr
from utils.url_utils import get_user_email


'''
Feature: The last reviewer gave it a pass, but the PR was still closed (and there was no PR tag, and the PR tag is also an explanation)
Points that can be improved:
1. Have you considered the situation where the PR creator actively closes the PR (for some reason, the PR creator does not want to merge?)
2. If you see a situation that occurs frequently (such as: zookeeper-1597), the project maintainer applies the current changes through another commit after closing the PR (the current PR is referenced in the commit message). If so, it needs to be updated. timeline-api, add reference event
3. Check whether there is a corresponding Comment (IssueComment with the same time) when ClosePR, and explain the reason for closing in the Comment.
'''
def open_close(repo: str, scene: str):
    anomaly_pr = []
    input_path = f"{CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    if 'OpenPR_ClosePR' not in df.columns:
        return anomaly_pr
    log_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    df_log = pd.read_csv(log_path, parse_dates=['time:timestamp'])
    df_check = df.loc[(df['OpenPR_ClosePR'] > 0) & (df['repo'] == repo)]
    for index, row in df_check.iterrows():
        pr_number = int(row['pr_number'])
        group = df_log.loc[df_log['case:concept:name'] == pr_number]

        df_open = group.loc[group['concept:name'] == 'OpenPR']
        contributor_name = df_open['people'].iloc[0]
        # contributor_email = get_user_email(contributor_name)

        df_close = group.loc[group['concept:name'] == 'ClosePR']
        maintainer_name = df_close['people'].iloc[-1]
        # description = json.loads(df_close['description'].iloc[-1])
        # maintainer_name, maintainer_email = get_user_info_who_close_pr(person, description)

        pr_type = 1 if contributor_name == maintainer_name else 2

        pr_subtype, explain = cal_pr_subtype(repo, pr_number, group, maintainer_name)

        anomaly_pr.append([repo, pr_number, pr_type, pr_subtype, explain
                           # contributor_name, contributor_email,
                           # maintainer_name, maintainer_email
                           ])
    return anomaly_pr


def auto_analysis():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    anomaly_pr = []
    for pro in projects:
        repo = pro.split('/')[1]
        result1 = open_close(repo, "fork_close")
        result2 = open_close(repo, "unfork_close")
        anomaly_pr.extend(result1)
        anomaly_pr.extend(result2)
        print(f"{repo} process done")
    # 保存为文件
    df_file = pd.DataFrame(data=anomaly_pr, columns=['repo', 'pr_number', 'pr_type', 'pr_subtype', 'explain'
                                                     # 'contributor_name', 'contributor_email',
                                                     # 'maintainer_name', 'maintainer_email'
                                                     ])
    output_path = f"{ANOMALY_PR_DIR}/open_close.xls"
    df_file.to_excel(output_path, index=False, header=True, encoding='utf-8-sig')


if __name__ == '__main__':
    auto_analysis()
