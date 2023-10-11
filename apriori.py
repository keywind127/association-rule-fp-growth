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

    # empty itemset
    if (len(itemset) == 0):

        # number of transactions
        return len(transactions)

    # number of transactions that are supersets of itemset
    return len(set_intersection(*[  
        occurrences[item][1] 
            for item in itemset  
    ]))



def __find_frequent_patterns(frequent_patterns : Dict[ FrozenSet[ str ], int ], 
                             accumulation      : List[ str ], 
                             remaining         : List[ str ],
                             transactions      : List[ Set[ str ] ],
                             occurrences       : Dict[ str, List[ Union[ int, Tuple[ str ] ] ] ],
                             min_sup_int       : int
            ) -> None:
    
    """This function is called to recursively mine frequent patterns using DFS Apriori Algorithm."""
    
    # zero items left to accumulate
    if (remaining.__len__() == 0):

        # `accumulation` is not empty set
        if (accumulation.__len__()):

            # convert to frozenset to be used as dictionary key
            itemset = frozenset(accumulation)

            # obtain itemset support count
            itemset_support_count = count_itemset_support(
                transactions, 
                occurrences, 
                itemset
            )

            # current itemset is frequent
            if (itemset_support_count >= min_sup_int):

                # save frequent itemset with its corresponding support count
                frequent_patterns[itemset] = itemset_support_count

        # stop recursion
        return 
    
    # convert to frozenset to be used as dictionary key
    itemset = frozenset(accumulation)

    # obtain itemset support count
    itemset_support_count = count_itemset_support(
        transactions, 
        occurrences, 
        itemset
    )

    # current itemset is infrequent
    if (itemset_support_count < min_sup_int):

        # stop recusion
        return
    
    # remove next item from `remaining`
    next_item = remaining.pop(0)

    # recursion: current item not included
    __find_frequent_patterns(
        frequent_patterns, 
        accumulation, 
        remaining, 
        transactions, 
        occurrences,
        min_sup_int
    )

    # add next item to `accumulation`
    accumulation.append(next_item)

    # recursion: current item is included
    __find_frequent_patterns(
        frequent_patterns, 
        accumulation, 
        remaining, 
        transactions, 
        occurrences,
        min_sup_int
    )

    # undo accumulation
    accumulation.pop()
    
    # undo removal
    remaining.insert(0, next_item)



def find_frequent_patterns(transactions : List[ List[ str ] ], 
                           occurrences  : Dict[ str, int ],
                           min_sup_int  : int
            ) -> Dict[ FrozenSet[ str ], int ]:

    """
        Given transactions (list), occurrences (dict) and `min_sup_int` (int), 
        find frequent patterns with their corresponding support counts.
    """

    # initialize dictionary to store frequent patterns with their support counts
    frequent_patterns = dict()

    # initialize empty list to accumulate items
    accumulation = []

    # obtain candidate items to be accumulated (sorted in alphabetical order A->Z)
    remaining = list(map(lambda x : x[0], sorted(occurrences.items(), key = lambda x : x[1][0])))

    # recursively mine frequent patterns using DFS Apriori Algorithm
    __find_frequent_patterns(
        frequent_patterns, 
        accumulation, 
        remaining, 
        transactions, 
        occurrences,
        min_sup_int
    )

    return frequent_patterns



def format_occurrences(occurrences : Dict[ str, List[ Union[ int, Set[ str ] ] ] ]) -> None:

    for item in list(occurrences.keys()):
        occurrences[item] = occurrences[item][0]

    return occurrences



def mine_frequent_patterns(transactions : List[ List[ str ] ], 
                           min_sup_int  : int
            ) -> Tuple[ Dict[ FrozenSet[ str ], int ], Dict[ str, int ] ]:
    
    # obtain occurrences count of each distinct item
    occurrences : dict = count_item_occurrences(transactions)

    # mine frequent patterns satisfying minimum support threshold
    frequent_patterns = find_frequent_patterns(
        transactions, 
        occurrences, 
        min_sup_int
    )

    # remove transaction collection from occurrences dictionary
    format_occurrences(occurrences)

    # frequent patterns (dict) and occurrences of each distinct item (dict)
    return (frequent_patterns, occurrences)



if (__name__ == "__main__"):

    transactions = [
        [ '9192', '31651', '45874' ],
        [ '57515', '45874' ],
        [ '45874', '9192' ],
        [ '31651' ]
    ]

    min_sup_int = 1

    frequent_patterns, occurrences = mine_frequent_patterns(transactions, min_sup_int)

    print(frequent_patterns, occurrences)