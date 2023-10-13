from typing import *
import copy

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
                        itemset_k    : Dict[ FrozenSet[ str ], Dict[ str, int ] ],
                        min_sup_int  : int) -> List[ Set[ str ] ]:
    
    candidates = dict()

    for prefix, suffix_data in itemset_k.items():

        for item_label, item_support in suffix_data.items():

            for (other_item_label, other_item_support) in itemset_k[prefix].items():

                if (item_label == other_item_label):
                    continue

                if (item_label < other_item_label):
                    new_prefix = { item_label }.union(prefix)
                    new_item_label = other_item_label

                else:
                    new_prefix = { other_item_label }.union(prefix)
                    new_item_label = item_label

                new_item_set = new_prefix.union({ new_item_label })

                new_support = count_itemset_support(transactions, occurrences, new_item_set)

                if (new_support < min_sup_int):
                    continue

                fs_new_prefix = frozenset(new_prefix)

                if (fs_new_prefix in candidates):
                    candidates[fs_new_prefix][new_item_label] = new_support

                else:
                    candidates[fs_new_prefix] = { new_item_label : new_support }

    return candidates


def format_frequent_patterns(frequent_patterns : Dict[ FrozenSet[ str ], Dict[ str, int ] ]):

    formatted = dict()

    for prefix, suffix_data in frequent_patterns.items():
        for item_label, item_support in suffix_data.items():
            formatted[frozenset(prefix.union({ item_label }))] = item_support

    return formatted


def format_occurrences(occurrences : Dict[ str, List[ Union[ int, Set[ str ] ] ] ]) -> None:

    for item in list(occurrences.keys()):
        occurrences[item] = occurrences[item][0]

    return occurrences


def mine_frequent_patterns(transactions : List[ List[ str ] ], 
                           min_sup_int  : int
            ) -> Tuple[ Dict[ FrozenSet[ str ], int ], Dict[ str, int ] ]:
    
    occurrences = count_item_occurrences(transactions)

    frequent_patterns = {
        frozenset({}) : {
            item : count_data[0] 
                for item, count_data in occurrences.items()
                    if (count_data[0] >= min_sup_int)
        }
    }

    itemset_k = copy.deepcopy(frequent_patterns)

    while (itemset_k.__len__()):

        itemset_k = generate_candidates(
            transactions, 
            occurrences, 
            itemset_k, 
            min_sup_int
        )

        frequent_patterns.update(itemset_k)

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