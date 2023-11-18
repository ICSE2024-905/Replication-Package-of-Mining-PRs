import pandas as pd
from NormalProcessModel.Config import *
from utils.process_discovery_algorithm import inductive_mining
from utils.process_model_evaluation import model_evaluation
from utils.log_utils import get_event_log_from_file, log_info, process_log


'''
Function: Use a specific process discovery algorithm to construct the mainstream model under a specific scene using the project list repos.
'''
def process_discovery_inductive(log, label, scene: str, params: str):
    petri_net_filename = f"{PETRI_NET_DIR}/normal/{scene}_petri_net_cluster_{label}"
    bpmn_filename = f"{BPMN_DIR}/normal/{scene}_bpmn_cluster_{label}"

    petri_net, im, fm = inductive_mining(log, petri_net_filename, bpmn_filename, params)

    fitness, precision, generalization, simplicity = model_evaluation(log, petri_net, im, fm)

    return [fitness['average_trace_fitness'], fitness['percentage_of_fitting_traces'], precision, generalization, simplicity]


'''

Function: Automated process (clustering logs corresponding to scenarios)
'''
def auto_analysis(scene, algorithm_param):
    log_path = f"{NORMAL_PROCESS_LOG_DIR}/{scene}_process_log.csv"
    df_log = get_event_log_from_file(log_path)

    df_log = process_log(scene, df_log)

    input_path = f"{NORMAL_CLUSTER_DIR}/{scene}_cluster.csv"
    df = pd.read_csv(input_path)
    df['case_id'] = df.apply(lambda x: x['repo'] + '#' + str(x['pr_number']), axis=1)

    model_evaluation_result = []
    for label in df['label'].unique():
        df_cluster = df.loc[df['label'] == int(label)]
        cluster_case_ids = df_cluster['case_id'].tolist()
        log = df_log[df_log['case:concept:name'].isin(cluster_case_ids)]
        case_number, variant_number = log_info(log)
        res = process_discovery_inductive(log, label, scene, algorithm_param)
        single_result = [scene, label, case_number, variant_number]
        single_result.extend(res)
        model_evaluation_result.append(single_result)
        print(f"{scene} cluster {label} process done")

    output_path = f"{CLUSTER_MODEL_EVALUATION_DIR}/{scene}_model_evaluation_result.xls"
    columns = ['scene', 'cluster', 'case_num', 'variant_num', 'average_trace_fitness', 'percentage_of_fitting_traces', 'precision', 'generalization', 'simplicity']
    df_file = pd.DataFrame(data=model_evaluation_result, columns=columns)
    df_file.to_excel(output_path, index=False, header=True)


if __name__ == "__main__":
    scene = "fork_merge"
    algorithm_param = "noise_threshold=0.1"
    auto_analysis(scene, algorithm_param)

