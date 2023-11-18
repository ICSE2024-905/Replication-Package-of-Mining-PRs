import pandas as pd
from NormalProcessModel.Config import *


def occur_in_pr(df: pd.DataFrame, output_path):
    datas = []
    df1 = df.iloc[:, 2:].applymap(lambda x: 0 if x == 0 else 1)
    total_case = df1.shape[0]
    columns = df1.columns.values.tolist()[2:]
    for c in columns:
        if "_" not in c:
            continue
        sum_pr_include = df1[c].sum()
        percent = sum_pr_include / total_case
        datas.append([c, sum_pr_include, percent])
    df_file = pd.DataFrame(data=datas, columns=['transition', 'sum_pr_include', 'percent'])
    df_file.sort_values(by='sum_pr_include', ascending=False, inplace=True)
    df_file.to_excel(output_path, index=False)


def filter_noise(df: pd.DataFrame):
    anomaly_branchs = ['ReviewRequested_DeleteBranch', 'ReviewApproved_DeleteBranch', 'DeleteBranch_DeleteBranch', 'ClosePR_ClosePR',
                       'MergePR_Revise', 'MergePR_ReviewRequested', 'MergePR_ReviewRequestRemoved', 'MergePR_ReviewApproved',
                       'ClosePR_Revise', 'ClosePR_ReviewRequested', 'ClosePR_ReviewRequestRemoved', 'ClosePR_ReviewApproved',
                       'ReviewRequested_MergePR', 'ReviewRequested_ClosePR', 'ReviewRejected_MergePR', 'ReviewApproved_ClosePR']
    for branch in anomaly_branchs:
        if branch in df.columns:
            df = df.loc[df[branch] == 0]
    return df


def cal_transition_frequency(scene):
    input_path = f"{NORMAL_CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    df = filter_noise(df)
    output_path = f"{TRANSITION_FREQ_DIR}/{scene}_transition_freq.xls"
    occur_in_pr(df, output_path)
    print(f"{scene} process done")




def filter_transition_by_low_occur_freq(threshold):
    transition_set = set()
    df_list = []
    for scene in PR_TYPES:
        input_path = f"{TRANSITION_FREQ_DIR}/{scene}_transition_freq.xls"
        df = pd.read_excel(input_path)
        df_filter = df.loc[df['percent'] > threshold]
        transition_list = df_filter['transition'].tolist()
        transition_set.update(tuple(transition_list))
        df_list.append(df)
        del df

    datas = []
    transition_list = list(transition_set)
    for i in range(len(PR_TYPES)):
        scene = PR_TYPES[i]
        df = df_list[i]
        single = [scene]
        for transition in transition_list:
            df_transition = df.loc[df['transition'] == transition]
            percent = 0
            if df_transition.shape[0] > 0:
                percent = df_transition['percent'].iloc[0]
            single.append(percent)
        datas.append(single)

    transition_list.insert(0, 'scene')
    df_file = pd.DataFrame(data=datas, columns=transition_list)
    output_file = f"{SUMMARY_DIR}/transition_percent.xls"
    df_file.to_excel(output_file, index=False, header=True)


if __name__ == '__main__':
    for scene in PR_TYPES:
        cal_transition_frequency("unfork_close")
    filter_transition_by_low_occur_freq(0.2)