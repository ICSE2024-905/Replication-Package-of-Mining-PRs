import pandas as pd
from TOPSIS.Config import *
from utils.topsis_utils import *



def prepare_data(role):
    input_path1 = f"{SUMMARY_DIR}/score_behavior_risk.xls"
    input_path2 = f"{FEATURE_DIR}/{role}_feature.csv"
    df1 = pd.read_excel(input_path1)
    df1 = df1.loc[df1['change_role'] == role.capitalize()]
    df1 = df1[['repo', 'people', 'total_score']]
    df1.rename(columns={'total_score': 'behavior_risk'}, inplace=True)
    df2 = pd.read_csv(input_path2)

    df3 = pd.merge(df2, df1, how='left', on=['repo', 'people'])
    df3 = df3[['repo', 'people', 'behavior_risk', 'pr_num', 'avg_review_comment_length', 'avg_review_response_time']]
    output_path = f"{SUMMARY_DIR}/{role}_topsis_data.xls"
    df3.to_excel(output_path, index=False, header=True)



def topsis_reviewer(role, weights):
    file = f"{SUMMARY_DIR}/{role}_topsis_data.xls"
    df_origin = pd.read_excel(file)
    df_origin['avg_review_response_time'] = df_origin['avg_review_response_time'] / 1440

    df = df_origin.copy()
    df["behavior_risk"] = df["behavior_risk"].apply(np.log1p)
    df["pr_num"] = df["pr_num"].apply(np.log1p)
    df["avg_review_comment_length"] = df["avg_review_comment_length"].apply(np.log1p)
    df["avg_review_response_time"] = df["avg_review_response_time"].apply(np.log1p)

    answer1 = df.iloc[:, 2:].values.T

    answer2 = []
    for i in range(0, weights.size):
        if i == 0:
            answer = dataDirection_1(answer1[i])
        elif i == 1:
            answer = answer1[i]
        elif i == 2:
            answer = answer1[i]
        else:
            answer = dataDirection_1(answer1[i])
        answer2.append(answer)
    answer2 = np.array(answer2)
    answer3 = standard_matrix(answer2)
    answer4 = weight_standard_matrix(answer3, weights)
    answer5 = score_and_normalize(answer4)

    df_origin['score'] = answer5
    output_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df_origin.sort_values(by='score', inplace=True)
    df_origin.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    prepare_data("reviewer")

    weights = np.array([0.65062452, 0.09561662, 0.04820532, 0.20555354])

    topsis_reviewer("reviewer", weights)