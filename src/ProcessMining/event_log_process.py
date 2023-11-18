import pm4py
from ProcessMining.Config import *
from utils.log_utils import log_info, get_event_log_from_file

'''
Function: Event log data preprocessing: only retain required activities
'''
def process_event_log(repo: str):
    input_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    log = get_event_log_from_file(input_path)
    print("origin log")
    log_info(log)
    log = pm4py.filter_event_attribute_values(log, 'concept:name', ['ReopenPR'], level="case", retain=False)
    print("filter_event_attribute_values (ReopenPR)")
    log_info(log)
    activities = ['SubmitCommit', 'OpenPR', 'Revise',
                  'IssueComment', 'ReviewComment', 'ReviewApproved', 'ReviewRejected',
                  'ClosePR', 'MergePR', 'DeleteBranch', 'ReviewRequested', 'Referenced', 'HeadRefForcePushed',
                  'ReviewRequestRemoved']
    log = log.loc[log['concept:name'].isin(activities)]

    log['concept:name'] = log['concept:name'].apply(lambda x: 'Revise' if x == 'HeadRefForcePushed' else x)
    log = log[['case:concept:name', 'concept:name', 'time:timestamp', 'people', 'scene']]
    output_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
    log.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


'''
Function: Count cases containing reopen events
'''
def reopen(repo):
    input_path = f"{EVENT_LOG_DIR}/{repo}_event_log.csv"
    log = get_event_log_from_file(input_path)
    # print("origin log")
    total_case_num, total_variants_num = log_info(log)
    log = pm4py.filter_event_attribute_values(log, 'concept:name', ['ReopenPR'], level="case", retain=True)
    # print("case contains (ReopenPR)")
    reopen_case_num, reopen_variants_num = log_info(log)

    print(f"repo: {repo}, total case: {total_case_num}, reopen case: {reopen_case_num}")
    return total_case_num, reopen_case_num


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in ['faker-js/faker']:
        repo = pro.split('/')[1]
        process_event_log(repo)
        print(f"repo#{repo} process done\n")

