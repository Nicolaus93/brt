from collections import Counter
from tqdm import tqdm
import pickle

if __name__ == '__main__':

    entities = Counter()
    with open('data-concept-instance-relations.txt') as f:
        for line in tqdm(f):
            words = line.split()
            if len(words) == 3:
                entities[words[1]] += 1

    print(len(entities))
    most_common = sorted(entities.items(), key=lambda kv: kv[1], reverse=True)
    pickle.dump(most_common, open("most_common.p", "wb"))
    print(most_common[:10])
