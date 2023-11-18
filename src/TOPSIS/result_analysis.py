import pandas as pd
from TOPSIS.Config import *


'''
Function: Calculate the number of high-risk personnel in different projects, threshold is the scoring threshold for high-risk personnel
'''
def high_risk_people_on_repo(role, threshold):
    input_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df = pd.read_excel(input_path)
    df['high_risk'] = df['score'].apply(lambda x: 1 if x < threshold else 0)
    repos = df['repo'].unique()
    datas = []
    for repo in repos:
        df_repo = df.loc[df['repo'] == repo]
        df_high_risk = df_repo.loc[df_repo['high_risk'] == 1]
        people_num = df_repo.shape[0]
        high_risk_num = df_high_risk.shape[0]
        datas.append([repo, people_num, high_risk_num])
    output_path = f"{SUMMARY_DIR}/{role}_high_risk.xls"
    df_file = pd.DataFrame(data=datas, columns=['repo', 'people_num', 'high_risk_num'])
    df_file.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    high_risk_people_on_repo("reviewer", 0.523)
    high_risk_people_on_repo("maintainer", 0.285)