import pm4py



def alignments(log, petri_net_path):
    net, initial_marking, final_marking = pm4py.read_pnml(petri_net_path)
    traces = []
    index = 1
    total = len(log['case:concept:name'].unique())
    for case_id, group in log.groupby('case:concept:name'):
        trace = pm4py.conformance_diagnostics_alignments(group, net, initial_marking, final_marking)
        trace[0]['case_id'] = case_id
        traces.append(trace[0])
        print(f"{index}/{total} process done")
        index += 1
    return traces