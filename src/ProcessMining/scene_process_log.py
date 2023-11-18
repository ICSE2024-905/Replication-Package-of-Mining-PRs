import pandas as pd
import os
from ProcessMining.Config import *


'''
Function: Merge repeated and continuous activities into one, such as: (ReviewComment,ReviewComment) into ReviewComment
'''
def merge_repetitive_activity(log):
    datas = []
    for pr_number, group in log.groupby('case:concept:name'):
        total = group.shape[0]
        idx = 0
        while idx < total:
            cur_activity = group.iloc[idx, 1]
            cur_start_time = group.iloc[idx, 2]
            cur_people = group.iloc[idx, 3]
            cur_scene = group.iloc[idx, 4]

            nextIdx = idx + 1
            while nextIdx < total:
                next_activity = group.iloc[nextIdx, 1]
                next_start_time = group.iloc[nextIdx, 2]
                next_people = group.iloc[nextIdx, 3]
                if (next_activity == cur_activity) and (next_people == cur_people):
                    nextIdx += 1
                else:
                    break

            cur_end_time = group.iloc[nextIdx - 1, 2]
            cur_num = nextIdx - idx
            cur_record = [pr_number, cur_activity, cur_start_time, cur_end_time, cur_people, cur_scene, cur_num]
            datas.append(cur_record)

            idx = nextIdx

    df_log = pd.DataFrame(data=datas, columns=['case:concept:name', 'concept:name', 'time:timestamp', 'endtime', 'people', 'scene', 'num'])
    return df_log


'''
Function: Filter out the event log of a specific scene from repos and splice it into the log
'''
def get_event_log(repos, scene):
    log = pd.DataFrame()
    for repo in repos:
        input_path = f"{PROCESS_LOG_DIR}/{repo}_process_log.csv"
        if not os.path.exists(input_path):
            print(f"{input_path} don't exist")
            continue
        df = pd.read_csv(input_path, parse_dates=['time:timestamp'])
        df = df.loc[df['scene'] == scene]
        df['case:concept:name'] = df['case:concept:name'].apply(lambda x: repo + '#' + str(x))
        log = pd.concat([log, df], ignore_index=True)
    log = merge_repetitive_activity(log)
    output_path = f"{SCENE_PROCESS_LOG_DIR}/{scene}_process_log.csv"
    log.to_csv(output_path, index=False, header=True, encoding="utf-8-sig")


if __name__ == "__main__":
    projects = ['openzipkin/zipkin', 'apache/netbeans', 'opencv/opencv', 'apache/dubbo', 'phoenixframework/phoenix',
                'apache/zookeeper', 'spring-projects/spring-framework', 'spring-cloud/spring-cloud-function',
                'vim/vim', 'gpac/gpac', 'ImageMagick/ImageMagick', 'apache/hadoop', 'libexpat/libexpat',
                'apache/httpd', 'madler/zlib', 'redis/redis', 'stefanberger/swtpm', 'tensorflow/tensorflow']
    repos = []
    for pro in projects:
        repo = pro.split('/')[1]
        repos.append(repo)

    for scene in PR_TYPES:
        get_event_log(repos, scene)
        print(f"{scene} process done")
