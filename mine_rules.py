from main import powerset
from typing import *

def frequent_itemset_as_tuples(frequent_itemsets : Dict[ Any, Dict[ Tuple[ Any ], int ] ]) -> Set[ Tuple[ Any ] ]:

    itemsets = set()

    for tail_item, prefix_paths in frequent_itemsets.items():
        for prefix_path, _ in prefix_paths.items():
            itemsets.add((*prefix_path, tail_item))

    return itemsets

def _mine_association_rules(rules_list : List[ Tuple[ FrozenSet[ Any ], FrozenSet[ Any ] ] ],
                           frequent_itemset_support : Dict[ Any, Dict[ Tuple[ Any ], int ] ],
                           antecedent : Dict[ Any, int ], consequent : Dict[ Any, int ],
                           master_support : int, min_conf_float : float, master_len : int):

    if (consequent.__len__() and antecedent.__len__()):

        _ant = {  v : k for k, v in antecedent.items()  }

        #print(_ant)

        ant_support = tuple(_ant[x] for x in range(master_len) if x in _ant)

        #print(ant_support)

        ant_support = frequent_itemset_support[ant_support[-1]][ant_support[:-1]]

        confidence = master_support / ant_support

        if (confidence >= min_conf_float):

            rules_list.append((frozenset(antecedent.keys()), frozenset(consequent.keys()), confidence, master_support))

    for item, indx in list(antecedent.items()):

        consequent[item] = indx
        del antecedent[item]

        _mine_association_rules(rules_list, frequent_itemset_support, antecedent, 
            consequent, master_support, min_conf_float, master_len)

        antecedent[item] = indx
        del consequent[item]

def mine_association_rules(frequent_itemset_list : Set[ Tuple[ Any ] ], frequent_itemset_support : dict, min_conf_float : float):

    association_rules = []

    for frequent_itemset in frequent_itemset_list:

        master_support = frequent_itemset_support[frequent_itemset[-1]][frequent_itemset[:-1]]

        frequent_itemset = {  val : idx for idx, val in enumerate(frequent_itemset)  }

        _mine_association_rules(association_rules, frequent_itemset_support, frequent_itemset, 
                                dict(), master_support, min_conf_float, len(frequent_itemset))

    return association_rules

if (__name__ == "__main__"):

    frequent_itemsets = {45874: {(): 3}, 9192: {(): 2, (45874,): 2}, 31651: {(): 2, (45874,): 1, (9192,): 1, (45874, 9192): 1}, 57515: {(): 1, (45874,): 1}}

    frequent_itemsets_list = frequent_itemset_as_tuples(frequent_itemsets)

    min_conf_float = 0.2

    asso_rules = mine_association_rules(frequent_itemsets_list, frequent_itemsets, min_conf_float)

    print(asso_rules)