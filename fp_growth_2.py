from typing import *

class TreeNode(object):

    NULL_LABEL = "null"

    def __init__(self, label  : Optional[ str ] = NULL_LABEL, 
                       count  : Optional[ int ] = 1,
                       parent : Optional[ "TreeNode" ] = None) -> None:

        self.label    : str      = label

        self.count    : int      = count

        self.children : dict     = dict()

        self.parent   : TreeNode = parent

        self.friend   : TreeNode = None

    def __contains__(self, __obj : Union[ str, "TreeNode" ]) -> bool:

        """Checks whether node contains such a child node."""
        return (self.children.__contains__(__obj))
    
    def __getitem__(self, label : str) -> "TreeNode":

        """Retrieves a child node by string label."""
        return self.children[label]

    def add_child(self, child_node : "TreeNode") -> None:

        """Adds a child node to current node."""
        self.children[child_node.label] = child_node

    def __eq__(self, __obj : Union[ str, "TreeNode" ]) -> bool:

        """Checks whether node labels match."""
        if (isinstance(__obj, str)):
            return (__obj == self.label)
        
        return (self.label == __obj.label)
    
    def __repr__(self) -> str:

        """Used to print out FP-Tree structure."""
        return f"({self.label}:{self.count}){self.children}"



def sort_transactions_by_occurrence(transactions : List[ List[ Union[ int, str ] ] ],
                                    leave_trail  : Optional[ bool ] = False
            ) -> Dict[ str, int ]:

    # initialization of an empty dictionary to be used to count item occurrences
    occurrences = dict()

    # do the following for each transaction
    for transaction in transactions:

        # amount to increment by
        trans_incr_occ = 1

        # extract transaction count if first item is an integer
        if (isinstance(transaction[0], int)):

            # set transaction count to be used for increment
            trans_incr_occ = transaction[0]

            # the remaining section of transaction (excluding integer count)
            transaction = transaction[1:]

        # increment occurrences count of current item
        for item in transaction:
            occurrences[item] = occurrences.get(item, 0) + trans_incr_occ

    # specifying the range of list to sort (e.q.) [:], [:-1], [1:], [1:-1]
    indexing = slice(
        (( 1) if (isinstance(transactions[0][0], int)) else (None)),
        ((-1) if (leave_trail)                         else (None))                  
    )

    # sort each transaction based on occurrences in non-increasing order
    for transaction in transactions:
        transaction[indexing] = sorted(transaction[indexing], key = occurrences.__getitem__, reverse = True)

    return occurrences



def filter_transactions_by_occurrences(transactions : List[ List[ Union[ int, str ] ] ], 
                                       occurrences  : Dict[ str, int ],
                                       min_sup_int  : int,
                                       leave_trail  : Optional[ bool ] = False) -> None:
    
    # specifying the range of list to sort (e.q.) [:], [:-1], [1:], [1:-1]
    indexing = slice(
        (( 1) if (isinstance(transactions[0][0], int)) else (None)),
        ((-1) if (leave_trail)                         else (None))                  
    )

    # filter out items from transactions with support lower than minimum threshold
    for transaction in transactions:
        transaction[indexing] = list(filter(lambda x : occurrences[x] >= min_sup_int, transaction[indexing]))



# index of occurrence count in header (friend link)
HEADER_OCCU = 0

# index of head node in header (friend link)
HEADER_HEAD = 1

# index of tail node in header (friend link)
HEADER_TAIL = 2



def __construct_tree(headers     : Dict[ str, Tuple[ int, TreeNode, TreeNode ] ], 
                     cur_node    : TreeNode, 
                     transaction : List[ str ], 
                     occurrence  : int) -> None:

    # recursion base case => no more items in transaction
    if (len(transaction) == 0):
        return
    
    # next immediate item
    cur_item = transaction[0]

    # current node already contains a child node labeled as such
    if (cur_item in cur_node):

        # fetch reference to this child node
        child_node = cur_node[cur_item]

        # increment child node count by (an integer) `occurrence``
        child_node.count += occurrence

        # increment item node count in headers (friend link)
        headers[cur_item][HEADER_OCCU] += occurrence

        # finish constructing FP-Tree with the remaining items and return
        return __construct_tree(headers, child_node, transaction[1:], occurrence)
    
    # create a new child node for current node whose count equals to `occurrence` and parent to current node
    child_node = TreeNode(label = cur_item, count = occurrence, parent = cur_node)

    # add this new child node to current node's collection of children nodes
    cur_node.add_child(child_node)

    # current item already added to headers (friend link)
    if (cur_item in headers):

        """
            Append new child node to tail of friend linked list in headers (friend link)
        """

        headers[cur_item][HEADER_TAIL].friend = child_node

        headers[cur_item][HEADER_TAIL] = child_node

        # increment item node count in headers (friend link)
        headers[cur_item][HEADER_OCCU] += occurrence

    else:

        # initialize headers at `cur_item` with a list of three things [ OCCU, HEAD, TAIL ]
        headers[cur_item] = [  occurrence, child_node, child_node  ]

    # finish constructing FP-Tree with the remaining items and return
    __construct_tree(headers, child_node, transaction[1:], occurrence)



def construct_tree(transactions : List[ List[ Union[ int, str ] ] ], 
                   make_copy    : Optional[ bool ] = False
            ) -> Tuple[ TreeNode, Dict[ str, Tuple[ int, TreeNode, TreeNode ] ] ]:

    # initialize the dummy root node of FP-Tree
    root = TreeNode(count = -1)

    # initialize empty dictionary to store header data (friend links)
    headers = dict()

    # do for each transaction
    for transaction in transactions:

        """
            Modify on a copy of the transaction if specified
        """

        if (make_copy):
            transaction = transaction.copy()

        # amount to increment by
        occurrence = 1

        # set occurrence if first element in transaction if it is an integer
        if (isinstance(transaction[0], int)):
            occurrence = transaction.pop(0)

        # recursively construct the FP-Tree with the current transaction
        __construct_tree(headers, root, transaction, occurrence)

    # return root of FP-Tree and the headers (friend links)
    return (root, headers)



def __find_conditional_pattern_bases(item_node : TreeNode) -> List[ List[ Union[ int, str ] ] ]:

    # list of conditional pattern bases
    conditional_pattern_bases = []

    """
        Iterate through friend nodes
    """

    friend_node = item_node

    while (friend_node is not None):

        """
            Ascend from friend node to null root
        """

        ascend_node = friend_node

        # storing path width as first element in prefix path
        prefix_path = [  friend_node.count  ]

        # do until reaching null root
        while (ascend_node.label != TreeNode.NULL_LABEL):

            # insert item label after path width (starting from index 1)
            prefix_path.insert(1, ascend_node.label)

            # ascend upwards toward the root
            ascend_node = ascend_node.parent

        # add prefix path to conditional pattern bases if more than 1 items [ count, item1, item2, ... ]
        if (prefix_path.__len__() > 2):
            conditional_pattern_bases.append(prefix_path[:-1])

        # shift to next node in friend link
        friend_node = friend_node.friend

    # return the conditional pattern bases
    return conditional_pattern_bases



def __mine_patterns(frequent_patterns : List[ List[ Union[ int, str ] ] ], 
                    accum             : List[ Union[ int, str ] ], 
                    cur_node          : TreeNode, 
                    min_sup_int       : int                             
            ) -> None:

    # find the conditional pattern bases
    conditional_pattern_bases : list = __find_conditional_pattern_bases(cur_node)

    # recursion base case, no more pattern bases to build conditional FP-Trees
    if (len(conditional_pattern_bases) == 0):
        return

    # sort conditional pattern bases as though they are transactions, and store occurrences
    occurrences : dict = sort_transactions_by_occurrence(conditional_pattern_bases, leave_trail = False)

    # filter items from conditional pattern bases with support count lower than minimum threshold
    filter_transactions_by_occurrences(conditional_pattern_bases, occurrences, min_sup_int, leave_trail = False)

    # headers containing occurrences and friend links of each item
    fp_headers : list = construct_tree(conditional_pattern_bases)[1]

    # temporarily store the original minimum path width prior to modification
    accum_tmp : int = accum[0]

    # do the following for each item in headers in non-decreasing order (by occurrences)
    for item, header in sorted(fp_headers.items(), key = lambda x : x[1][HEADER_OCCU]):

        # update minimum width of current path (itemset)
        accum[0] = min(accum[0], header[HEADER_OCCU])

        # current itemset is a frequent itemset
        if (accum[0] >= min_sup_int):

            # prepend item to path list (right after path width, which is at index 0)
            accum.insert(1, item)

            # store frequent itemset in frequent patterns
            frequent_patterns.append(accum.copy())

            # mine the remaining items to be added to path list
            __mine_patterns(frequent_patterns, accum, header[HEADER_HEAD], min_sup_int)

            # undo insertion of current item to path list
            accum.pop(1)

        # restore minimum width for next iteration
        accum[0] = accum_tmp



def format_frequent_patterns(frequent_patterns : List[ List[ Union[ int, str ] ] ]
            #) -> Dict[ str, Dict[ Tuple[ str ], int ] ]:
            ) -> Dict[ FrozenSet[ str ], int ]:

    # initialization of empty dictionary to store formatted frequent itemsets with occurrences
    frequent_patterns_dict = dict()

    # do the following for each frequent itemset
    for frequent_pattern in frequent_patterns:

        # use the tail item as key
        tail_item  : str   = frequent_pattern[-1]

        # extract path width (support count)
        path_count : int   = frequent_pattern[0]

        # format prefix path into tuple
        pattern    : tuple = tuple(frequent_pattern[1:-1])

        """
            Add frequent itemset to collection
        """

        # if (tail_item in frequent_patterns_dict):
        #     frequent_patterns_dict[tail_item][pattern] = path_count
        # else:
        #     frequent_patterns_dict[tail_item] = {  pattern : path_count  }

        frequent_patterns_dict[frozenset([ *pattern, tail_item ])] = path_count

    # return formatted patterns
    return frequent_patterns_dict



def mine_patterns(fp_headers  : Dict[ str, Tuple[ int, TreeNode, TreeNode ] ], 
                  min_sup_int : int
            ) -> Dict[ str, Dict[ Tuple[ str ], int ] ]:

    frequent_patterns = []

    # do the following for each item in non-decreasing order by occurrences
    for item, header in sorted(fp_headers.items(), key = lambda x : x[1][HEADER_OCCU]):

        # initialize `accum` with [ path_width : int, item_label : str ]
        accum = [  header[HEADER_OCCU], item  ]

        # save frequent 1-itemset
        frequent_patterns.append(accum.copy())

        # mine the remaining patterns to be added
        __mine_patterns(frequent_patterns, accum, header[HEADER_HEAD], min_sup_int)

    # hash frequent patterns into a dictionary for easy lookup
    frequent_patterns : dict = format_frequent_patterns(frequent_patterns)

    return frequent_patterns



def mine_frequent_patterns(transactions : List[ List[ str ] ], 
                           min_sup_int  : int
            ) -> Tuple[ Dict[ str, Dict[ Tuple[ str ], int ] ], Dict[ str, int ] ]:

    # sort transactions by occurrences in non-increasing order and save occurrences dictionary
    occurrences : dict = sort_transactions_by_occurrence(transactions)

    # filter infrequent items in transactions
    filter_transactions_by_occurrences(transactions, occurrences, min_sup_int)

    # construct FP-Tree and save the header data (friend links)
    fp_headers : list = construct_tree(transactions)[1]

    # mine the frequent patterns (itemsets) given FP-Tree
    frequent_patterns : dict = mine_patterns(fp_headers, min_sup_int)

    # the frequent patterns formatted as a dictionary and the occurrences of each item
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