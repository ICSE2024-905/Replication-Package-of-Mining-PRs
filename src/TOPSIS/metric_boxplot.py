import pandas as pd
import numpy as np
from TOPSIS.Config import *

'''
Function: Statistical information of each evaluation indicator, including minimum value, first quartile, median, third quartile, maximum value, and average value. Note that you need to manually add the rank column to the topsis_result.xls file in advance.
'''
def cal_boxplot_data(role):
    input_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df = pd.read_excel(input_path)
    df_metrics = df.iloc[:, 2:-2]
    columns = df_metrics.columns.tolist()
    columns.insert(0, 'metric')
    statistics = []
    for index, column in df_metrics.iteritems():
        res = np.percentile(column, (0, 25, 50, 75, 100), interpolation='midpoint')
        mean = column.mean()
        statistics.append([index, res[0], res[1], res[2], res[3], res[4], mean])

    df_file = pd.DataFrame(data=statistics, columns=['metric', '0%', '25%', '50%', '75%', '100%', 'mean'])
    output_path = f"{SUMMARY_DIR}/{role}_metric_boxplot.xls"
    df_file.to_excel(output_path, index=False, header=True)


if __name__ == '__main__':
    cal_boxplot_data("reviewer")