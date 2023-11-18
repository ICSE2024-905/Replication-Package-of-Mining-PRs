import requests
import time
import json

from utils.access_key import get_token
from utils.mysql_utils import insert_into_pr_self
from utils.time_utils import time_reverse


def list_to_json(temp_list):
    dict = {}
    for i in range(0, temp_list.__len__()):
        dict[i] = temp_list[i]

    return json.dumps(dict)


# Based on the number of comments
def url_to_json(url, number, headers):
    url_str = url + "?per_page=100&anon=true&page="
    # print(url_str)
    page = 1
    maxPage = number // 100 + 1
    count = 0
    re_json = json.loads("[]")
    while page <= maxPage:
        try:
            temp_url_str = url_str + page.__str__()
            print(temp_url_str)
            url_r = requests.get(temp_url_str, headers=headers)
            re_json = re_json + url_r.json()
            page = page + 1
        except Exception as e:
            print(e)
    return re_json


# Count the number of elements contained in the url
def findUrlJsonCount(url_str, headers):
    url_str = url_str + "?per_page=100&anon=true&page="
    # print(url_str)
    page = 1
    count = 0
    while 1:
        temp_url_str = url_str + page.__str__()
        print(temp_url_str)
        url_r = requests.get(temp_url_str, headers=headers)
        url_json = url_r.json()
        if len(url_json) < 100:
            count = count + len(url_json)
            return count
        else:
            count = count + 100
            page = page + 1
    return count


# Crawl all PR data in the project repo_name where pr_number is in the interval [index, max_num]
def get_pr_self_info(index, max_num, owner_name, repo_name, headers):
    pr_url = "https://api.github.com/repos/" + owner_name + "/" + repo_name + "/pulls/"
    update_sql = """update """ + repo_name.replace('-', '_') + """_self set
                pr_user_id=%s,
                pr_user_name=%s,
                pr_author_association=%s,
                title=%s,
                body=%s,
                labels=%s,
                state=%s,
                created_at=%s,
                updated_at=%s,
                closed_at=%s,
                merged_at=%s,
                merged=%s,
                mergeable=%s,
                mergeable_state=%s,
                merge_commit_sha=%s,
                assignees_content=%s,
                requested_reviewers_content=%s,
                comments_number=%s,
                comments_content=%s,
                review_comments_number=%s,
                review_comments_content=%s,
                commit_number=%s,
                commit_content=%s,
                changed_file_num=%s,
                total_add_line=%s,
                total_delete_line=%s, 
                issue_url=%s,
                head_ref=%s,
                head_repo_full_name=%s,
                head_repo_fork=%s,
                base_ref=%s,
                base_repo_full_name=%s,
                base_repo_fork=%s 
                where  pr_number=%s and repo_name=%s"""
    while index < max_num:
        try:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "PR#" + str(index) + " begin")
            temp_url = pr_url + index.__str__()
            pr_r = requests.get(temp_url, headers=headers)
            print("pr_url: " + temp_url + "  Status Code:", pr_r.status_code)
        except Exception as e:
            print("网络连接失败: pr_url: ", temp_url)
            print(e)
            time.sleep(10)
            continue
        if 200 <= pr_r.status_code < 300:
            pr_json_str = pr_r.json()
            pr_number = index
            pr_user_id = pr_json_str["user"]["id"]
            pr_user_name = pr_json_str["user"]["login"]
            pr_author_association = pr_json_str["author_association"]
            title = pr_json_str["title"]
            body = pr_json_str["body"]
            state = pr_json_str["state"]
            created_at = pr_json_str["created_at"]
            updated_at = pr_json_str["updated_at"]
            closed_at = pr_json_str["closed_at"]
            merged_at = pr_json_str["merged_at"]
            merged = pr_json_str["merged"]
            mergeable = pr_json_str["mergeable"]
            mergeable_state = pr_json_str["mergeable_state"]
            merge_commit_sha = pr_json_str["merge_commit_sha"]
            comments_number = pr_json_str["comments"]
            review_comments_number = pr_json_str["review_comments"]
            commit_number = pr_json_str["commits"]
            changed_file_num = pr_json_str["changed_files"]
            total_add_line = pr_json_str["additions"]
            total_delete_line = pr_json_str["deletions"]
            labels = list_to_json(pr_json_str["labels"])
            assignees_content = list_to_json(pr_json_str["assignees"])
            requested_reviewers_content = list_to_json(pr_json_str["requested_reviewers"])
            comments_content = url_to_json(pr_json_str["comments_url"], comments_number, headers)
            review_comments_content = url_to_json(pr_json_str["review_comments_url"], review_comments_number, headers)
            commit_content = url_to_json(pr_json_str["commits_url"], commit_number, headers)
            issue_url = pr_json_str["issue_url"]
            head_ref = pr_json_str["head"]["ref"],
            head_repo_full_name = pr_json_str["head"]["repo"]["full_name"] if pr_json_str["head"]["repo"] is not None else None,
            head_repo_fork = pr_json_str["head"]["repo"]["fork"] if pr_json_str["head"]["repo"] is not None else None,
            base_ref = pr_json_str["base"]["ref"],
            base_repo_full_name = pr_json_str["base"]["repo"]["full_name"] if pr_json_str["base"]["repo"] is not None else None,
            base_repo_fork = pr_json_str["base"]["repo"]["fork"] if pr_json_str["base"]["repo"] is not None else None,
        else:
            index = index + 1
            continue
        try:
            sqlData = (
                pr_number,
                temp_url,
                repo_name,
                pr_user_id,
                pr_user_name,
                pr_author_association,
                title,
                body,
                labels,
                state,
                time_reverse(created_at),
                time_reverse(updated_at),
                time_reverse(closed_at),
                time_reverse(merged_at),
                ((merged == True) and 1 or 0),
                ((mergeable == True) and 1 or 0),
                mergeable_state,
                merge_commit_sha,
                assignees_content,
                requested_reviewers_content,
                comments_number,
                json.dumps(comments_content),
                review_comments_number,
                json.dumps(review_comments_content),
                commit_number,
                json.dumps(commit_content),
                changed_file_num,
                total_add_line,
                total_delete_line,
                issue_url,
                head_ref,
                head_repo_full_name,
                head_repo_fork,
                base_ref,
                base_repo_full_name,
                base_repo_fork
            )
            insert_into_pr_self(repo_name, sqlData)
            index = index + 1
        except Exception as e:
            index = index + 1
            print(e)
            continue


if __name__ == '__main__':
    # Set crawling parameters
    index = 1
    max_num = 1990
    owner_name = "apache"
    repo_name = "dubbo"
    access_token = get_token()
    headers = {'Authorization': 'token ' + access_token}

    # Start crawling data
    get_pr_self_info(index, max_num, owner_name, repo_name, headers)


