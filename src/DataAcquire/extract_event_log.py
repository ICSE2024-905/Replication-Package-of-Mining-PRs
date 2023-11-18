import pandas as pd
import pm4py
from datetime import datetime, timedelta
from DataAcquire.Config import *
from utils.log_utils import get_event_log_from_sql, log_info
from utils.pr_self_utils import get_pr_attributes
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


'''
Function: Segment the three types of events: SubmitCommit, IssueComment, and ReviewComment.
1. Subdivide SubmitCommit: SubmitCommit (before OpenPR), Revise (after OpenPR)
2. Subdivide IssueComment: IssueComment (before ClosePR), IssueCommentSupplement (after ClosePR)
3. Segment ReviewComment: ReviewComment (before ClosePR), ReviewCommentSupplement (after ClosePR)
'''
def divide_event(repo: str, df: pd.DataFrame) -> pd.DataFrame:
    def divide(event_type: str, event_time: datetime, pr_open_time: datetime, pr_close_time: datetime):
        if event_type == 'SubmitCommit' and (not pd.isna(pr_open_time)):
            return "Revise" if event_time > pr_open_time else "SubmitCommit"
        elif event_type == 'IssueComment' and (not pd.isna(pr_close_time)):
            return "IssueCommentSupplement" if event_time >= pr_close_time else "IssueComment"
        elif event_type == 'ReviewComment' and (not pd.isna(pr_close_time)):
            return "ReviewCommentSupplement" if event_time >= pr_close_time else "ReviewComment"
        return event_type

    df_new = pd.DataFrame()
    for pr_number, group in df.groupby('pr_number'):
        pr = get_pr_attributes(repo, int(pr_number))
        pr_open_time = pr['created_at']
        pr_close_time = pr['closed_at']
        group['activity'] = group.apply(lambda x: divide(x['activity'], x['created_at'], pr_open_time, pr_close_time), axis=1)
        df_new = pd.concat([df_new, group])
    return df_new


'''

Function: Correct the time of the ReviewRequested event. Because the reviewer can be selected when creating a PR, the time of the ReviewRequested event is consistent with OpenPR, which is not conducive to the mining process.
'''
def modify_requested_review_time(repo: str, df: pd.DataFrame):
    def divide(event_type: str, event_time: datetime, pr_open_time: datetime):
        if event_type == 'ReviewRequested' and (not pd.isna(pr_open_time)):
            return pr_open_time + delta if event_time <= pr_open_time else event_time
        return event_time

    df_new = pd.DataFrame()
    delta = timedelta(seconds=1)
    for pr_number, group in df.groupby('pr_number'):
        pr = get_pr_attributes(repo, int(pr_number))
        pr_open_time = pr['created_at']
        group['created_at'] = group.apply(lambda x: divide(x['activity'], x['created_at'], pr_open_time), axis=1)
        df_new = pd.concat([df_new, group])
    return df_new


'''
Function: Process log, filter Activity, remove redundant ClosePR, subdivide SubmitCommit
'''
def process_log(repo: str, df: pd.DataFrame) -> pd.DataFrame:
    # Remove redundant ClosePR (ClosePR will appear redundantly during MergePR)
    merge_index = df.loc[df['activity'] == 'MergePR'].index
    close_index = []
    for idx in merge_index:
        if idx < df.shape[0] - 1:
            if df.loc[idx + 1, 'activity'] == 'ClosePR':
                close_index.append(idx + 1)
            elif df.loc[idx - 1, 'activity'] == 'ClosePR':
                close_index.append(idx - 1)
    df.drop(index=close_index, inplace=True)
    df = divide_event(repo, df)
    df = modify_requested_review_time(repo, df)
    df = df[['pr_number', 'activity', 'people', 'created_at', 'scene', 'message', 'description']]
    activities = ['SubmitCommit', 'OpenPR', 'Revise',
                  'IssueComment', 'ReviewComment', 'ReviewApproved', 'ReviewRejected',
                  'ClosePR', 'MergePR', 'DeleteBranch',
                  'ReopenPR', 'ReviewDismissed', 'ReviewRequested', 'Referenced',
                  'IssueCommentSupplement', 'ReviewCommentSupplement',
                  'Labeled', 'Assigned', 'CrossReferenced', 'UnLabeled', 'RenameTitle',
                  'HeadRefForcePushed', 'UnAssigned', 'ReviewRequestRemoved',
                  'BaseRefChanged']
    df = df.loc[df['activity'].isin(activities)]
    return df


'''

Function: Event log data preprocessing: loading event logs, eliminating invalid cases
'''
def data_preprocess(repo: str):
    data = get_event_log_from_sql(repo)
    df = pd.DataFrame(data)

    df = process_log(repo, df)

    log = pm4py.format_dataframe(df, case_id='pr_number', activity_key='activity', timestamp_key='created_at')
    log = log[['case:concept:name', 'concept:name', 'time:timestamp', 'people', 'scene', 'message', 'description']]
    log['time:timestamp'] = log['time:timestamp'].dt.tz_localize(None)

    print("origin log")
    log_info(log)

    log = pm4py.filter_event_attribute_values(log, 'concept:name', ['ClosePR', 'MergePR'], level="case", retain=True)
    print("filter_event_attribute_values (ClosePR, MergePR)")
    log_info(log)

    output_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    log.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in projects:
        repo = pro.split('/')[1]
        data_preprocess(repo)
        print(f"repo#{repo} process done\n")

