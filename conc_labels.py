from test import prior, tipicality
from collections import defaultdict
from itertools import combinations
from birdseye import eye


def ps(ci, Cm, prior):
    """
    Eq. 9 in the paper
    """
    tot = 0
    for concept in Cm:
        tot += prior[concept]
    return prior[ci] / tot

# @eye
def tot_ps(Cm, prior):
    """
    Eq. 9 in the paper
    Input:
        - Cm, set - common concepts set
        - concepts prior, dict
    """
    d = dict()
    tot = 0
    for concept in Cm:
        p = prior[concept]
        d[concept] = p
        tot += p

    for key in d:
        d[key] /= tot

    return d

# @eye
def marginal(Dm, Cm, ps, e_tipicality):
    """
    Eq. 10 in the paper
    Input:
        - e_tipicality, dict of dicts
        - ps, dict of priors (from tot_ps?)
        - Cm, dict
    """
    f = 0
    for concept in Cm:
        tip = e_tipicality[concept]
        m = conditional(Dm, tip)
        f += ps[concept] * m
    return f

# @eye
def conditional(Dm, e_tipicality):
    """
    Eq. 11 in the paper
    Parameters:
        - Dm, entities set
        - e_tipicality, (dict)
    """
    p = 1.
    for entity in Dm:
        p *= e_tipicality[entity]
    return p


class Node(object):
    """
    Parameters:
        - Ti, the label of the cluster?
        - pi, is the prior prob that all the data
            in the node is kept in one cluster
            instead of being partitioned into sub-trees
    """

    def __init__(self, data, common_concepts, label=None, likelihood=1):
        assert type(common_concepts) == set

        self.Dm = data
        self.Cm = common_concepts
        self.children = []
        self.likelihood = likelihood
        self.label = label

    def __repr__(self):
        return "{}: {}".format(self.Cm, self.Dm)

    # def add_child(self, child):
    #     """
    #     Add a children node.
    #     """
    #     self.Dm += child.Dm
    #     self.children.append(child)


class bayes_rose_tree(object):
    """
    Bayesian Rose Tree.
    Input:
        - entities, dict
        - concepts, dict
        - gamma_0, float - hyperparameter
        - pi, float - hyperparameter between 0 and 1
    """

    def __init__(self, entities, concepts, gamma_0=0.2, pi=0.5):
        self.concepts = concepts
        self.entities = entities
        self.c_prior = prior(concepts)
        self.e_prior = prior(entities)
        self.n_clusters = len(entities)
        self.pi = pi

        self.e_tipicality = defaultdict(dict)
        for concept in concepts:
            # p(e|c)
            self.e_tipicality[concept] = tipicality(concepts, concept)

        self.c_tipicality = defaultdict(dict)
        for entity in entities:
            # p(c|e)
            self.c_tipicality[entity] = tipicality(entities, entity)

        # self.nodes = defaultdict(list)
        self.nodes = set()
        self.search = dict()
        for entity in entities:
            common_concepts = set(entities[entity].keys())
            new_node = Node([entity], common_concepts, label=entity)
            # self.nodes[new_node] = []
            self.nodes.add(new_node)
            self.search[entity] = new_node

    def __repr__(self):
        return 'Nodes: {}'.format(self.nodes)

    def node_likelihood(self, node):
        """
        Returns p(Dm|Tm).
        Input:
            - node, Node object
        """
        if len(node.children) == 0:
            return 1

        prior = tot_ps(node.Cm, self.c_prior)
        first_term = self.pi * marginal(
            node.Dm, node.Cm, prior, self.e_tipicality)

        second_term = (1 - self.pi)
        for child in node.children:
            second_term *= child.likelihood
        return first_term + second_term

    def join(self, Ti, Tj):
        """
        Join 2 nodes Ti and Tj.
        Input:
            - Ti, Tj, Node objects
        Returns:
            - Tm likelihood, float
            - Tm, new Node object
        """
        common_concepts = Ti.Cm & Tj.Cm
        if len(common_concepts) == 0:
            # there is no common concept for Dm,
            # the words in Dm cannot be generated by
            # a single model
            return Node([], set()), 0

        data = Ti.Dm + Tj.Dm
        Tm = Node(data, common_concepts)
        Tm.children.extend([Ti, Tj])
        return Tm, self.node_likelihood(Tm)

    def absorb(self, Ti, Tj):
        """
        Absorb 1 node.
        Input:
            - Ti (Node), absorbing node
            - Tj (Node), absorbed node
        """
        if len(Ti.children) == 0:
            # print("The node selected should have at least 1 child")
            return Node([], set()), 0

        data = Ti.Dm + Tj.Dm
        common_concepts = Ti.Cm & Tj.Cm
        if len(common_concepts) == 0:
            return Node([], set()), 0

        Tm = Node(data, common_concepts)
        Tm.children.append(Tj)
        return Tm, self.node_likelihood(Tm)

    def collapse(self, Ti, Tj):
        """
        TODO
        """
        T_m = Node()
        return brt.node_likelihood(T_m)

    def which_operation(self, Ti, Tj):
        """
        Select the operation which maximizes the
        following likelihood ratio:
            L(Tm) = p(Dm|Tm) / p(Di|Ti)p(Dj|Tj)
        """
        operations = [0] * 3
        nodes = [0] * 3
        # den = Ti.likelihood * Tj.likelihood

        # join
        join_score, join_node = self.join(Ti, Tj)
        operations[0] = join_score
        nodes[0] = join_node

        # absorb
        absorb_score = 0
        absorb_node = None
        if len(Ti.children) > 0:
            absorb_score, absorb_node = self.absorb(self.nodes[Ti], Tj)
        operations[1] = absorb_score
        nodes[1] = absorb_node

        # collapse
        collapse_score = 0
        collapse_node = None
        if len(Ti.children) > 0 and len(Tj.children) > 0:
            collapse_score, collapse_node = self.collapse(
                self.nodes[Ti], self.nodes[Tj])
        operations[2] = collapse_score
        nodes[2] = collapse_node

        index_max = max(range(len(operations)), key=operations.__getitem__)
        return nodes[index_max], max(operations)

    def select_pair(self):
        """
        Iterate over the tree dict (self.nodes) and select the
        best pair. Once we do that, add Tm to the tree and remove
        Ti, Tj from the tree dict.
        """
        best_score = 0
        for concept in self.concepts:
            for pair in combinations(self.concepts[concept].keys(), 2):
                entity1, entity2 = pair[0], pair[1]
                Ti = self.search[entity1]  # returns a node
                Tj = self.search[entity2]
                new_node, score = self.join(Ti, Tj)
                if score > best_score:
                    best_score = score
                    best_node = new_node
                    best_pair = (Ti, Tj)
        if best_score == 0:
            return None, None
        return best_node, best_pair

    def select_label(self, node):
        """
        Select the label of a new node from its set of
        common concepts.
        """
        best_score = 0
        for concept in node.Cm:
            # now look at eq. 12 in the paper
            concept_score = conditional(
                node.Dm, self.e_tipicality[concept]) * self.c_prior[concept]
            if concept_score > best_score:
                best_score = concept_score
                best_concept = concept
        node.label = best_concept

    def update(self, node):
        """
        Update all dictionaries once the best pair is found.
        """
        self.nodes.remove(node)
        entity = node.Dm[0]
        # concepts = self.entities[entity]
        concepts = self.entities.pop(entity)
        for concept in concepts:
            self.concepts[concept].pop(entity)

    def algo(self, verbose=False):
        """
        Algorithm 1 in the paper
        """
        while self.entities:

            node, pair = self.select_pair()
            if node is None:
                print(self.nodes)
                return

            self.select_label(node)
            self.nodes.add(node)
            if verbose:
                print(node, node.label)

            Ti, Tj = pair[0], pair[1]
            # maybe add Ti and Tj in node.children?
            self.update(Ti)
            self.update(Tj)


if __name__ == '__main__':
    brt = bayes_rose_tree()
