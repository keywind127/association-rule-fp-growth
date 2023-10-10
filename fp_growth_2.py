from typing import *
import itertools

def powerset(iterable : Iterable[ Any ]) -> itertools.chain:

    iterable = list(iterable)

    return itertools.chain.from_iterable(
        itertools.combinations(iterable, choice) 
            for choice in range(len(iterable) + 1)
    )

class TreeNode(object):

    NULL_LABEL = "null"

    def __init__(self, label  : Optional[ str ] = NULL_LABEL, 
                       count  : Optional[ int ] = 1,
                       parent : Optional[ "TreeNode" ] = None) -> None:

        self.label = label

        self.count = count

        self.children = dict()

        self.parent = parent

        self.friend = None

    def __contains__(self, __obj : Union[ str, "TreeNode" ]) -> bool:

        return (self.children.__contains__(__obj))
    
    def __getitem__(self, label : str) -> "TreeNode":

        return self.children[label]

    def add_child(self, child_node : "TreeNode") -> None:

        self.children[child_node.label] = child_node

    def __eq__(self, __obj : Union[ str, "TreeNode" ]) -> bool:

        if (isinstance(__obj, str)):
            return (__obj == self.label)
        
        return (self.label == __obj.label)
    
    def __repr__(self) -> str:

        return f"({self.label}:{self.count}){self.children}"

def sort_transactions_by_occurrence(transactions : List[ List[ Union[ int, str ] ] ],
                                    leave_trail  : Optional[ bool ] = False) -> Dict[ str, int ]:

    occurrences = dict()

    for transaction in transactions:
        trans_incr_occ = 1
        if (isinstance(transaction[0], int)):
            trans_incr_occ = transaction[0]
            transaction = transaction[1:]
        for item in transaction:
            occurrences[item] = occurrences.get(item, 0) + trans_incr_occ

    indexing = slice(
        (( 1) if (isinstance(transactions[0][0], int)) else (None)),
        ((-1) if (leave_trail)                         else (None))                  
    )

    for transaction in transactions:
        transaction[indexing] = sorted(transaction[indexing], key = occurrences.__getitem__, reverse = True)

    return occurrences

def filter_transactions_by_occurrences(transactions : List[ List[ Union[ int, str ] ] ], 
                                       occurrences  : Dict[ str, int ],
                                       min_sup_int  : int,
                                       leave_trail  : Optional[ bool ] = False) -> None:
    
    indexing = slice(
        (( 1) if (isinstance(transactions[0][0], int)) else (None)),
        ((-1) if (leave_trail)                         else (None))                  
    )

    for transaction in transactions:
        transaction[indexing] = list(filter(lambda x : occurrences[x] >= min_sup_int, transaction[indexing]))

HEADER_OCCU = 0

HEADER_HEAD = 1

HEADER_TAIL = 2

def __construct_tree(headers     : Dict[ str, Tuple[ int, TreeNode, TreeNode ] ], 
                     cur_node    : TreeNode, 
                     transaction : List[ str ], 
                     occurrence  : int) -> None:

    if (len(transaction) == 0):
        return
    
    cur_item = transaction[0]

    if (cur_item in cur_node):

        child_node = cur_node[cur_item]

        child_node.count += occurrence

        headers[cur_item][HEADER_OCCU] += occurrence

        return __construct_tree(headers, child_node, transaction[1:], occurrence)
    
    child_node = TreeNode(label = cur_item, count = occurrence, parent = cur_node)

    cur_node.add_child(child_node)

    if (cur_item in headers):

        headers[cur_item][HEADER_TAIL].friend = child_node

        headers[cur_item][HEADER_TAIL] = child_node

        headers[cur_item][HEADER_OCCU] += occurrence

    else:

        headers[cur_item] = [  occurrence, child_node, child_node  ]

    __construct_tree(headers, child_node, transaction[1:], occurrence)

def construct_tree(transactions : List[ List[ Union[ int, str ] ] ], make_copy : Optional[ bool ] = False
        ) -> Tuple[ TreeNode, Dict[ str, Tuple[ int, TreeNode, TreeNode ] ] ]:

    root = TreeNode(count = -1)

    headers = dict()

    for transaction in transactions:

        #if (make_copy):
        transaction = transaction.copy()

        occurrence = 1

        if (isinstance(transaction[0], int)):
            occurrence = transaction.pop(0)

        __construct_tree(headers, root, transaction, occurrence)

    return (root, headers)

def __find_conditional_pattern_bases(item_node : TreeNode) -> list:

    conditional_pattern_bases = []

    friend_node = item_node

    while (friend_node is not None):

        ascend_node = friend_node

        prefix_path = [  friend_node.count  ]

        while (ascend_node.label != TreeNode.NULL_LABEL):

            prefix_path.insert(1, ascend_node.label)

            ascend_node = ascend_node.parent

        if (prefix_path.__len__() > 2):
            conditional_pattern_bases.append(prefix_path[:-1])

        friend_node = friend_node.friend

    return conditional_pattern_bases

def __mine_patterns(frequent_patterns : list, accum : list, cur_node : TreeNode, min_sup_int : int) -> None:

    conditional_pattern_bases = __find_conditional_pattern_bases(cur_node)

    if (len(conditional_pattern_bases) == 0):
        return

    occurrences = sort_transactions_by_occurrence(conditional_pattern_bases, leave_trail = False)

    filter_transactions_by_occurrences(conditional_pattern_bases, occurrences, min_sup_int, leave_trail = False)

    (_, fp_headers) = construct_tree(conditional_pattern_bases)

    accum_tmp = accum[0]

    for item, header in sorted(fp_headers.items(), key = lambda x : x[1][HEADER_OCCU]):

        accum[0] = min(accum[0], header[HEADER_OCCU])

        if (accum[0] >= min_sup_int):

            accum.insert(1, item)

            frequent_patterns.append(accum.copy())

            __mine_patterns(frequent_patterns, accum, header[HEADER_HEAD], min_sup_int)

            accum.pop(1)

        accum[0] = accum_tmp

def format_frequent_patterns(frequent_patterns : list) -> dict:

    frequent_patterns_dict = dict()

    for frequent_pattern in frequent_patterns:

        tail_item = frequent_pattern[-1]

        path_count = frequent_pattern[0]

        pattern = tuple(frequent_pattern[1:-1])

        if (tail_item in frequent_patterns_dict):
            frequent_patterns_dict[tail_item][pattern] = path_count
        else:
            frequent_patterns_dict[tail_item] = {  pattern : path_count  }

    return frequent_patterns_dict

def mine_patterns(fp_headers : Dict[ str, Tuple[ int, TreeNode, TreeNode ] ], min_sup_int : int
        ) -> Dict[ str, Dict[ Tuple[ str ], int ] ]:

    frequent_patterns = []

    for item, header in sorted(fp_headers.items(), key = lambda x : x[1][HEADER_OCCU]):

        accum = [  header[HEADER_OCCU], item  ]

        frequent_patterns.append(accum.copy())

        __mine_patterns(frequent_patterns, accum, header[HEADER_HEAD], min_sup_int)

    frequent_patterns = format_frequent_patterns(frequent_patterns)

    return frequent_patterns

def mine_frequent_patterns(transactions : List[ List[ str ] ], min_sup_int : int
        ) -> Tuple[ Dict[ str, Dict[ Tuple[ str ], int ] ], Dict[ str, int ] ]:

    occurrences = sort_transactions_by_occurrence(transactions)

    filter_transactions_by_occurrences(transactions, occurrences, min_sup_int)

    _, fp_headers = construct_tree(transactions)

    frequent_patterns = mine_patterns(fp_headers, min_sup_int)

    return (frequent_patterns, occurrences)

if (__name__ == "__main__"):

    transactions = [
        [ '9192', '31651', '45874' ],
        [ '57515', '45874' ],
        [ '45874', '9192' ],
        [ '31651' ]
    ]

    min_sup_int = 1

    # occurrences = sort_transactions_by_occurrence(transactions)

    # #print(transactions)

    # #print(occurrences)

    # filter_transactions_by_occurrences(transactions, occurrences, min_sup_int)

    # #print(transactions)

    # fp_tree, fp_headers = construct_tree(transactions)

    # for item, header in fp_headers.items():

    #     print(item, header[HEADER_OCCU], id(header[HEADER_HEAD]), id(header[HEADER_TAIL]), header[HEADER_HEAD].label, header[HEADER_TAIL].label)

    # frequent_patterns = mine_patterns(fp_headers, min_sup_int)

    # print(frequent_patterns)

    frequent_patterns = mine_frequent_patterns(transactions, min_sup_int)

    print(frequent_patterns)