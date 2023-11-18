import pm4py


def inductive_mining(log,
                     petri_net_filename: str,
                     bpmn_filename: str,
                     params: str):
    params_dic = {"noise_threshold": 0.0}
    pArr = params.split("=")
    if pArr[0] in params_dic:
        params_dic[pArr[0]] = float(pArr[1])
    print(params_dic)

    # Petri-Net
    petri_net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold=params_dic[
        "noise_threshold"])
    pm4py.write_pnml(petri_net, initial_marking, final_marking, f"{petri_net_filename}.pnml")
    pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, f"{petri_net_filename}.png")

    bpmn = pm4py.convert_to_bpmn(petri_net, initial_marking, final_marking)
    pm4py.write_bpmn(bpmn, f"{bpmn_filename}.bpmn")
    pm4py.save_vis_bpmn(bpmn, f"{bpmn_filename}.png")

    return petri_net, initial_marking, final_marking



def alpha_mining(log,
                 petri_net_filename: str,
                 bpmn_filename: str):
    # Petri-Net
    petri_net, initial_marking, final_marking = pm4py.discover_petri_net_alpha(log)
    pm4py.write_pnml(petri_net, initial_marking, final_marking, f"{petri_net_filename}.pnml")
    pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, f"{petri_net_filename}.png")

    bpmn = pm4py.convert_to_bpmn(petri_net, initial_marking, final_marking)
    pm4py.write_bpmn(bpmn, f"{bpmn_filename}.bpmn")
    pm4py.save_vis_bpmn(bpmn, f"{bpmn_filename}.png")

    return petri_net, initial_marking, final_marking


def heuristics_mining(log,
                      heuristics_net_filepath: str,
                      petri_net_filename: str,
                      bpmn_filename: str,
                      params: str):
    params_dic = {
        "dependency_threshold": 0.5,
        "and_threshold": 0.65,
        "loop_two_threshold": 0.5
    }
    for p in params.split(","):
        pArr = p.split("=")
        if pArr[0] in params_dic:
            params_dic[pArr[0]] = float(pArr[1])
    print(params_dic)

    heuristics_net = pm4py.discover_heuristics_net(log,
                                                   dependency_threshold=params_dic["dependency_threshold"],
                                                   and_threshold=params_dic["and_threshold"],
                                                   loop_two_threshold=params_dic["loop_two_threshold"])
    pm4py.save_vis_heuristics_net(heuristics_net, heuristics_net_filepath)

    petri_net, initial_marking, final_marking = pm4py.convert_to_petri_net(heuristics_net)
    pm4py.write_pnml(petri_net, initial_marking, final_marking, f"{petri_net_filename}.pnml")
    pm4py.save_vis_petri_net(petri_net, initial_marking, final_marking, f"{petri_net_filename}.png")

    bpmn = pm4py.convert_to_bpmn(petri_net, initial_marking, final_marking)
    pm4py.write_bpmn(bpmn, f"{bpmn_filename}.bpmn")
    pm4py.save_vis_bpmn(bpmn, f"{bpmn_filename}.png")

    return petri_net, initial_marking, final_marking