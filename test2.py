from utilities import load_file, preprocess_transactions
from main import count_transaction_occurrences, sort_transaction_by_occurrences, filter_transactions_by_occurrences

if (__name__ == "__main__"):

    transactions = preprocess_transactions(load_file("test_data/ibm-2023-released.txt"))

    occurrences = count_transaction_occurrences(transactions)

    sort_transaction_by_occurrences(transactions, occurrences)

    filter_transactions_by_occurrences(transactions, occurrences, 2993 * 0.05)

    num_transactions = len(transactions)

    union_set = { "18", "14" }

    union_ant = { "14" }

    sup_union = 0

    for transaction in transactions:

        sup_union += (union_set.issubset(transaction))

    sup_ant = 0

    for transaction in transactions:

        sup_ant += (union_ant.issubset(transaction))

    union = sup_union / num_transactions

    antec = sup_ant / num_transactions

    confi = union / antec

    print(sup_union, sup_ant, confi)