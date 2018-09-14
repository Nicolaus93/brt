from test import prior, tipicality
from collections import defaultdict


def ps(ci, Cm, prior):
    """
    Eq. 9 in the paper
    """
    tot = 0
    for concept in Cm:
        tot += prior[concept]
    return prior[ci] / tot


def tot_ps(Cm, prior):
    """
    Eq. 9 in the paper
    Input:
        - Cm, common concepts set (dict?)
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


def conditional(Dm, e_tipicality):
    """
    Eq. 11 in the paper
    Parameters:
        - Dm, entities set
        - e_tipicality, (dict)
    """
    p = 1
    for entity in Dm:
        p *= e_tipicality[entity]
    return p


def label_selection(Dm, Cm, c_prior):
    best_score = 0
    for concept in Cm:
        concept_score = conditional(Dm, concept) * c_prior[concept]
        if concept_score > best_score:
            best_score = concept_score
            best_concept = concept
    return best_concept


class Node(object):
    """
    Parameters:
        - Ti, the label of the cluster?
        - pi, is the prior prob that all the data
            in the node is kept in one cluster
            instead of being partitioned into sub-trees
    """

    # def _get_Dm(self):
    #     if len(self.children) == 0:
    #         return [self.entity]

    #     Dm = []
    #     for child in self.children:
    #         Dm += child.get_Dm()
    #     return Dm

    # def _get_Cm(self):
    #     if len(self.children) == 0:
    #         return set(self.common_concepts)

    #     Cm = set()
    #     for child in self.children:
    #         Cm &= child._get_Cm()
    #     return Cm

    def _get_likelihood(self, entities):
        if len(self.children) == 0:
            # Dm = [self.entity]
            Dm = self.Dm
            print(Dm)
            # Cm = entities[self.entity]
            Cm = self.Cm
            print(Cm)
            return self.pi * marginal(Dm, Cm, )

        children_lik = (1 - self.pi)
        for child in self.children:
            children_lik *= child._get_likelihood(entities)

        p_m = self.pi * marginal() + children_lik
        return p_m

    def __init__(self, data, common_concepts, likelihood=1):
        assert type(common_concepts) == set

        self.Dm = data
        self.Cm = common_concepts
        self.children = []
        self.likelihood = likelihood

    def __repr__(self):
        return "{}".format(self.Dm)


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
        self.entities = entities
        self.concepts = concepts
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

        self.nodes = defaultdict(list)
        for entity in entities:
            common_concepts = set(entities[entity].keys())
            new_node = Node([entity], common_concepts)
            self.nodes[new_node] = []

    def node_likelihood(self, node):
        """
        Returns p(Dm|Tm).
        Input:
            - node, Node object
        """
        if len(self.nodes[node]) == 0:
            # Dm = [node.entity]
            # Cm = self.entities[node.entity]
            # Dm = node.Dm
            # Cm = node.Cm
            # prior = tot_ps(Cm, self.c_prior)
            # return node.pi * marginal(Dm, Cm, prior, self.e_tipicality)
            return 1

        prior = tot_ps(node.Cm, self.c_prior)
        first_term = self.pi * marginal(
            node.Dm, node.Cm, prior, self.e_tipicality)
        second_term = (1 - self.pi)
        # for child in node.children:
        for child in self.nodes[node]:
            second_term *= child.likelihood
        return first_term + second_term

    def __repr__(self):
        return 'Nodes: {}'.format(self.nodes)

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
        data = Ti.Dm + Tj.Dm
        Tm = Node(data, common_concepts)
        return brt.node_likelihood(Tm), Tm

    def absorb(self, children_of_Ti, T_j):
        T_m = Node()
        return brt.node_likelihood(T_m)

    def collapse(self, children_Ti, children_Tj):
        T_m = Node()
        return brt.node_likelihood(T_m)

    def which_operation(self, Ti, Tj):
        join_score, new_node1 = self.join(Ti, Tj)
        absorb_score, new_node2 = self.absorb(self.nodes[Ti], Tj)
        collapse_score, new_node3 = self.collapse(
            self.nodes[Ti], self.nodes[Tj])
        return


if __name__ == '__main__':
    brt = bayes_rose_tree()
