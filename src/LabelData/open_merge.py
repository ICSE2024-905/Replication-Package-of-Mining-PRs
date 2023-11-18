import pandas as pd
from LabelData.Config import *
from utils.url_utils import get_user_email


'''
Function: PR is merged directly after it is opened
'''
def open_merge(repo: str, scene: str):
    anomaly_pr = []
    input_path = f"{CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    if 'OpenPR_MergePR' not in df.columns:
        return anomaly_pr
    log_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    df_log = pd.read_csv(log_path, parse_dates=['time:timestamp'])
    df_check = df.loc[(df['OpenPR_MergePR'] > 0) & (df['repo'] == repo)]
    for index, row in df_check.iterrows():
        pr_number = int(row['pr_number'])
        group = df_log.loc[df_log['case:concept:name'] == pr_number]

        df_open = group.loc[group['concept:name'] == 'OpenPR']
        contributor_name = df_open['people'].iloc[0]
        # contributor_email = get_user_email(contributor_name)

        df_merge = group.loc[group['concept:name'] == 'MergePR']
        maintainer_name = df_merge['people'].iloc[-1]
        # maintainer_email = get_user_email(maintainer_name)

        df_merge_comment = group.loc[(group['concept:name'] == 'IssueCommentSupplement')
                                     & (group['people'] == maintainer_name)]
        merge_comment = df_merge_comment['message'].iloc[0] if (df_merge_comment.shape[0] > 0) else None

        pr_type = 1 if contributor_name == maintainer_name else 2

        pr_subtype = 1 if df_merge_comment.shape[0] > 0 else 2

        anomaly_pr.append([repo, pr_number, pr_type, pr_subtype, merge_comment
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
        result1 = open_merge(repo, "fork_merge")
        result2 = open_merge(repo, "unfork_merge")
        anomaly_pr.extend(result1)
        anomaly_pr.extend(result2)
        print(f"{repo} process done")
    # 保存为文件
    df_file = pd.DataFrame(data=anomaly_pr, columns=['repo', 'pr_number', 'pr_type', 'pr_subtype', 'explain'
                                                     # 'contributor_name', 'contributor_email',
                                                     # 'maintainer_name', 'maintainer_email'
                                                     ])
    output_path = f"{ANOMALY_PR_DIR}/open_merge.xls"
    df_file.to_excel(output_path, index=False, header=True, encoding='utf-8-sig')


if __name__ == '__main__':
    auto_analysis()
