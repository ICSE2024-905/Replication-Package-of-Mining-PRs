import requests
import pandas as pd
import json
from datetime import datetime
from typing import List
from utils.access_key import get_token
from utils.mysql_utils import select_all, insert_into_commit
from utils.time_utils import time_reverse


# Initialize variables
access_token = get_token()
headers = {'Authorization': 'token ' + access_token}


'''
Function: Convert object array to json string and save it
'''
def list_to_json(temp_list: List):
    dic = {}
    for i in range(0, len(temp_list)):
        dic[i] = temp_list[i]
    return json.dumps(dic)


'''
Function: Use GitHub Commit Api to crawl commit data and save it to the database
'''
def crawl_commit(owner: str, repo: str, pr_number: int, commit_sha_list: List):
    for sha in commit_sha_list:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        print(url)
        response = requests.get(url, headers=headers)
        if 200 <= response.status_code < 300:
            commit = response.json()
            author_login, author_name, author_email, author_date, committer_login, committer_name, committer_email, committer_date, message = None, None, None, None, None, None, None, None, None
            if not pd.isna(commit['author']) and len(commit['author']) > 0:
                author_login = commit['author']['login']
            if not pd.isna(commit['committer']) and len(commit['committer']) > 0:
                committer_login = commit['committer']['login']
            if not pd.isna(commit['commit']) and len(commit['commit']) > 0:
                message = commit['commit']['message']
                author_name = commit['commit']['author']['name']
                author_date = time_reverse(commit['commit']['author']['date'])
                author_email = commit['commit']['author']['email'] if not pd.isna(commit['commit']['author']) else None
                committer_name = commit['commit']['committer']['name']
                committer_date = time_reverse(commit['commit']['committer']['date'])
                committer_email = commit['commit']['committer']['email'] if not pd.isna(commit['commit']['committer']) else None
            author = author_login if author_login is not None else author_name
            committer = committer_login if committer_login is not None else committer_name
            line_addition = commit['stats']['additions']
            line_deletion = commit['stats']['deletions']
            file_edit_num = len(commit['files'])
            file_content = list_to_json(commit['files'])

            commit_data = [
                pr_number,
                sha,
                author,
                author_email,
                author_date,
                committer,
                committer_email,
                committer_date,
                message,
                line_addition,
                line_deletion,
                file_edit_num,
                file_content
            ]
            result = insert_into_commit(repo, commit_data)
            print(f"commit_sha: %s, insert %s" % (sha, result > 0))
        else:
            print(f"commit_sha: %s, request url failed, status code: %s" % (sha, response.status_code))


'''
Function: Extract the sha of all commits from the json string and return it in list form
'''
def extract_commit_sha(commit_content: str):
    commit_sha_list = []
    commit_list = json.loads(commit_content)
    if len(commit_list) == 0:
        return commit_sha_list
    for commit in commit_list:
        commit_sha = commit['sha']
        commit_sha_list.append(commit_sha)
    return commit_sha_list


'''
Function: Extract all commit-related information from the repo_self table
'''
def crawl_commit_between(owner: str, repo: str, start: datetime, end: datetime):
    # Query PR information for a specific time period from the repo_self table
    table = f"{repo.replace('-', '_')}_self"
    sql = f"select pr_number, created_at, closed_at, commit_number, commit_content from `{table}` where created_at >= '{start}' and created_at < '{end}'"
    data = select_all(sql)

    # Analyze PR collections with pandas
    df = pd.DataFrame(data)
    for index, row in df.iterrows():
        pr_number = row['pr_number']
        # if pr_number <= 29133:
        #     print(f"pr#{pr_number} process done")
        #     continue
        commit_content = row['commit_content']
        commit_sha_list = extract_commit_sha(commit_content)
        crawl_commit(owner, repo, pr_number, commit_sha_list)
        print(f"pr#{pr_number} process done")


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in ['tensorflow/tensorflow']:
        owner = pro.split('/')[0]
        repo = pro.split('/')[1]
        start = datetime(2022, 1, 1)
        end = datetime(2023, 1, 1)
        print(f"project#{repo}/{owner} begin")
        crawl_commit_between(owner, repo, start, end)
        print(f"project#{repo}/{owner} process done")