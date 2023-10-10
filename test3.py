import pickle 

if (__name__ == "__main__"):

    result = pickle.load(open("e.pickle", mode = "rb"))

    union_set = ("14", "18")

    union_ant = ("18", )

    sup_uni = result[union_set[-1]][union_set[:-1]]

    sup_ant = result[union_ant[-1]][union_ant[:-1]]

    print(sup_uni, sup_ant, sup_uni / sup_ant)