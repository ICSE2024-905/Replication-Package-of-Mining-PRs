import requests
from utils.access_key import get_token



def get_req_headers():
    access_token = get_token()
    req_headers = {
        'Authorization': 'token ' + access_token
    }
    return req_headers


def get_next_url(res_headers):
    next_url = None
    links = res_headers.get("Link")
    if links is not None:
        link_list = links.split(", ")
        for link in link_list:
            link_info = link.split("; ")
            if link_info[1] == "rel=\"next\"":
                next_url = link_info[0][1:-1]
    return next_url


user_map = {}



def get_committer_info(url):
    headers = get_req_headers()
    res = requests.get(url, headers=headers)
    committer_login, committer_email = None, None
    if 200 <= res.status_code < 300:
        commit = res.json()
        if commit['committer'] is not None and len(commit['committer']) > 0:
            committer_login = commit['committer']['login']
        if commit['commit'] is not None \
                and len(commit['commit']) > 0 \
                and commit['commit']['committer'] is not None:
            committer_email = commit['commit']['committer']['email']
    else:
        print(f"{url} requested failed, error code: {res.status_code}")
    print(f"{url} requested success, committer: {committer_login}, committer_email: {committer_email}")
    if committer_login not in user_map:
        user_map[committer_login] = committer_email
    return committer_login, committer_email



def get_user_email(user_name):
    if user_name in user_map:
        return user_map[user_name]
    headers = get_req_headers()
    url = f"https://api.github.com/users/{user_name}"
    res = requests.get(url, headers=headers)
    user_email = None, None
    if 200 <= res.status_code < 300:
        user_info = res.json()
        user_email = user_info['email']
    else:
        print(f"{url} requested failed, error code: {res.status_code}")
    print(f"{url} requested success, user_name: {user_name}, user_email: {user_email}")
    user_map[user_name] = user_email
    return user_email


