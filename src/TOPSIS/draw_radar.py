import pandas as pd
import numpy as np
from TOPSIS.Config import *


'''
Function: Draw a radar chart of a single person who has changed permissions and show their performance on various evaluation indicators.
'''
def prepare_data(role, min_columns):
    input_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df_origin = pd.read_excel(input_path)

    df = df_origin.iloc[:, 2:-2]
    df[min_columns] = df[min_columns].apply(lambda x: np.max(x) - x)

    # df = df.apply(np.log1p)

    df = df.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))

    df['repo'] = df_origin['repo']
    df['people'] = df_origin['people']
    df['score'] = df_origin['score']
    df['rank'] = df_origin['rank']
    output_path = f"{SUMMARY_DIR}/{role}_radar_data.xls"
    df.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    prepare_data("maintainer", ['behavior_risk', 'avg_response_time', 'avg_response_interval'])