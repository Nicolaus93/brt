from conc_labels import bayes_rose_tree
import pickle

if __name__ == '__main__':
    concepts = pickle.load(open(
        "data-concept/most_common_100_concepts.p", "rb"))
    entities = pickle.load(open(
        "data-concept/most_common_100_entities.p", "rb"))

    print("How many concepts? {}".format(len(concepts)))
    print("How many entities? {}".format(len(entities)))
    print("Running algo..")
    brt = bayes_rose_tree(entities, concepts)
    brt.algo(k=80)
    print(brt)
    print(len(brt.nodes))
    brt.adjust()
    print(brt)
