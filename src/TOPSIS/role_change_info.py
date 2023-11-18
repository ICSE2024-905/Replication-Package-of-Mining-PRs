import pandas as pd
from TOPSIS.Config import *



def cal_role_change_info_for_single_repo(repo):
    input_path1 = f"{PROCESS_ANOMALY_PR_DIR}/process_anomaly_pr.xls"
    df_pr = pd.read_excel(input_path1)
    df_pr['repo'] = df_pr['case_id'].apply(lambda x: x.split("#")[0])
    df_pr['pr_number'] = df_pr['case_id'].apply(lambda x: x.split("#")[1])

    input_path2 = f"{ROLE_CHANGE_DIR}/{repo}_role_change.csv"
    df_role = pd.read_csv(input_path2)
    df_role = df_role.loc[df_role['change_role'].isin(['Maintainer', 'Reviewer'])]

    for index, row in df_role.iterrows():
        involved_pr_list = row['involved_pr_after_permission_change'].split("#")
        total_pr_num = len(involved_pr_list)
        df_anomaly_pr = df_pr.loc[(df_pr['repo'] == repo) & (df_pr['pr_number'].isin(involved_pr_list))]
        anomaly_pr_list = df_anomaly_pr['pr_number'].tolist()
        anomaly_pr_str = "#".join([str(x) for x in anomaly_pr_list])
        anomaly_pr_num = df_anomaly_pr.shape[0]
        anomaly_pr_rate = anomaly_pr_num * 1.0 / total_pr_num
        df_control_flow_anomaly_pr = df_pr.loc[(df_pr['repo'] == repo)
                                               & (df_pr['pr_number'].isin(involved_pr_list))
                                               & (df_pr['control_flow_anomaly'] == 1)]
        control_flow_anomaly_pr_list = df_control_flow_anomaly_pr['pr_number'].tolist()
        control_flow_anomaly_pr_str = "#".join([str(x) for x in control_flow_anomaly_pr_list])
        control_flow_anomaly_pr_num = df_control_flow_anomaly_pr.shape[0]
        control_flow_anomaly_pr_rate = control_flow_anomaly_pr_num * 1.0 / total_pr_num
        df_semantic_anomaly_pr = df_pr.loc[(df_pr['repo'] == repo)
                                           & (df_pr['pr_number'].isin(involved_pr_list))
                                           & (df_pr['semantic_anomaly'] == 1)]
        semantic_anomaly_pr_list = df_semantic_anomaly_pr['pr_number'].tolist()
        semantic_anomaly_pr_str = "#".join([str(x) for x in semantic_anomaly_pr_list])
        semantic_anomaly_pr_num = df_semantic_anomaly_pr.shape[0]
        semantic_anomaly_pr_rate = semantic_anomaly_pr_num * 1.0 / total_pr_num
        df_role.loc[index, 'total_pr_num'] = total_pr_num
        df_role.loc[index, 'anomaly_pr'] = anomaly_pr_str
        df_role.loc[index, 'control_flow_anomaly_pr'] = control_flow_anomaly_pr_str
        df_role.loc[index, 'semantic_anomaly_pr'] = semantic_anomaly_pr_str
        df_role.loc[index, 'anomaly_pr_num'] = anomaly_pr_num
        df_role.loc[index, 'control_flow_anomaly_pr_num'] = control_flow_anomaly_pr_num
        df_role.loc[index, 'semantic_anomaly_pr_num'] = semantic_anomaly_pr_num
        # df_role.loc[index, 'anomaly_pr_rate'] = anomaly_pr_rate
        # df_role.loc[index, 'control_flow_anomaly_pr_rate'] = control_flow_anomaly_pr_rate
        # df_role.loc[index, 'semantic_anomaly_pr_rate'] = semantic_anomaly_pr_rate
    df_role.insert(0, 'repo', repo)
    return df_role



def cal_role_change_info():
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    df_merge = pd.DataFrame()
    output_path = f"{SUMMARY_DIR}/role_change_info.xls"
    for pro in projects:
        repo = pro.split('/')[1]
        df_single = cal_role_change_info_for_single_repo(repo)
        df_merge = pd.concat([df_merge, df_single], ignore_index=True)
        print(f"{repo} process done")
    df_merge.to_excel(output_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == '__main__':
    cal_role_change_info()
