import pandas as pd
from AnomalyPermissionChange.Config import *

# 按项目合并结果
def merge_anomaly(repo):
    input_path1 = f"{PROCESS_ANOMALY_DIR}/{repo}_process_anomaly.xls"
    input_path2 = f"{DATA_ANOMALY_DIR}/{repo}_data_anomaly.xls"

    df1 = pd.read_excel(input_path1)
    df2 = pd.read_excel(input_path2)

    if df1.shape[0] == 0 or df2.shape[0] == 0:
        print(f"{repo} 行为异常/数据异常内容为空")
        return

    df1['process_anomaly'] = df1['anomaly_pr_rate'].apply(lambda x: -1 if x >= ANOMALY_PR_RATE_THRESHOLD else 1)
    df3 = pd.merge(df1, df2, how='left', on=['people', 'change_role'])
    output_path = f"{MERGE_ANOMALY_DIR}/{repo}_merge_anomaly.xls"
    df3.to_excel(output_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in projects:
        repo = pro.split('/')[1]
        merge_anomaly(repo)
        print(f"{repo} process done")