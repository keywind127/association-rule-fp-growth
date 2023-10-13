from typing import *

def argmin(iterable : Iterable, key_funct : Optional[ Callable ] = lambda x : x[1]) -> Tuple[ int, Any ]:
    
    """This function take an iterable and returns the minimum element and its index."""
    return min(enumerate(iterable), key = key_funct)


def set_intersection(*sets_list) -> Set[ Any ]:

    """This function finds the intersection between a list of sets."""

    # index of minimum set
    min_idx : int = argmin(sets_list, lambda x : len(x[1]))[0]

    # the intersection of these sets
    return set.intersection(sets_list[min_idx], *sets_list[None : min_idx], *sets_list[min_idx + 1 : None])


def count_item_occurrences(transactions : List[ List[ Union[ int, str ] ] ]
            ) -> Dict[ str, List[ Union[ int, Set[ int ] ] ] ]:

    """Given a list of transactions, count the number of occurrences of each distinct item."""

    # initialize empty dictionary to record item occurrences
    occurrences = dict()

    # iterate through each transaction
    for tid, transaction in enumerate(transactions):

        # define incremental base unit (default 1)
        occur_incr_unit = 1 

        # integer count is stored in front of transaction
        if (isinstance(transaction[0], int)):

            # override incremental base unit
            occur_incr_unit = transaction[0]

            # ignore first element since it is not an item
            transaction = transaction[1:]

        # iterate through each item
        for item in transaction:

            # item already in dictionary
            if (item in occurrences):

                # increment item occurrences count
                occurrences[item][0] += occur_incr_unit

                # add tid to transaction collection
                occurrences[item][1].add(tid)

            else:

                # initialize item in dictionary with [  OCCURRENCES, TID_SET  ]
                occurrences[item] = [  
                    occur_incr_unit, set([ tid ])  
                ]

    return occurrences



def count_itemset_support(transactions : List[ Set[ str ] ], 
                          occurrences  : Dict[ str, List[ Union[ int, Set[ str ] ] ] ],
                          itemset      : Set[ str ]
            ) -> int:

    """Given a list of transactions and an itemset, find the support count of this itemset."""

    count = 0

    for transaction in transactions:

        count += itemset.issubset(transaction)
    
    return count

    # empty itemset
    if (len(itemset) == 0):

        # number of transactions
        return len(transactions)

    # number of transactions that are supersets of itemset
    return len(set_intersection(*[  
        occurrences[item][1] 
            for item in itemset  
    ]))


def generate_candidates(transactions : List[ List[ str ] ], 
                        occurrences  : Dict[ str, List[ Union[ int, Set[ str ] ] ] ], 
                        itemset_k    : List[ List[ Union[ List[ str ], int ] ] ],
                        min_sup_int  : int) -> List[ Set[ str ] ]:
    
    num_items = len(itemset_k)

    candidates = []

    k_1 = len(itemset_k[0][0])

    for i in range(num_items - 1):

        for j in range(i + 1, num_items):

            if (k_1 > 1):

                if any((itemset_k[i][0][idx] != itemset_k[j][0][idx]) for idx in range(k_1 - 1)):
                    continue

            candidate = itemset_k[i][0] + [ itemset_k[j][0][-1] ]

            candidate_support = count_itemset_support(transactions, occurrences, set(candidate))

            if (candidate_support < min_sup_int):
                continue

            candidates.append([ candidate.copy(), candidate_support ])

    return candidates


def format_frequent_patterns(frequent_patterns : List[ Tuple[ FrozenSet[ str ], int ] ]):

    formatted = dict()

    for itemset, support_count in frequent_patterns:
        formatted[frozenset(itemset)] = support_count

    return formatted


def format_occurrences(occurrences : Dict[ str, List[ Union[ int, Set[ str ] ] ] ]) -> None:

    for item in list(occurrences.keys()):
        occurrences[item] = occurrences[item][0]

    return occurrences


def mine_frequent_patterns(transactions : List[ List[ str ] ], 
                           min_sup_int  : int
            ) -> Tuple[ Dict[ FrozenSet[ str ], int ], Dict[ str, int ] ]:
    
    occurrences = count_item_occurrences(transactions)

    frequent_patterns = [
        [[ item ], count_data[0]] for item, count_data in occurrences.items()
            if (count_data[0] >= min_sup_int)
    ]

    itemset_k = frequent_patterns.copy()

    while (itemset_k):

        itemset_k = generate_candidates(
            transactions, 
            occurrences, 
            itemset_k, 
            min_sup_int
        )

        frequent_patterns += itemset_k

    format_occurrences(occurrences)

    return (format_frequent_patterns(frequent_patterns), occurrences)

if (__name__ == "__main__"):

    transactions = [
        [ '9192', '31651', '45874' ],
        [ '57515', '45874' ],
        [ '45874', '9192' ],
        [ '31651' ]
    ]

    min_sup_int = 1

    frequent_patterns = mine_frequent_patterns(transactions, min_sup_int)

    print(frequent_patterns)