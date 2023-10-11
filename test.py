from utilities import load_file, preprocess_transactions, post_process_mined_rules
#from fp_growth_2 import mine_frequent_patterns
from apriori import mine_frequent_patterns
from mine_asso_rules import mine_association_rules
import datetime
#import pickle

if (__name__ == "__main__"):

    SOT = datetime.datetime.now()

    max_transactions = 10000

    filename = "test_data/ibm-2023-released.txt"

    input_data = load_file(filename)

    transactions = preprocess_transactions(input_data)

    max_transactions = min(max_transactions, len(transactions))

    transactions[:] = transactions[:max_transactions]

    min_sup_float = 0.05

    print("MAX TRANS:", max_transactions)

    min_sup_int = max_transactions * min_sup_float

    print("MIN SUP INT:", min_sup_int)

    min_conf_float = 0.07

    frequent_patterns, occurrences = mine_frequent_patterns(transactions, min_sup_int)

    print(
        frequent_patterns[frozenset([ "14" ])], 
        frequent_patterns[frozenset([ "18" ])],
        frequent_patterns[frozenset([ "14", "18" ])]
    )

    # print(frequent_patterns["14"][()], frequent_patterns["18"][()], frequent_patterns["18"].get(("14", ), -1))

    #with open("d.txt", "w", encoding = "utf-8") as wf:

    #    for pattern in frequent_patterns["14"]:

    #        wf.write(f"{pattern}")

    #with open("e.pickle", "wb") as wf:

    #    pickle.dump(frequent_patterns, wf, protocol = pickle.HIGHEST_PROTOCOL)

    association_rules = mine_association_rules(frequent_patterns, min_conf_float, max_transactions)

    post_processed = post_process_mined_rules(occurrences, association_rules, min_conf_float, max_transactions)

    print(len(association_rules))

    print(f"Elapsed Time: {(datetime.datetime.now() - SOT).total_seconds()}")

    with open("c.txt", "w") as wf:

        for row in post_processed:

            for item in row:

                wf.write(f"{item} ")

            wf.write("\n")