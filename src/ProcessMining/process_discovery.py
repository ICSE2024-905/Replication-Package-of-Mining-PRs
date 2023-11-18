import pm4py
from ProcessMining.Config import *
from utils.process_discovery_algorithm import inductive_mining
from utils.process_model_evaluation import model_evaluation
from utils.log_utils import *


'''
Function: Use a specific process discovery algorithm to construct the mainstream model under a specific scene using the project list repos.
'''
def process_discovery_inductive(scene, algorithm_params):
    petri_net_filename = f"{PETRI_NET_DIR}/{scene}_petri_net"
    bpmn_filename = f"{BPMN_DIR}/{scene}_bpmn"

    input_path = f"{SCENE_PROCESS_LOG_DIR}/{scene}_process_log.csv"
    log = get_event_log_from_file(input_path)
    log_info(log)

    variants = filter_variants_by_min_total_coverage(log, min_coverage=COVERAGE_THRESHOLD)
    log = pm4py.filter_variants(log, variants)
    log_info(log)

    petri_net, im, fm = inductive_mining(log, petri_net_filename, bpmn_filename, algorithm_params)

    fitness, precision, generalization, simplicity = model_evaluation(log, petri_net, im, fm)

    case_num, variant_num = log_info(log)
    model_evaluation_result = [scene, case_num, variant_num, fitness['average_trace_fitness'],
                               fitness['percentage_of_fitting_traces'], precision, generalization, simplicity]
    output_path = f"{MODEL_EVALUATION_DIR}/{scene}_model_evaluation_result.csv"
    columns = ['scene', 'case_num', 'variant_num', 'average_trace_fitness', 'percentage_of_fitting_traces', 'precision',
               'generalization', 'simplicity']
    df_file = pd.DataFrame(data=[model_evaluation_result], columns=columns)
    df_file.to_csv(output_path, index=False, header=True)


if __name__ == "__main__":
    scene = "fork_merge"
    algorithm_param = "noise_threshold=0.1"

    process_discovery_inductive(scene, algorithm_param)
    print(f"{scene} process done")

