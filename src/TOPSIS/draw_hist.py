import matplotlib.pyplot as plt
import pandas as pd
from TOPSIS.Config import *

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fsize = 18

'''
Function: Personnel dimension, histogram plots the distribution of scores of people with different types of permission changes
'''
def draw_topsis_result(role):
    input_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df = pd.read_excel(input_path)
    scores = df['score'].values

    output_path = f"{FIGURE_DIR}/{role}_topsis_score.pdf"
    plt.xlabel("Comprehensive evaluation score",fontsize=fsize)
    plt.ylabel("Number of people",fontsize=fsize)
    plt.tick_params(labelsize=fsize)
    a, b, c = plt.hist(scores, bins=30)
    plt.subplots_adjust(left=0.11, right=0.98, top=0.98, bottom=0.13)
    # plt.show()
    plt.savefig(output_path)
    plt.cla()
    plt.close()


'''
Function: Project dimension, box and whisker plot plots the distribution of ratings of personnel who have changed permissions in different projects
'''
def score_boxplot_on_repos(role):
    input_path = f"{SUMMARY_DIR}/{role}_topsis_result.xls"
    df = pd.read_excel(input_path)
    repos = df['repo'].unique().tolist()
    scores = []
    repos.sort()
    for repo in repos:
        sl = df.loc[df['repo'] == repo]['score'].tolist()
        scores.append(sl)
    plt.boxplot(scores, labels=repos)
    plt.xticks(rotation=-90)
    # plt.tick_params(labelsize=fsize)
    plt.xlabel("project")
    plt.ylabel("Comprehensive evaluation score")
    plt.subplots_adjust(left=0.085, right=0.98, top=0.98, bottom=0.37)
    output_path = f"{FIGURE_DIR}/{role}_topsis_score_on_repos.pdf"
    plt.savefig(output_path)
    plt.cla()
    plt.close()
    # plt.show()

if __name__ == '__main__':
    # draw_topsis_result("maintainer")

    score_boxplot_on_repos("reviewer")