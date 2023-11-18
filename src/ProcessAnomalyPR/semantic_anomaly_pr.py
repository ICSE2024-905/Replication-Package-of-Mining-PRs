import pandas as pd
from ProcessAnomalyPR.Config import *


'''
Function: Merge all semantic exception type files
'''
def semantic_anomaly_pr():
    filename_list = ["no_reviewer_response_but_close", "no_reviewer_response_but_merge",
                     "review_approved_but_close", "review_rejected_but_merge"]
    df_merge = pd.DataFrame()
    for index in range(len(filename_list)):
        filename = filename_list[index]
        input_path = f"../LabelData/anomaly_pr/{filename}.xls"
        df = pd.read_excel(input_path)
        df['semantic_type'] = filename
        df_merge = pd.concat([df_merge, df], ignore_index=True)
    output_path = f"{PROCESS_ANOMALY_PR_DIR}/semantic_anomaly_pr.xls"
    df_merge.to_excel(output_path, index=False, header=True)


'''
Function: Merge the scored semantic anomaly PRs. Note that you need to manually add the score column to the file in advance and perform scoring.
'''
def score_semantic_anomaly_pr():
    filename_list = ["no_reviewer_response_but_close", "no_reviewer_response_but_merge",
                     "review_approved_but_close", "review_rejected_but_merge"]
    df_merge = pd.DataFrame()
    for index in range(len(filename_list)):
        filename = filename_list[index]
        input_path = f"../LabelData/anomaly_pr/{filename}.xls"
        df = pd.read_excel(input_path)
        df['case_id'] = df.apply(lambda x: str(x['repo']) + '#' + str(x['pr_number']), axis=1)
        df['semantic_anomaly_type'] = index + 1
        df = df[['case_id', 'semantic_anomaly_type', 'category', 'score']]
        df_merge = pd.concat([df_merge, df], ignore_index=True)
    output_path = f"{SUMMARY_DIR}/score_semantic_anomaly_pr.xls"
    df_merge.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    semantic_anomaly_pr()
    # score_semantic_anomaly_pr()