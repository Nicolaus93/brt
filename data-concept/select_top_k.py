from collections import defaultdict
import pickle


if __name__ == '__main__':

    concepts = defaultdict(dict)
    entities = defaultdict(dict)

    most_common = pickle.load(open("most_common.p", "rb"))
    k = 100
    most_common = set([x[0] for x in most_common[:k]])

    with open('data-concept-instance-relations.txt') as f:
        for line in f:
            words = line.split()
            if len(words) == 3 and words[1] in most_common:
                concepts[words[0]][words[1]] = int(words[2])
                entities[words[1]][words[0]] = int(words[2])

    pickle.dump(entities, open("most_common_" + str(k) + "_entities.p", "wb"))
    pickle.dump(concepts, open("most_common_" + str(k) + "_concepts.p", "wb"))
