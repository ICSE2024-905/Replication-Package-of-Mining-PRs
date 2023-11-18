import pymysql
from typing import List
from utils.access_key import get_mysql_root_psw

EVENT_TABLE_FIELDS = [
        "id",
        "type",
        "public",
        "created_at",
        "actor_id",
        "actor_login",
        "repo_id",
        "repo_name",
        "payload_ref",
        "payload_ref_type",
        "payload_pusher_type",
        "payload_push_id",
        "payload_size",
        "payload_distinct_size",
        "payload_commits",
        "payload_action",
        "payload_pr_number",
        "payload_forkee_full_name",
        "payload_changes",
        "payload_review_state",
        "payload_review_author_association",
        "payload_member_id",
        "payload_member_login",
        "payload_member_type",
        "payload_member_site_admin"]
COMMIT_TABLE_FIELDS = [
    "pr_number",
    "sha",
    "author",
    "author_email",
    "author_date",
    "committer",
    "committer_email",
    "committer_date",
    "message",
    "line_addition",
    "line_deletion",
    "file_edit_num",
    "file_content"]
PROCESS_EVENT_TABLE_FIELDS = [
    "repo",
    "pr_number",
    "activity",
    "created_at",
    "people",
    "scene"
]
PERMISSION_CHANGE_TABLE_FIELDS = [
    "repo",
    "people",
    "pr_number",
    "change_time",
    "permission"
]
PROCESS_MODEL_TABLE_FIELDS = [
    "scene",
    "log_case",
    "algorithm",
    "param",
    "average_trace_fitness",
    "percentage_of_fitting_traces",
    "precision",
    "generalization",
    "simplicity",
    "petri_net"
]
CONTRIBUTOR_TABLE_FIELDS = [
    'id',
    'login',
    'name',
    'email',
    'url',
    'public_repos',
    'created_at',
    'updated_at',
    'contributions',
    'project'
]
EVENT_LOG_TABLE_FIELDS = [
    'project',
    'pr_number',
    'activity',
    'people',
    'created_at',
    'message',
    'description',
    'scene'
]
PR_SELF_TABLE_FIELDS = [
    "pr_number",
    "pr_url",
    "repo_name",
    "pr_user_id",
    "pr_user_name",
    "pr_author_association",
    "title",
    "body",
    "labels",
    "state",
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at",
    "merged",
    "mergeable",
    "mergeable_state",
    "merge_commit_sha",
    "assignees_content",
    "requested_reviewers_content",
    "comments_number",
    "comments_content",
    "review_comments_number",
    "review_comments_content",
    "commit_number",
    "commit_content",
    "changed_file_num",
    "total_add_line",
    "total_delete_line",
    "issue_url",
    "head_ref",
    "head_repo_full_name",
    "head_repo_fork",
    "base_ref",
    "base_repo_full_name",
    "base_repo_fork"
]

username, password = get_mysql_root_psw()
conn = pymysql.connect(host='127.0.0.1', port=3306, user=username, password=password, db='poison', charset='utf8', cursorclass=pymysql.cursors.DictCursor)



def batch_insert_into_events(repo: str, data: List):
    table = f"{repo.replace('-', '_')}_events"
    if len(data) == 0:
        return
    fields = ",".join(EVENT_TABLE_FIELDS)
    fields_param = ("%s," * len(EVENT_TABLE_FIELDS))[0:-1]
    sql = f"insert into `{table}` ({fields}) values({fields_param})"

    cursor = conn.cursor()
    try:
        conn.ping(reconnect=True)
        result = cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()



def batch_insert_into_process_events(data: List):
    if len(data) == 0:
        return
    fields = ",".join(PROCESS_EVENT_TABLE_FIELDS)
    fields_param = ("%s," * len(PROCESS_EVENT_TABLE_FIELDS))[0:-1]
    sql = f"insert into process_events ({fields}) values({fields_param})"

    cursor = conn.cursor()
    try:
        conn.ping(reconnect=True)
        result = cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()



def batch_insert_into_permission_change(data: List):
    if len(data) == 0:
        return
    fields = ",".join(PERMISSION_CHANGE_TABLE_FIELDS)
    fields_param = ("%s," * len(PERMISSION_CHANGE_TABLE_FIELDS))[0:-1]
    sql = f"insert into permission_change ({fields}) values({fields_param})"

    cursor = conn.cursor()
    try:
        conn.ping(reconnect=True)
        result = cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()


def insert_into_commit(repo: str, data: List):
    table = f"{repo.replace('-', '_')}_commit"
    fields = ",".join(COMMIT_TABLE_FIELDS)
    fields_param = ("%s," * len(COMMIT_TABLE_FIELDS))[0:-1]
    sql = f"insert into `{table}` ({fields}) values({fields_param})"
    # print("执行SQL: " + sql)
    cursor = conn.cursor()
    result = 0
    try:
        conn.ping(reconnect=True)
        result = cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
    return result


'''
'''
def insert_into_process_model(data: List):
    fields = ",".join(PROCESS_MODEL_TABLE_FIELDS)
    fields_param = ("%s," * len(PROCESS_MODEL_TABLE_FIELDS))[0:-1]
    sql = f"insert into process_model ({fields}) values({fields_param})"

    cursor = conn.cursor()
    result = 0
    try:
        conn.ping(reconnect=True)
        result = cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"process_model表数据插入失败, {e}")
    return result



def insert_into_contributor(data: List):
    fields = ",".join(CONTRIBUTOR_TABLE_FIELDS)
    fields_param = ("%s," * len(CONTRIBUTOR_TABLE_FIELDS))[0:-1]
    sql = f"insert into contributor ({fields}) values({fields_param})"

    cursor = conn.cursor()
    result = 0
    try:
        conn.ping(reconnect=True)
        result = cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
    return result



def batch_insert_into_event_log(repo: str, data: List):
    if len(data) == 0:
        return
    table = f"{repo.replace('-', '_')}_event_log"
    fields = ",".join(EVENT_LOG_TABLE_FIELDS)
    fields_param = ("%s," * len(EVENT_LOG_TABLE_FIELDS))[0:-1]
    sql = f"insert into `{table}` ({fields}) values({fields_param})"

    cursor = conn.cursor()
    result = 0
    try:
        conn.ping(reconnect=True)
        result = cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
    return result


def insert_into_pr_self(repo: str, data: List):
    table = f"{repo.replace('-', '_')}_self"
    fields = ",".join(PR_SELF_TABLE_FIELDS)
    fields_param = ("%s," * len(PR_SELF_TABLE_FIELDS))[0:-1]
    sql = f"insert into `{table}` ({fields}) values({fields_param})"

    cursor = conn.cursor()
    result = 0
    try:
        conn.ping(reconnect=True)
        result = cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        # conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
    return result



def execute_sql(sql):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    print(cursor.rowcount)
    cursor.close()
    conn.close()



def select_all(sql):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def select_one(sql):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data
