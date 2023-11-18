import pm4py
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator


def model_evaluation(log, petri_net, initial_marking, final_marking):
    fitness = pm4py.fitness_token_based_replay(log, petri_net, initial_marking, final_marking)
    precision = pm4py.precision_token_based_replay(log, petri_net, initial_marking, final_marking)
    precision = pm4py.precision_alignments(log, petri_net, initial_marking, final_marking)
    generalization = generalization_evaluator.apply(log, petri_net, initial_marking, final_marking)
    simplicity = simplicity_evaluator.apply(petri_net)

    print("fitness")
    print("\taverage_trace_fitness:%.3f" % fitness['average_trace_fitness'])
    print("\tpercentage_of_fitting_traces:%.3f" % fitness['percentage_of_fitting_traces'])

    print("precision:%.3f" % precision)

    print("generalization:%.3f" % generalization)

    print("simplicity:%.3f" % simplicity)
    print()

    return fitness, precision, generalization, simplicity
