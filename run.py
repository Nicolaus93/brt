from conc_labels import bayes_rose_tree
import pickle

if __name__ == '__main__':
    """
    To use this script, first run data-concept/select_top_k.py
    Load the most common concepts and run the algorithm.
    """
    concepts = pickle.load(open(
        "data-concept/most_common_100_concepts.p", "rb"))
    entities = pickle.load(open(
        "data-concept/most_common_100_entities.p", "rb"))

    print("How many concepts? {}".format(len(concepts)))
    print("How many entities? {}".format(len(entities)))
    print("Running algo..")
    brt = bayes_rose_tree(entities, concepts)
    brt.algo(k=80)
    brt.adjust()
    print(brt)
