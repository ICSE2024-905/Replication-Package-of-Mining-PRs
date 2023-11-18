import pandas as pd
from AnomalyPermissionChange.Config import *


'''
功能：统计过程/数据异常的权限变更人员在项目中的数量分布情况
'''
def repo_single_anomaly_people_num(projects, anomaly_type):
    datas = []
    for pro in projects:
        repo = pro.split("/")[1]
        # 分项目、过程异常类型两个维度来统计可疑权限变更人员的数量
        input_path = f"{MERGE_ANOMALY_DIR}/{repo}_merge_anomaly.xls"
        df = pd.read_excel(input_path)
        df_reviewer = df.loc[df['change_role'] == 'Reviewer']
        df_maintainer = df.loc[df['change_role'] == 'Maintainer']

        reviewer = df_reviewer.shape[0]
        maintainer = df_maintainer.shape[0]
        reviewer_process_anomaly = df_reviewer.loc[df_reviewer[anomaly_type] == -1].shape[0]
        maintainer_process_anomaly = df_maintainer.loc[df_maintainer[anomaly_type] == -1].shape[0]
        # reviewer_process_anomaly_rate = "{:.1f}%".format(reviewer_process_anomaly*100 / reviewer)
        # maintainer_process_anomaly_rate = "{:.1f}%".format(maintainer_process_anomaly*100 / maintainer)
        datas.append([repo, reviewer_process_anomaly, maintainer_process_anomaly])
                      # f"{reviewer_process_anomaly}({reviewer_process_anomaly_rate})",
                      # f"{maintainer_process_anomaly}({maintainer_process_anomaly_rate})"])

    # 保存为文件
    output_path = f"{SUMMARY_DIR}/repo_{anomaly_type}_num.xls"
    df_file = pd.DataFrame(data=datas, columns=['repo', 'reviewer', 'maintainer'])
    df_file.to_excel(output_path, index=False, header=True)


'''
功能：统计过程&数据异常的权限变更人员在项目中的数量分布情况
'''
def repo_tow_anomaly_people_num(projects):
    datas = []
    for pro in projects:
        repo = pro.split("/")[1]
        # 分项目、过程异常类型两个维度来统计可疑权限变更人员的数量
        input_path = f"{MERGE_ANOMALY_DIR}/{repo}_merge_anomaly.xls"
        df = pd.read_excel(input_path)
        df_reviewer = df.loc[df['change_role'] == 'Reviewer']
        df_maintainer = df.loc[df['change_role'] == 'Maintainer']

        reviewer = df_reviewer.shape[0]
        maintainer = df_maintainer.shape[0]
        reviewer_process_anomaly = df_reviewer.loc[(df_reviewer['process_anomaly'] == -1) & (df_reviewer['data_anomaly'] == -1)].shape[0]
        maintainer_process_anomaly = df_maintainer.loc[(df_maintainer['process_anomaly'] == -1) & (df_maintainer['data_anomaly'] == -1)].shape[0]
        # reviewer_process_anomaly_rate = "{:.1f}%".format(reviewer_process_anomaly*100 / reviewer)
        # maintainer_process_anomaly_rate = "{:.1f}%".format(maintainer_process_anomaly*100 / maintainer)
        datas.append([repo, reviewer_process_anomaly, maintainer_process_anomaly])
                      # f"{reviewer_process_anomaly}({reviewer_process_anomaly_rate})",
                      # f"{maintainer_process_anomaly}({maintainer_process_anomaly_rate})"])

    # 保存为文件
    output_path = f"{SUMMARY_DIR}/repo_merge_anomaly_num.xls"
    df_file = pd.DataFrame(data=datas, columns=['repo', 'reviewer', 'maintainer'])
    df_file.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    anomaly_types = ["process_anomaly", "data_anomaly"]
    # repo_single_anomaly_people_num(projects, "data_anomaly")

    repo_tow_anomaly_people_num(projects)