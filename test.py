from collections import defaultdict
from utils import prior, tipicality


def tipicality_single(vocab, conditioned, target):
    """
    Calculates p(e|c) or p(c|e)
    If p(e|c):
        - vocab = dict, concepts
        - conditioned = str, concept
        - target = str, entity
    If p(c|e):
        - vocab = dict, entities
        - conditioned = str, entity
        - target = str, concept
    """
    total = 0
    for value in vocab[conditioned]:
        total += vocab[conditioned][value]
    return vocab[conditioned][target] / total


if __name__ == '__main__':

    i = 0
    concepts = defaultdict(dict)
    entities = defaultdict(dict)

    with open('data-concept/data-concept-instance-relations.txt') as f:
        for line in f:
            words = line.split()
            if len(words) == 3:
                concepts[words[0]][words[1]] = int(words[2])
                entities[words[1]][words[0]] = int(words[2])

            if i > 10:
                break
            i += 1

    print(entities)
    print("\n")
    print(concepts)
    print(prior(concepts))
    print(tipicality_single(concepts, 'factor', 'age'))
    print(tipicality(concepts, 'factor'))

    print("\n")
    print(entities)
    print(tipicality_single(entities, 'age', 'factor'))
