import pandas as pd
import json
from typing import List
from TOPSIS.Config import *
from utils.mysql_utils import select_all
from utils.time_utils import cal_time_delta_minutes
from utils.pr_self_utils import get_pr_attributes
from utils.math_utils import cal_mean


'''

Function: Calculate string length
'''
def cal_str_length(s: str):
    if not pd.isna(s):
        return len(s.split())
    return 0


'''

Function: Extract all review-related information from the repo_self table
'''
def cal_avg_review_comment_length(repo: str, people: str, involved_pr: List):
    table = f"{repo.replace('-', '_')}_self"
    sql = f"select * from `{table}` where pr_number in ({','.join(involved_pr)})"
    data = select_all(sql)

    review_comment_length_list = []
    df = pd.DataFrame(data)
    for index, row in df.iterrows():
        pr_number = row['pr_number']
        review_comments_content = row['review_comments_content']
        for review in json.loads(review_comments_content):
            reviewer = review['user']['login'] if not pd.isna(review['user']) else None
            review_comment = review['body']
            if reviewer == people:
                length = cal_str_length(review_comment)
                review_comment_length_list.append(length)
    avg_review_comment_length = cal_mean(review_comment_length_list)
    return avg_review_comment_length


'''
Function: Based on the incoming review activities, determine whether to agree to merge
'''
def is_approve(activity: str):
    if activity == 'ReviewApproved':
        return 1
    elif activity == 'ReviewRejected' or activity == 'ReviewComment':
        return 0
    raise Exception("invalid param, activity should be Union['ReviewApproved', 'ReviewRejected', 'ReviewComment']")


'''
Function: Calculate each reviewer's review pass rate, first review response time, and total number of reviews
'''
def cal_review_approve_rate(repo: str, people: str, involved_pr: List):
    input_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
    involved_pr = [int(x) for x in involved_pr]
    review_events = ['ReviewApproved', 'ReviewRejected', 'ReviewComment']
    df = pd.read_csv(input_path, parse_dates=['time:timestamp'])
    df = df.loc[df['case:concept:name'].isin(involved_pr)
                & df['concept:name'].isin(review_events)
                & (df['people'] == people)]
    df['IsApprove'] = df['concept:name'].apply(lambda x: is_approve(x))
    approve_rate = df['IsApprove'].sum() / df.shape[0]
    first_response_time_list = []
    for pr_number, group in df.groupby('case:concept:name'):
        pr_attributes = get_pr_attributes(repo, pr_number)
        pr_open_time = pr_attributes['created_at']
        group.sort_values(by='time:timestamp', inplace=True)
        row = group.iloc[0]
        first_response_time = cal_time_delta_minutes(pr_open_time, row['time:timestamp'])
        first_response_time_list.append(first_response_time)
    avg_first_response_time = cal_mean(first_response_time_list)
    review_num = df.shape[0]

    return approve_rate, avg_first_response_time, review_num


'''
Function: Calculate the relevant indicators of a single review authority change person (maintainer)
'''
def cal_reviewer_feature_for_people(repo: str, people: str, involved_pr: List):
    avg_review_comment_length = cal_avg_review_comment_length(repo, people, involved_pr)

    approve_rate, avg_first_response_time, review_num = cal_review_approve_rate(repo, people, involved_pr)

    pr_num = len(involved_pr)

    feature = [people, pr_num, review_num, avg_review_comment_length, avg_first_response_time, approve_rate]
    return feature


'''
Function: Calculate the characteristics of all review permission changers in a single project within a period of time after obtaining reviewer permissions
'''
def cal_reviewer_feature_for_repo(repo: str):
    reviewer_feature = []
    input_path = f"{ROLE_CHANGE_DIR}/{repo}_role_change.csv"
    df_role = pd.read_csv(input_path, parse_dates=['change_role_time'])
    df_role = df_role.loc[df_role['change_role'] == 'Reviewer']
    df_role.reset_index(drop=True, inplace=True)
    for index, row in df_role.iterrows():
        print(f"{index+1}/{df_role.shape[0]} {row['people']} begin")
        people = row['people']
        involved_pr_str = row['involved_pr_after_permission_change']
        involved_pr = involved_pr_str.split("#") if not pd.isna(involved_pr_str) else []
        feature = cal_reviewer_feature_for_people(repo, people, involved_pr)
        if len(feature) == 0:
            continue
        reviewer_feature.append(feature)

    columns = ['people', 'pr_num', 'review_num', 'avg_review_comment_length', 'avg_review_response_time', 'approve_rate']
    df_file = pd.DataFrame(data=reviewer_feature, columns=columns)
    output_path = f"{FEATURE_DIR}/{repo}_reviewer_feature.csv"
    df_file.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


'''
Function: Calculate the characteristics of all review permission changers in all projects within a period of time after obtaining reviewer permissions
'''
def cal_reviewer_feature():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in projects:
        repo = pro.split('/')[1]
        cal_reviewer_feature_for_people(repo)
        print(f"repo#{repo} process done")


if __name__ == '__main__':
    cal_reviewer_feature()