from ProcessAnomalyPR.Config import *
from utils.log_utils import *

'''
Function: Count the variants of each PR case in the event log in sequence and number them
'''
def cal_log_variant(scene):
    input_path = f"../ProcessMining/scene_process_log/{scene}_process_log.csv"
    log = get_event_log_from_file(input_path)
    variant_dic = {}
    index = 1
    datas = []
    for case_id, group in log.groupby('case:concept:name'):
        variant = tuple(group['concept:name'].tolist())
        if variant not in variant_dic:
            variant_dic[variant] = index
            index += 1
        datas.append([case_id, variant, variant_dic[variant]])
    df = pd.DataFrame(data=datas, columns=['case_id', 'variant', 'variant_id'])
    output_path = f"{LOG_VARIANTS_DIR}/{scene}_log_variant.csv"
    df.to_csv(output_path, index=False, header=True)


if __name__ == '__main__':
    for scene in PR_TYPES:
        cal_log_variant(scene)
        print(f"{scene} process done")