import pandas as pd
import numpy as np
from typing import List

def cal_mean(l: List):
    sum = 0
    len = 0
    for v in l:
        if pd.isna(v):
            continue
        sum += v
        len += 1
    if len == 0:
        return 0
    return sum * 1.0 / len


def kappa(matrix):
    n = np.sum(matrix)
    sum_po = 0
    sum_pe = 0
    for i in range(len(matrix[0])):
        sum_po += matrix[i][i]
        row = np.sum(matrix[i, :])
        col = np.sum(matrix[:, i])
        sum_pe += row * col
    po = sum_po / n
    pe = sum_pe / (n * n)
    # print(po, pe)
    return (po - pe) / (1 - pe)