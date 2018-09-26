import pymongo as pm
import pprint
import random
import argparse
from conc_labels import bayes_rose_tree
from collections import defaultdict
from tqdm import tqdm


def random_sampling(db, tot, m=5, n=5):
    records_id = set([int(random.uniform(0, tot)) for i in range(m)])
    # pairs = []
    count = 0
    for i, row in enumerate(db.find({})):
        if i in records_id:
            concept = row['concept']
            all_entities = [i for i in db.find({'concept': concept})]
            # select n entities randomly
            for i in random.choices(all_entities, k=n):
                yield i
            count += 1
            if count > m:
                break
            # new = [i for i in random.choices(all_entities, k=n)]
            # pairs += new
    # return pairs


def random_sampling_entities(db, tot, m=5, n=5, seed=None):
    random.seed(seed)
    records_id = set([int(random.uniform(0, tot)) for i in range(m)])
    pairs = []
    count = 0
    for i, row in tqdm(enumerate(db.find({}))):
        if i in records_id:
            concept = row['concept']
            print("\n sampled: {}".format(concept))
            all_entities = [i for i in db.find({'concept': concept})]
            new = [i for i in random.choices(all_entities, k=n)]
            all_entities = []
            for record in new:
                all_entities += [i for i in db.find({'entity': record['entity']})]
            pairs += all_entities
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
    parser.add_argument('-k', dest='k', type=int,
                        help='number of passes of the algorithm',
                        default=50)
    parser.add_argument('-seed', dest='s', type=int,
                        help='seed using for sampling from db (Default None)',
                        default=None)
    parser.add_argument('-verbose', dest='verbose', action='store_true',
                        default=False,
                        help='print stuff uh?')

    args = parser.parse_args()
    # loading results
    m = args.m
    n = args.n
    k = args.k
    seed = args.s
    verbose = args.verbose

    client = pm.MongoClient()
    mydb = client['concept_graph']
    graph = mydb['concept_graph']
    tot = graph.count()
    print("{} entries in the db".format(tot))

    concepts = defaultdict(dict)
    entities = defaultdict(dict)

    print("Now sampling concepts from the DB..")
    records = random_sampling_entities(graph, tot, m=m, n=n, seed=seed)
    print("{} records sampled".format(len(records)))
    for record in records:
        if verbose:
            pprint.pprint(record)
        concept = record['concept']
        entity = record['entity']
        frequency = record['frequency']
        concepts[concept][entity] = frequency
        entities[entity][concept] = frequency

    print("Running Bayes Rose Tree Algo")
    brt = bayes_rose_tree(entities, concepts)
    brt.algo(k=k, verbose=verbose)
    brt.adjust()
    print(brt)
