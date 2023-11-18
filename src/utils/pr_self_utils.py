import json
from utils.mysql_utils import select_one, select_all
from typing import Dict, List
from datetime import datetime

from utils.url_utils import get_committer_info, get_user_email


def get_pr_attributes(repo: str, pr_number: int) -> Dict:
    table = f"{repo.replace('-', '_')}_self"
    sql = f"select * from `{table}` where repo_name='{repo.replace('-', '_')}' and pr_number={pr_number}"
    data = select_one(sql)
    return data



def get_pr_labels(repo: str, pr_number: int):
    table = f"{repo.replace('-', '_')}_event_log"
    sql = f"select * from {table} where pr_number={pr_number} and activity='Labeled'"
    data = select_all(sql)
    labels = [x['message'] for x in data]
    return labels



def get_pr_requested_reviewer_list(repo: str, pr_number: int):
    table = f"{repo.replace('-', '_')}_event_log"
    sql = f"select * from {table} where pr_number={pr_number} and activity='ReviewRequested'"
    data = select_all(sql)
    requested_reviewer_list = set()
    for item in data:
        item_json = json.loads(item['description'])
        if item_json['requested_reviewer'] is not None:
            requested_reviewer = item_json['requested_reviewer']['login']
            requested_reviewer_list.add(requested_reviewer)
    return requested_reviewer_list



def get_all_pr_number_between(repo: str, start: datetime, end: datetime) -> List:
    start_time = start.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end.strftime('%Y-%m-%d %H:%M:%S')
    table = f"{repo.replace('-', '_')}_self"
    sql = f"select pr_number from `{table}` where created_at >= '{start_time}' and created_at < '{end_time}'"
    pr_list = select_all(sql)
    pr_number_list = [x['pr_number'] for x in pr_list]
    return pr_number_list



def get_pr_between(repo: str, start: datetime, end: datetime) -> List:
    start_time = start.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end.strftime('%Y-%m-%d %H:%M:%S')
    table = f"{repo.replace('-', '_')}_self"
    sql = f"select * from `{table}` where created_at >= '{start_time}' and created_at < '{end_time}'"
    pr_list = select_all(sql)
    return pr_list



def get_user_info_who_close_pr(person, description):
    # 是否属于通过命令行来应用PR(合入分支为默认分支)
    close_flag = False
    if description['commit_url'] is not None:
        close_flag = True
    # 如果是通过命令行来关闭PR，则通过commit_url获取用户信息
    if close_flag:
        user_name, user_email = get_committer_info(description['commit_url'])
    # 如果是在页面关闭PR，则通过person获取用户信息
    else:
        user_name = person
        user_email = get_user_email(person)
    return user_name, user_email



def cal_pr_subtype(repo, pr_number, group, maintainer_name):
    df_close_comment = group.loc[(group['concept:name'] == 'IssueCommentSupplement')
                                 & (group['people'] == maintainer_name)]
    close_comment = df_close_comment['message'].iloc[0] if (df_close_comment.shape[0] > 0) else None
    df_close = group.loc[group['concept:name'] == 'ClosePR']
    description = json.loads(df_close['description'].iloc[-1])
    close_flag = True if description['commit_url'] is not None else False
    df_reference = group.loc[group['concept:name'] == 'Referenced']
    reference_flag = df_reference.shape[0] > 0
    close_comment_flag = df_close_comment.shape[0] > 0
    pr_labels = get_pr_labels(repo, pr_number)
    label_flag = len(pr_labels) > 0
    pr_subtype = 0
    explain = None
    if close_flag:
        pr_subtype = 1
    elif reference_flag:
        pr_subtype = 2
    elif close_comment_flag:
        pr_subtype = 3
        explain = close_comment
    elif label_flag:
        pr_subtype = 4
        explain = pr_labels
    else:
        pr_subtype = 5

    return pr_subtype, explain
