from typing import *
import itertools

def powerset(iterable : Iterable[ Any ]) -> itertools.chain:

    iterable = list(iterable)

    return itertools.chain.from_iterable(
        itertools.combinations(iterable, choice) 
            for choice in range(len(iterable) + 1)
    )

class TreeNode(object):

    NULL_LABEL = None

    def __init__(self, item_label  : Optional[ Union[ int, str ] ], 
                       item_value  : Optional[ int               ] = 0,
                       parent_node : Optional[ "TreeNode"        ] = None

                       ) -> None:

        # item label, either integer or string
        self.item_label = item_label

        # item value, number of occurrences of current path from root
        self.item_value = item_value

        # dictionary of children nodes
        self.children_nodes = dict()

        # reference to parent node
        self.parent_node = parent_node

        # reference to friend node (header link)
        self.friend_node = None

    def __iadd__(self, value : Union[ int, "TreeNode" ]) -> "TreeNode":

        if (isinstance(value, int)):

            # increment by value
            self.item_value += value

        elif (isinstance(value, TreeNode)):

            # add children node
            self.children_nodes[value.as_key] = value

        # return object itself
        return self
    
    @property
    def as_key(self) -> Union[ str, int ]:

        # return item label
        return self.item_label
    
    def __repr__(self) -> str:

        # return string representation of tree
        return f"({self.item_label}:{self.item_value}){self.children_nodes}"
    
    def __contains__(self, value : Union[ str, int, "TreeNode" ]) -> bool:

        # replace value with item label if is node
        if (isinstance(value, TreeNode)):
            value = value.as_key
        
        # check whether node is child and return boolean
        return self.children_nodes.__contains__(value)
    
    def __getitem__(self, item_label : Union[ str, int ]) -> "TreeNode":

        # fetch child node with item label
        return self.children_nodes[item_label]
    

def count_transaction_occurrences(transactions : List[ List[ Any ] ]) -> Dict[ Any, int ]:

    # initialize empty dictionary
    occurrences = dict()

    # iterate through each transaction
    for transaction in transactions:

        # iterate through each item
        for item in transaction:

            # increment item occurrence
            occurrences[item] = occurrences.get(item, 0) + 1

    # return occurrences dictionary
    return occurrences


def sort_transaction_by_occurrences(transactions : List[ List[ Any ] ], occurrences  : Dict[ Any, int ]) -> None:
    
    # iterate through each transaction
    for transaction in transactions:

        # sort items in transaction by occurrences in non-increasing order
        transaction.sort(key = occurrences.__getitem__, reverse = True)


def filter_transactions_by_occurrences(transactions : List[ List[ Any ] ], 
                                       occurrences  : Dict[ Any, int ],
                                       min_sup_int  : int) -> None:

    # iterate through each transaction
    for transaction in transactions:

        # filter items below support threshold
        transaction[:] = list(filter(lambda x : occurrences[x] >= min_sup_int, transaction))


def prepend_transaction_occurrences(transactions : List[ List[ Any ] ]) -> None:

    # iterate through each transaction
    for transaction in transactions:

        # prepend one to transaction
        transaction[:] = [ 1 ] + transaction


HEADER_HEAD = 0

HEADER_TAIL = 1


def _append_to_headers(headers : Dict[ Any, List[ TreeNode ] ], node : TreeNode, value : Any) -> None:
    
    # if `headers` does not already track value
    if (value not in headers):

        # initialize friend link with references to head and tail node
        headers[value] = [  node, node  ]

        # stop function
        return 

    # obtain reference to tail node of friend link
    tail_node = headers[value][HEADER_TAIL]

    # add newest node to friend link
    tail_node.friend_node = node

    # replace tail node with current node
    headers[value][HEADER_TAIL] = node


def _construct_fp_tree(headers     : Dict[ Any, List[ TreeNode ] ], 
                       cur_node    : TreeNode, 
                       transaction : List[ Any ],
                       occurrences : Optional[ int ] = 1
                       ) -> None:

    # stop recursion on empty transaction
    if (transaction.__len__() == 0):
        return
    
    # retrieve first item
    item_label = transaction[0]

    # if current node contains such a labeled child
    if (item_label in cur_node):

        # fetch child node with item label
        child_node = cur_node[item_label]

        # increment child node occurrences (value)
        child_node += occurrences

        # construct FP tree with remaining transaction items
        return _construct_fp_tree(headers, child_node, transaction[1:], occurrences)

    # construct new child node since it does not exist yet
    new_node = TreeNode(item_label, item_value = occurrences, parent_node = cur_node)

    # add new node to children list of current node
    cur_node += new_node

    # update headers (friend link)
    _append_to_headers(headers, new_node, item_label)

    # construct FP tree with remaining transaction items
    _construct_fp_tree(headers, new_node, transaction[1:], occurrences)
    

def count_transaction_occurrences_2(transactions : List[ List[ Any ] ]):

    occurrences = dict()

    for transaction in transactions:

        occ = transaction[0]

        for item in transaction[1:]:

            occurrences[item] = occurrences.get(item, 0) + occ

    return occurrences


def construct_fp_tree(transactions : List[ List[ Any ] ], min_sup_int : int) -> Tuple[ TreeNode, Dict[ Any, List[ TreeNode ] ] ]:

    _occurrences = count_transaction_occurrences_2(transactions)

    #print(_occurrences)

    #print(transactions)

    indiv_count = [  x[0] for x in transactions  ]

    transactions = [  x[1:] for x in transactions  ]

    filter_transactions_by_occurrences(transactions, _occurrences, min_sup_int)

    #sort_transaction_by_occurrences(transactions, _occurrences)

    #print(transactions)

    transactions = [  
        [ indiv_count[x], *transaction ] 
            for x, transaction in enumerate(transactions)  
    ]

    # root node of FP tree
    root_node = TreeNode(TreeNode.NULL_LABEL, None)

    # headers to link nodes sharing item label (friend link)
    headers = dict()

    # iterate through each transaction
    for transaction in transactions:

        occurrences : int = transaction[0]

        # update the FP tree with current transaction
        _construct_fp_tree(headers, root_node, transaction[1:], occurrences)

    # return `root node` and `headers`
    return (root_node, headers)


def __mine_frequent_patterns(item_node : TreeNode, min_sup_int : int):

    #print(item_node.item_label)

    conditional_pattern_base = []

    friend_node = item_node 

    while (friend_node is not None):

        ascend_node = friend_node

        prefix_path = [  ascend_node.item_value  ]

        while (ascend_node.item_label != TreeNode.NULL_LABEL):

            #print("f", (ascend_node.item_label, ascend_node.item_value))
            
            prefix_path.insert(1, ascend_node.item_label)

            ascend_node = ascend_node.parent_node

        if (len(prefix_path)):
            conditional_pattern_base.append(prefix_path)

        friend_node = friend_node.friend_node

    #print(conditional_pattern_base)

    #print(item_node.item_label)

    #print("CPB:", conditional_pattern_base)

    (cond_fp_tree, cond_fp_headers) = construct_fp_tree(conditional_pattern_base, min_sup_int)

    #print("CT:", cond_fp_tree)

    friend_node = cond_fp_headers[item_node.item_label][HEADER_HEAD]

    frequent_pattern_list = dict()

    while (friend_node is not None):

        ascend_node = friend_node

        value_pair = []

        if (ascend_node.item_label != TreeNode.NULL_LABEL):

            #print((ascend_node.item_label, ascend_node.item_value))

            #value_pair.insert(0, (ascend_node.item_label, ascend_node.item_value))

            ascend_node = ascend_node.parent_node

        while (ascend_node.item_label != TreeNode.NULL_LABEL):

            #if (ascend_node.item_value >= min_sup_int):
            value_pair.insert(0, (ascend_node.item_label, ascend_node.item_value))

            ascend_node = ascend_node.parent_node

        #print("VP:", value_pair)

        for pattern in powerset(value_pair):

            if (len(pattern) == 0):
                continue

            path_width = min(pat[1] for pat in pattern)

            pattern = tuple(pat[0] for pat in pattern)

            #print(pattern, path_width)

            frequent_pattern_list[pattern] = path_width

        friend_node = friend_node.friend_node

    return frequent_pattern_list


def mine_patterns(headers : Dict[ Any, List[ TreeNode ] ], min_sup_int : int, occurrences) -> Dict[ Any, Dict[ Tuple[ Any ], int ] ]:

    frequent_patterns = dict()

    for item_label, (item_head, _) in sorted(headers.items(), key = lambda x : occurrences[x[0]]):

        frequent_patterns[item_label] = __mine_frequent_patterns(item_head, min_sup_int)

        frequent_patterns[item_label][()] = occurrences[item_label]

    return frequent_patterns


def count_fp_tree_item_occurrence(occurrence : list, fp_node : TreeNode, item : Any) -> None:

    #print(type(fp_node))

    if (fp_node is None):
        return
    
    if (fp_node.item_label == item):
        occurrence[0] += 1

    for child_node in fp_node.children_nodes.values():

        #print(type(child_node))

        count_fp_tree_item_occurrence(occurrence, child_node, item)

def mine_frequent_patterns(transactions : List[ List[ int ] ], min_sup_int : int):

    occurrences = count_transaction_occurrences(transactions = transactions)

    sort_transaction_by_occurrences(transactions = transactions, occurrences = occurrences)

    filter_transactions_by_occurrences(transactions = transactions, occurrences = occurrences, min_sup_int = min_sup_int)

    prepend_transaction_occurrences(transactions = transactions)

    fp_tree, fp_headers = construct_fp_tree(transactions = transactions, min_sup_int = min_sup_int)

    #occurrence = [ 0 ]

    #count_fp_tree_item_occurrence(occurrence, fp_tree, "18")

    #print("OCC:", occurrence[0])

    frequent_items = mine_patterns(headers = fp_headers, min_sup_int = min_sup_int, occurrences = occurrences)

    return frequent_items, occurrences

if (__name__ == "__main__"):

    min_sup_int = 1

    transactions = [
        [ '9192', '31651', '45874' ],
        #[ '9192', '31651' ],
        [ '57515', '45874' ],
        [ '45874', '9192' ],
        [ '31651' ]
    ]

    # print(f"Source Transactions: {transactions}\n")


    # occurrences = count_transaction_occurrences(transactions)

    # print(f"Occurrences: {occurrences}\n")


    # sort_transaction_by_occurrences(transactions, occurrences)

    # print(f"Sorted Transactions: {transactions}\n")


    # filter_transactions_by_occurrences(transactions, occurrences, min_sup_int = min_sup_int)

    # print(f"Filtered Transactions: {transactions}\n")


    # prepend_transaction_occurrences(transactions)

    # print(f"Prepended Transactions: {transactions}\n")


    # (fp_root, fp_headers) = construct_fp_tree(transactions)

    # print(f"FP Tree: {fp_root}\n")


    # frequent_patterns = mine_patterns(fp_headers, min_sup_int)

    # print(f"Frequent Itemsets: {frequent_patterns}")

    frequent_items, _ = mine_frequent_patterns(transactions, min_sup_int)

    print(frequent_items)
    