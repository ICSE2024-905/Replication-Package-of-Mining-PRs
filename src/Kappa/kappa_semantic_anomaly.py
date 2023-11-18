import pandas as pd
from Kappa.Config import *


'''
Function: Merge the labeling results of yang and ma. The results of yang are comprehensive. Ma needs to add some labels, so ma’s labeling is a more accurate version that has been revised later.
'''
def merge_semantic_file(t):
    file_ma = f"{ANOMALY_PR_MA_PATH}/{t}.csv"
    file_yang = f"{ANOMALY_PR_YANG_PATH}/{t}.xls"

    df_ma = pd.read_csv(file_ma)
    df_yang = pd.read_excel(file_yang)

    df_ma['category_ma'] = df_ma['reason'].apply(lambda x: x.split("-")[0])
    df_ma = df_ma[['repo', 'pr_number', 'category_ma']]

    df_yang.rename(columns={'category': 'category_yang'}, inplace=True)

    df_merge = pd.merge(df_yang, df_ma, how='left', on=['repo', 'pr_number'])

    output_path = f"{ANOMALY_PR_MERGE_PATH}/{t}.xls"
    df_merge.to_excel(output_path, index=False, header=True, encoding="utf-8-sig")


def cal_kappa_matrix():
    file_path = f"{ANOMALY_PR_PATH}/all_semantic_anomaly.xls"
    df = pd.read_excel(file_path)

    datas = []
    for i in range(len(SEMANTIC_TYPE)):
        l = []
        for j in range(len(SEMANTIC_TYPE)):
            df_filter = df.loc[(df['category_yang'] == SEMANTIC_TYPE[i]) & (df['category_ma'] == SEMANTIC_TYPE[j])]
            l.append(df_filter.shape[0])
        datas.append(l)

    output_path = f"{OUTPUT_PATH}/kappa_semantic_matrix.xls"
    df_file = pd.DataFrame(data=datas, columns=SEMANTIC_TYPE, index=SEMANTIC_TYPE)
    df_file.to_excel(output_path, index=True, header=True)


'''
Function: Calculate Kappa matrix and save it as a file
'''
def cal_kappa_matrix_other():
    file_path = f"{ANOMALY_PR_PATH}/semantic_anomaly_root_cause.xlsx"
    df1 = pd.read_excel(file_path, sheet_name=0)
    df2 = pd.read_excel(file_path, sheet_name=1)
    df3 = pd.concat([df1, df2], ignore_index=True)

    datas = []
    for i in range(len(SEMANTIC_TYPE)):
        l = []
        for j in range(len(SEMANTIC_TYPE)):
            df_filter = df3.loc[(df3['category_A'] == SEMANTIC_TYPE[i]) & (df3['category_B'] == SEMANTIC_TYPE[j])]
            l.append(df_filter.shape[0])
        datas.append(l)
    output_path = f"{OUTPUT_PATH}/kappa_semantic_matrix.xls"
    df_file = pd.DataFrame(data=datas, columns=SEMANTIC_TYPE, index=SEMANTIC_TYPE)
    df_file.to_excel(output_path, index=True, header=True)


if __name__ == '__main__':
    # t = "review_approved_but_close"
    # merge_semantic_file(t)
    # cal_kappa_matrix()
    cal_kappa_matrix_other()
