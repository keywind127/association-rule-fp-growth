from typing import *
import re

def preprocess_transactions(input_data : List[ List[ int ] ]) -> List[ List[ int ] ]:

    transactions = dict()

    for tid_1, _, item in input_data:

        if (tid_1 in transactions):
            transactions[tid_1].append(item)
            continue 

        transactions[tid_1] = [ item ]    

    return list(transactions.values())

def load_file(filename : str) -> List[ List[ str ] ]:

    with open(filename, mode = "r", encoding = "utf-8") as rf:

        file_data = list(map(lambda x : re.findall("[a-zA-Z0-9]+", x), filter("".__ne__, rf.read().splitlines())))

        return file_data

def post_process_mined_rules(occurrences : Dict[ str, int ],
                             mined_rules : Set[ Tuple[ FrozenSet[ Any ], FrozenSet[ Any ], float, int ] ],
                             min_conf_float : float,
                             num_transactions : int):
    
    post_processed_rules = list()

    for association_rule in mined_rules:

        antecedent = sorted(association_rule[0], key = occurrences.__getitem__, reverse = True)

        conseqeunt = sorted(association_rule[1], key = occurrences.__getitem__, reverse = True)

        confidence = association_rule[3]

        support_rt = association_rule[2] #/ num_transactions

        confi_lift = association_rule[4] #confidence / min_conf_float

        post_processed_rules.append((
            antecedent, 
            conseqeunt, 
            round(support_rt, 2), 
            round(confidence, 2),
            round(confi_lift, 2)
        ))

    return post_processed_rules

if (__name__ == "__main__"):

    # input_data = [
    #     [ '1', '1', '9192'  ],
    #     [ '1', '1', '31651' ],
    #     [ '2', '2', '26134' ],
    #     [ '2', '2', '57515' ],
    # ]

    # transactions = preprocess_transactions(input_data)

    # print(transactions)

    file_name = "test_data/ibm-2023-released.txt"

    input_data = load_file(file_name)

    print(input_data)
