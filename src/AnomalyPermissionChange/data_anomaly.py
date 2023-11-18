import pandas as pd
from AnomalyPermissionChange.Config import *

def data_anomaly(repo):
    input_path1 = f"{MULTI_MODEL_VOTE_DIR}/maintainer_multi_model_vote.xls"
    input_path2 = f"{MULTI_MODEL_VOTE_DIR}/reviewer_multi_model_vote.xls"

    df1 = pd.read_excel(input_path1)
    df2 = pd.read_excel(input_path2)
    df1['change_role'] = 'Maintainer'
    df2['change_role'] = 'Reviewer'
    df1.rename(columns={'vote': 'data_anomaly'}, inplace=True)
    df2.rename(columns={'vote': 'data_anomaly'}, inplace=True)
    df1 = df1.loc[df1['repo'] == repo]
    df2 = df2.loc[df2['repo'] == repo]
    df1 = df1[['people', 'change_role', 'data_anomaly', 'reason']]
    df2 = df2[['people', 'change_role', 'data_anomaly', 'reason']]
    df3 = pd.concat([df1, df2], ignore_index=True)

    output_path = f"{DATA_ANOMALY_DIR}/{repo}_data_anomaly.xls"
    df3.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    for pro in projects:
        repo = pro.split('/')[1]
        data_anomaly(repo)
        print(f"{repo} process done")