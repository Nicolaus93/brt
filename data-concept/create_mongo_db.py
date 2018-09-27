import pymongo as pm
import pprint


if __name__ == '__main__':

    client = pm.MongoClient()
    mydb = client['concept_graph']
    try:
        mydb.drop_collection('concept_graph')
    except Exception:
        pass
    graph = mydb['concept_graph']
    graph.create_index([("concept", pm.ASCENDING), ("entity", pm.ASCENDING)],
                       unique=True)
    docs = []

    with open('data-concept/data-concept-instance-relations.txt') as f:
        for line in f:
            words = line.split()
            if len(words) == 3:
                concept = words[0]
                entity = words[1]
                frequency = int(words[2])
                record = {'concept': concept,
                          'entity': entity,
                          'frequency': frequency}
                docs.append(record)

    result = graph.insert_many(docs)
    for pos, doc in enumerate(graph.find({})):
        pprint.pprint(doc)
        if pos > 10:
            break
