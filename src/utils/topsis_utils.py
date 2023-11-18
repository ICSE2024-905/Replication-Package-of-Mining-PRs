import numpy as np

def dataDirection_1(datas):
    return np.max(datas) - datas

def dataDirection_2(datas, x_best):
    temp_datas = datas - x_best
    M = np.max(abs(temp_datas))
    answer_datas = 1 - abs(datas - x_best) / M
    return answer_datas


def dataDirection_3(datas, x_min, x_max):
    M = max(x_min - np.min(datas), np.max(datas) - x_max)
    answer_list = []
    for i in datas:
        if i < x_min:
            answer_list.append(1 - (x_min - i) / M)  #
        elif x_min <= i <= x_max:
            answer_list.append(1)
        else:
            answer_list.append(1 - (i - x_max) / M)
    return np.array(answer_list)


def standard_matrix(datas):
    K = np.power(np.sum(pow(datas, 2), axis=1), 0.5)
    for i in range(0, K.size):
        for j in range(0, datas[i].size):
            datas[i, j] = datas[i, j] / K[i]
    return datas


def weight_standard_matrix(datas, weights):
    for j in range(0, np.size(datas, axis=1)):
        for i in range(0, weights.size):
            datas[i, j] = datas[i, j] * weights[i]
    return datas


def best_and_worst(datas):
    list_max = []
    list_min = []
    for i in range(0, np.size(datas, axis=0)):
        list_max.append(np.max(datas[i, :]))
        list_min.append(np.min(datas[i, :]))
    return np.array(list_max), np.array(list_min)


def score_and_normalize(datas):
    list_max, list_min = best_and_worst(datas)
    max_list = []
    min_list = []
    answer_list = []
    for k in range(0, np.size(datas, axis=1)):
        max_sum = 0
        min_sum = 0
        for q in range(0, np.size(datas, axis=0)):
            max_sum += np.power(datas[q, k] - list_max[q], 2)
            min_sum += np.power(datas[q, k] - list_min[q], 2)
        max_list.append(pow(max_sum, 0.5))
        min_list.append(pow(min_sum, 0.5))
        answer_list.append(min_list[k] / (min_list[k] + max_list[k]))
    answer = np.array(answer_list)
    return (answer - np.min(answer)) / (np.max(answer) - np.min(answer))
    # return answer