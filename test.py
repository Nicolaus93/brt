from collections import defaultdict


def prior(vocab):
    """
    Calculating the prior probability for entity/concepts
    as defined in eq. 4 of the paper.
    """
    d = dict()
    total = 0
    for concept in vocab:
        d[concept] = 0
        for entity in vocab[concept]:
            current = vocab[concept][entity]
            d[concept] += current
            total += current
    for concept in d:
        d[concept] /= total
    return d


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


def tipicality(vocab, conditioned):
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
    d = dict()
    total = 0
    for value in vocab[conditioned]:
        temp = vocab[conditioned][value]
        total += temp
        d[value] = temp

    for value in d:
        d[value] /= total
    return d


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
