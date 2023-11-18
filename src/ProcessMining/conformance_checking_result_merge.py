import pandas as pd
from ProcessMining.Config import *


'''
Function: merge consistency test results (train, test)
'''
def merge_conformance_check_result():
    df_merge = pd.DataFrame()
    for scene in PR_TYPES:
        train_alignment_path = f"{ALIGNMENTS_DIR}/train_data/{scene}_alignments.csv"
        df_train = pd.read_csv(train_alignment_path)

        test_alignment_path = f"{ALIGNMENTS_DIR}/test_data/{scene}_alignments.csv"
        df_test = pd.read_csv(test_alignment_path)

        df_total = pd.concat([df_train, df_test], ignore_index=True)
        df_total['scene'] = scene
        output_path = f"{ALIGNMENTS_DIR}/total_data/{scene}_alignments.csv"
        df_total.to_csv(output_path, index=False, header=True)

        df_merge = pd.concat([df_merge, df_total], ignore_index=True)

    output_path = f"{ALIGNMENTS_DIR}/alignments_total_result.csv"
    df_merge.to_csv(output_path, index=False, header=True)


if __name__ == "__main__":
    merge_conformance_check_result()

