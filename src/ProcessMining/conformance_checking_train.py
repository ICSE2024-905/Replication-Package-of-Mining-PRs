import pm4py
import pandas as pd
from ProcessMining.Config import *
from utils.log_utils import get_event_log_from_file, log_info, filter_variants_by_min_total_coverage, process_log
from utils.conformance_checking_algorithm import alignments




'''
Function: Automatically perform consistency checks on all PRs in a specific project
'''
def auto_analyse(scene):
    input_path = f"{SCENE_PROCESS_LOG_DIR}/{scene}_process_log.csv"
    log = get_event_log_from_file(input_path)
    log_info(log)

    variants = filter_variants_by_min_total_coverage(log, COVERAGE_THRESHOLD)
    log = pm4py.filter_variants(log, variants)
    log_info(log)

    petri_net_path = f"{PETRI_NET_DIR}/{scene}_petri_net.pnml"
    traces = alignments(log, petri_net_path)
    df_traces = pd.DataFrame(traces)
    output_path = f"{ALIGNMENTS_DIR}/train_data/{scene}_alignments.csv"
    df_traces.to_csv(output_path, index=False, header=True)
    print(f"{scene} process done")


if __name__ == "__main__":
    scene = "unfork_merge"
    auto_analyse(scene)
