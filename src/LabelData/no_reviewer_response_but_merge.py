import pandas as pd
from utils.pr_self_utils import get_pr_requested_reviewer_list
from LabelData.Config import *
from utils.url_utils import get_user_email

'''
Function: Abnormal PR identification: The PR is requested to be reviewed and all reviewers fail to respond in time/the response times out, the PR is merged.
To be improved: Although requested_reviewer did not respond, the situation where other reviewers gave review opinions has not been considered yet.
'''
def no_reviewer_response_but_merge(repo: str, scene: str):
    anomaly_pr = []
    input_path = f"{CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    if 'ReviewRequested_MergePR' not in df.columns:
        return anomaly_pr
    log_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    df_log = pd.read_csv(log_path)
    df_check = df.loc[(df['repo'] == repo) & (df['ReviewRequested_MergePR'] > 0)]
    for index, row in df_check.iterrows():
        pr_number = int(row['pr_number'])
        group = df_log.loc[df_log['case:concept:name'] == pr_number]

        df_open = group.loc[group['concept:name'] == 'OpenPR']
        contributor_name = df_open['people'].iloc[0]
        contributor_email = get_user_email(contributor_name)

        requested_reviewer_name_list = get_pr_requested_reviewer_list(repo, pr_number)
        requested_reviewer_email_list = [get_user_email(username) for username in requested_reviewer_name_list]

        df_merge = group.loc[group['concept:name'] == 'MergePR']
        maintainer_name = df_merge['people'].iloc[-1]
        maintainer_email = get_user_email(maintainer_name)

        df_merge_comment = group.loc[(group['concept:name'] == 'IssueCommentSupplement')
                                     & (group['people'] == maintainer_name)]
        merge_comment = df_merge_comment['message'].iloc[0] if (df_merge_comment.shape[0] > 0) else None

        pr_type = 0
        if maintainer_name == contributor_name:
            pr_type = 1
        elif maintainer_name in requested_reviewer_name_list:
            pr_type = 2
        else:
            pr_type = 3

        pr_subtype = 1 if df_merge_comment.shape[0] > 0 else 2

        anomaly_pr.append([repo, pr_number, pr_type, pr_subtype, merge_comment,
                           contributor_name, contributor_email,
                           str(requested_reviewer_name_list), str(requested_reviewer_email_list),
                           maintainer_name, maintainer_email])
    return anomaly_pr


def auto_analysis():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    anomaly_pr = []
    for pro in projects:
        repo = pro.split('/')[1]
        print(f"{repo} begin")
        result1 = no_reviewer_response_but_merge(repo, "fork_merge")
        result2 = no_reviewer_response_but_merge(repo, "unfork_merge")
        anomaly_pr.extend(result1)
        anomaly_pr.extend(result2)
        print()
    df_file = pd.DataFrame(data=anomaly_pr, columns=[
                           'repo', 'pr_number', 'pr_type', 'pr_subtype', 'explain',
                           'contributor_name', 'contributor_email',
                           'requested_reviewer_name', 'requested_reviewer_email',
                           'maintainer_name', 'maintainer_email'])
    output_path = f"{ANOMALY_PR_DIR}/no_reviewer_response_but_merge.xls"
    df_file.to_excel(output_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == '__main__':
    auto_analysis()