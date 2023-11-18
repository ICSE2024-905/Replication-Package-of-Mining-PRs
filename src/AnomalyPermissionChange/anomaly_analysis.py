import pandas as pd
from AnomalyPermissionChange.Config import *


def total_merge_anomaly(pros):
    df_merge = pd.DataFrame()
    for pro in pros:
        repo = pro.split("/")[1]
        input_path = f"{MERGE_ANOMALY_DIR}/{repo}_merge_anomaly.xls"
        df = pd.read_excel(input_path)
        df.insert(loc=0, column='repo', value=repo)
        df_merge = pd.concat([df_merge, df], ignore_index=True)
    # 保存为文件
    output_path = f"{SUMMARY_DIR}/total_merge_anomaly.xls"
    df_merge.to_excel(output_path, index=False, header=True)


'''
功能：计算person所参与的PR的实际决策情况
'''
def cal_merge_rate(repo, person, role):
    input_path = f"{MERGE_ANOMALY_DIR}/{repo}_merge_anomaly.xls"
    df = pd.read_excel(input_path)
    df_person = df.loc[(df['people'] == person) & (df['change_role'] == role)]
    if df_person.shape[0] == 0:
        print(f"no finding result")
    person_info = df_person.iloc[0]
    involved_prs = person_info.loc['involved_pr_after_permission_change'].split("#")

    # 获取person参与过的事件日志
    from utils.log_utils import get_event_log_from_file, log_info
    log_path = f"../DataAcquire/event_log/{repo}_event_log.csv"
    df_log = get_event_log_from_file(log_path)
    filter_log = df_log.loc[df_log['case:concept:name'].isin(involved_prs)]
    log_info(filter_log)

    # 统计person决策的PR的实际合入情况
    from Statistics.cal_close_type import cal_close_type
    pr_type_1, pr_type_2, pr_type_3 = cal_close_type(filter_log)
    print(f"total:{len(involved_prs)}, pr_type_1:{len(pr_type_1)}, pr_type_2:{len(pr_type_2)}, pr_type_3:{len(pr_type_3)}")
    print(f"pr_type_1:{pr_type_1}")
    print(f"pr_type_2:{pr_type_2}")
    print(f"pr_type_3:{pr_type_3}")


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    total_merge_anomaly(projects)
    # cal_merge_rate('zookeeper', 'arshadmohammad', 'Maintainer')