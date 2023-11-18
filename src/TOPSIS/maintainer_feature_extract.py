import pandas as pd
from typing import List
from TOPSIS.Config import *
from utils.time_utils import cal_time_delta_minutes, cal_time_interval
from utils.pr_self_utils import get_pr_attributes

'''
Function: Based on the incoming activity, determine whether it is a merged PR
'''
def cal_pr_state(activity: str):
    if activity == 'MergePR':
        return 1
    elif activity == 'ClosePR':
        return 0
    raise Exception("invalid param, activity should be Union['MergePR', 'ClosePR']")


'''
Function: Extract maintainer related data
'''
def cal_maintainer_pr_data(repo: str, people: str, involved_pr: List):
    involved_pr = [int(x) for x in involved_pr]
    input_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
    df = pd.read_csv(input_path, parse_dates=['time:timestamp'])
    df = df.loc[df['case:concept:name'].isin(involved_pr)]

    maintainer_pr_data = []
    for pr_number, group in df.groupby('case:concept:name'):
        pr_attribute = get_pr_attributes(repo, pr_number)
        pr_open_time = pr_attribute['created_at']
        pr_close_time = pr_attribute['closed_at']

        pr_state = pr_attribute['merged']

        operate_time = pr_close_time

        review_event = ['ReviewApproved', 'ReviewRejected', 'ReviewComment']
        df_review = group.loc[group['concept:name'].isin(review_event)]
        pr_reviewer_num = len(df_review['people'].unique()) if df_review.shape[0] > 0 else 0

        response_time = cal_time_delta_minutes(pr_open_time, pr_close_time)

        maintainer_pr_data.append([people, pr_number, pr_state, pr_reviewer_num, response_time, operate_time])

    return maintainer_pr_data


'''

Function: Calculate relevant indicators of a single maintenance authority change person (maintainer)
'''
def cal_maintainer_feature_for_people(repo: str, people: str, involved_pr: List):
    maintainer_pr_data = cal_maintainer_pr_data(repo, people, involved_pr)

    df = pd.DataFrame(data=maintainer_pr_data, columns=['people', 'pr_number', 'pr_state', 'pr_reviewer_num',
                                                        'response_time', 'operate_time'])
    pr_num = df.shape[0]
    merge_rate = df['pr_state'].sum() / pr_num
    avg_assign_reviewer_num = df['pr_reviewer_num'].sum() / pr_num
    avg_response_time = df['response_time'].sum() / pr_num
    avg_response_interval = cal_time_interval(df['operate_time'].tolist())
    df['has_review'] = df['pr_reviewer_num'].apply(lambda x: 1 if x > 0 else 0)
    review_rate = df['has_review'].sum() / pr_num

    feature = [people, pr_num, merge_rate, avg_assign_reviewer_num, avg_response_time, avg_response_interval, review_rate]

    return feature


'''
Function: Calculate the characteristics of all maintenance permission changers in a single project within a period of time after obtaining maintainer permissions
'''
def cal_maintainer_feature_for_repo(repo: str):
    maintainer_feature = []
    input_path = f"{ROLE_CHANGE_DIR}/{repo}_role_change.csv"
    df_role = pd.read_csv(input_path, parse_dates=['change_role_time'])
    df_role = df_role.loc[df_role['change_role'] == 'Maintainer']
    df_role.reset_index(drop=True, inplace=True)
    for index, row in df_role.iterrows():
        print(f"{index+1}/{df_role.shape[0]} {row['people']} begin")
        people = row['people']
        involved_pr_str = row['involved_pr_after_permission_change']
        involved_pr = involved_pr_str.split("#") if not pd.isna(involved_pr_str) else []
        feature = cal_maintainer_feature_for_people(repo, people, involved_pr)
        if len(feature) == 0:
            continue
        maintainer_feature.append(feature)

    columns = ['people', 'pr_num', 'merge_rate', 'avg_assign_reviewer_num', 'avg_response_time','avg_response_interval', 'review_rate']
    df_file = pd.DataFrame(data=maintainer_feature, columns=columns)
    output_path = f"{FEATURE_DIR}/{repo}_maintainer_feature.csv"
    df_file.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


'''
Function: Calculate the characteristics of all maintenance permission changers in all projects within a period of time after obtaining maintainer permissions
'''
def cal_maintainer_feature():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in projects:
        repo = pro.split('/')[1]
        cal_maintainer_feature_for_repo(repo)
        print(f"repo#{repo} process done")


if __name__ == '__main__':
    cal_maintainer_feature()