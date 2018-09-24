import pymongo as pm
import pprint
import random
import argparse
from conc_labels import bayes_rose_tree
from collections import defaultdict


def random_sampling(db, tot, m=5, n=5):
    records_id = set([int(random.uniform(0, tot)) for i in range(m)])
    pairs = []
    count = 0
    for i, row in enumerate(graph.find({})):
        if i in records_id:
            concept = row['concept']
            all_entities = [i for i in graph.find({'concept': concept})]
            new = [i for i in random.choices(all_entities, k=n)]
            pairs += new
            count += 1
            if count > m:
                break
    return pairs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Hierarchical Conceptual Labeling.')
    parser.add_argument("-m", dest='m', type=int,
                        help='number of concepts to use',
                        default=5)
    parser.add_argument('-n', dest='n', type=int,
                        help='number of entities to use',
                        default=5)
    parser.add_argument('-verbose', dest='verbose', action='store_true',
                        default=False,
                        help='print stuff uh?')

    args = parser.parse_args()
    # loading results
    m = args.m
    n = args.n
    verbose = args.verbose

    client = pm.MongoClient()
    mydb = client['concept_graph']
    graph = mydb['concept_graph']
    tot = graph.count()
    print("{} entries in the db".format(tot))
    print("\n")

    concepts = defaultdict(dict)
    entities = defaultdict(dict)
    for record in random_sampling(graph, tot, m=m, n=n):
        if verbose:
            pprint.pprint(record)
        concept = record['concept']
        entity = record['entity']
        frequency = record['frequency']
        concepts[concept][entity] = frequency
        entities[entity][concept] = frequency

    print("Running Bayes Rose Tree Algo")
    brt = bayes_rose_tree(entities, concepts)
    brt.algo()
    print(brt)
