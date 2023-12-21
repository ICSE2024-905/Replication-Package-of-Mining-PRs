import requests
import pandas as pd
import json
from datetime import datetime
from utils.url_utils import get_req_headers, get_next_url
from utils.time_utils import time_reverse
from utils.pr_self_utils import get_pr_between
from utils.mysql_utils import select_all, batch_insert_into_event_log

user_map = {}

def cal_operator(sha, project, author_name):
    if (author_name is not None) and (author_name in user_map):
        return user_map[author_name]
    repo = project.split("/")[1]
    table = f"{repo.replace('-', '_')}_commit"
    sql = f"select * from {table} where sha='{sha}'"
    data = select_all(sql)
    author_login = author_name
    if len(data) > 0:
        author_login = data[0]['author'] if data[0]['author'] is not None else author_name
    else:
        print(f"{table}中没有找到{sha}的记录")
    user_map[author_name] = author_login
    return author_login


def parse_committed_event(item, project):
    event_type = 'SubmitCommit'
    # operator = cal_operator(item['sha'], project, item['author']['name'])
    operator = item['author']['name']
    operate_time = time_reverse(item['committer']['date'])
    message = item['message']
    description = {
        'sha': item['sha'],
        'author': item['author'],
        'committer': item['committer']
    }
    return [event_type, operator, operate_time, message, description]


def parse_commented_event(item):
    event_type = 'IssueComment'
    operator = item['user']['login']
    operate_time = time_reverse(item['created_at'])
    message = item['body']
    description = {
        'url': item['url'],
        'author_association': item['author_association']
    }
    return [event_type, operator, operate_time, message, description]


def parse_reviewed_event(item):
    def cal_review_type(state):
        t = None
        if state == 'commented':
            t = 'ReviewComment'
        elif state == 'approved':
            t = 'ReviewApproved'
        elif state == 'changes_requested':
            t = 'ReviewRejected'
        elif state == 'dismissed':
            t = 'ReviewDismissed'
        return t
    event_type = cal_review_type(item['state'])
    operator = item['user']['login'] if item['user'] is not None else None
    operate_time = time_reverse(item['submitted_at'])
    message = item['body']
    description = {
        'author_association': item['author_association'],
        'html_url': item['html_url']
    }
    return [event_type, operator, operate_time, message, description]


def parse_renamed_event(item):
    event_type = 'RenameTitle'
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = None
    description = {
        'rename': item['rename'],
        'url': item['url']
    }
    return [event_type, operator, operate_time, message, description]


def parse_review_dismissed_event(item):
    event_type = 'ReviewDismissed'
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = None
    description = {
        'dismissed_review': item['dismissed_review'],
        'url': item['url']
    }
    return [event_type, operator, operate_time, message, description]


def parse_review_requested_event(item, event_type):
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = None
    description = {
        'requested_reviewer': item['requested_reviewer'] if 'requested_reviewer' in item else None,
        'requested_team': item['requested_team'] if 'requested_team' in item else None
    }
    return [event_type, operator, operate_time, message, description]


def parse_assigned_event(item, event_type):
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = None
    description = {
        'assignee': item['assignee']
    }
    return [event_type, operator, operate_time, message, description]


def parse_cross_referenced_event(item):
    event_type = 'CrossReferenced'
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = item['source']['issue']['title']
    description = {
        'reference': {
            'url': item['source']['issue']['url'],
            'is_pull_request': 'pull_request' in item['source']['issue'],
        }
    }
    return [event_type, operator, operate_time, message, description]


def parse_label_event(item, event_type):
    operator = item['actor']['login']
    operate_time = time_reverse(item['created_at'])
    message = item['label']['name']
    description = None
    return [event_type, operator, operate_time, message, description]


def parse_common_event(item, event_type):
    operator = item['actor']['login'] if item['actor'] is not None else None
    operate_time = time_reverse(item['created_at'])
    message = None
    description = {
        'url': item['url'],
        'commit_url': item['commit_url']
    }
    return [event_type, operator, operate_time, message, description]


'''
Function: Determine the collaboration scenario to which a single PR belongs（fork_merge, fork_close, unfork_merge, unfork_close）
'''
def get_scene(pr):
    scene = None
    pr_state = pr['merged']
    is_fork = pr['head_repo_fork']
    closed_at = pr['closed_at']
    if (closed_at is None) or (pr_state is None) or (is_fork is None):
        return scene
    if is_fork and pr_state:
        scene = "fork_merge"
    elif is_fork and (not pr_state):
        scene = "fork_close"
    elif (not is_fork) and pr_state:
        scene = "unfork_merge"
    elif (not is_fork) and (not pr_state):
        scene = "unfork_close"
    return scene


'''
Function: Get all event information of a single PR and reclassify it
'''
def crawl_event_for_single_pr(project, pr_number):
    event_list = []
    req_headers = get_req_headers()
    url = f"https://api.github.com/repos/{project}/issues/{pr_number}/timeline?per_page=100"
    while url is not None:
        res = requests.get(url, headers=req_headers)
        if 200 <= res.status_code < 300:
            content = res.json()
            for item in content:
                event = item['event']
                l = []
                if event == 'committed':
                    l = parse_committed_event(item, project)
                elif event == 'commented':
                    l = parse_commented_event(item)
                elif event == 'reviewed':
                    l = parse_reviewed_event(item)
                elif event == 'merged':
                    l = parse_common_event(item, 'MergePR')
                elif event == 'closed':
                    l = parse_common_event(item, 'ClosePR')
                elif event == 'reopened':
                    l = parse_common_event(item, 'ReopenPR')
                elif event == 'head_ref_deleted':
                    l = parse_common_event(item, 'DeleteBranch')
                elif event == 'base_ref_changed':
                    l = parse_common_event(item, 'BaseRefChanged')
                elif event == 'renamed':
                    l = parse_renamed_event(item)
                elif event == 'review_dismissed':
                    l = parse_review_dismissed_event(item)
                elif event == 'review_requested':
                    l = parse_review_requested_event(item, 'ReviewRequested')
                elif event == 'review_request_removed':
                    l = parse_review_requested_event(item, 'ReviewRequestRemoved')
                elif event == 'assigned':
                    l = parse_assigned_event(item, 'Assigned')
                elif event == 'unassigned':
                    l = parse_assigned_event(item, 'UnAssigned')
                elif event == 'marked_as_duplicate':
                    l = parse_common_event(item, 'MarkedAsDuplicate')
                elif event == 'cross-referenced':
                    l = parse_cross_referenced_event(item)
                elif event == 'labeled':
                    l = parse_label_event(item, 'Labeled')
                elif event == 'unlabeled':
                    l = parse_label_event(item, 'UnLabeled')
                elif event == 'referenced':
                    l = parse_common_event(item, 'Referenced')
                elif event == 'head_ref_force_pushed':
                    l = parse_common_event(item, 'HeadRefForcePushed')

                if len(l) > 0:
                    event_list.append(l)
        else:
            print(f"{url} request failed, error status code {res.status_code}")
        url = get_next_url(res.headers)

    return event_list


'''
Function: crawl all PR event logs of the project during the start~end period
'''
def crawl_event_for_project(project: str, start: datetime, end: datetime):
    repo = project.split("/")[1]
    pr_list = get_pr_between(repo, start, end)
    for pr in pr_list:
        pr_number = pr['pr_number']
        print(f"{repo} PR#{pr_number} begin")
        # if pr_number < 369:
        #     continue
        scene = get_scene(pr)
        if scene is None:
            print(f"{repo} PR#{pr['pr_number']},No explicit merge status or fork information (merged or head_repo_fork field is None)")
            continue
        event_list = crawl_event_for_single_pr(project, pr_number)
        event_list.append(['OpenPR', pr['pr_user_name'], pr['created_at'], None, None])
        df = pd.DataFrame(data=event_list, columns=['activity', 'people', 'created_at', 'message', 'description'])
        df['project'] = project
        df['pr_number'] = pr_number
        df['scene'] = scene
        df = df[['project', 'pr_number', 'activity', 'people', 'created_at', 'message', 'description', 'scene']]
        df['created_at'] = df['created_at'].astype(str)
        df['description'] = df['description'].apply(lambda x: json.dumps(x) if x is not None else None)
        df = df.groupby('pr_number').apply(lambda x: x.sort_values('created_at'))
        batch_insert_into_event_log(repo, df.values.tolist())


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for project in projects:
        start = datetime(2021, 1, 1)
        end = datetime(2022, 12, 31)
        print(f"{project} begin")
        crawl_event_for_project(project, start, end)
