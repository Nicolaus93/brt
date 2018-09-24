from collections import defaultdict
from itertools import combinations
from utils import *
from tqdm import tqdm


def print_tree(current_node, indent="", last='updown'):

    nb_children = lambda node: sum(
        nb_children(child) for child in node.children) + 1
    size_branch = {
        child: nb_children(child) for child in current_node.children}

    """ Creation of balanced lists for "up" branch and "down" branch. """
    up = sorted(current_node.children, key=lambda node: nb_children(node))
    down = []
    while up and sum(size_branch[node] for node in down) < sum(size_branch[node] for node in up):
        down.append(up.pop())

    """ Printing of "up" branch. """
    for child in up:
        next_last = 'up' if up.index(child) is 0 else ''
        next_indent = '{0}{1}{2}'.format(
            indent, ' ' if 'up' in last else '│', " " * len(current_node.name()))
        print_tree(child, indent=next_indent, last=next_last)

    """ Printing of current node. """
    if last == 'up':
        start_shape = '┌'
    elif last == 'down':
        start_shape = '└'
    elif last == 'updown':
        start_shape = ' '
    else:
        start_shape = '├'

    if up:
        end_shape = '┤'
    elif down:
        end_shape = '┐'
    else:
        end_shape = ''

    print('{0}{1}{2}{3}'.format(
        indent, start_shape, current_node.name(), end_shape))

    """ Printing of "down" branch. """
    for child in down:
        next_last = 'down' if down.index(child) is len(down) - 1 else ''
        next_indent = '{0}{1}{2}'.format(
            indent, ' ' if 'down' in last else '│', " " * len(current_node.name()))
        print_tree(child, indent=next_indent, last=next_last)


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

    def __repr__(self, level=0):
        if len(self.children) > 0:
            to_print = str(self.label) + ': ' + str(self.Dm)
        else:
            to_print = ''
            i = 0
            for concept in self.Cm:
                to_print += str(concept) + ', '
                i += 1
                if i > 3:
                    to_print += '...'
                    break
            to_print += str(self.Dm[0])
        ret = "\t" * level + to_print + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

    def name(self):
        if len(self.children) > 0:
            to_print = str(self.label) + ': ' + str(self.Dm[:3])
            # if len(self.Dm) > 3:
            #     to_print += ', ..'
        else:
            to_print = ''
            i = 0
            for concept in self.Cm:
                to_print += str(concept) + ', '
                i += 1
                if i > 3:
                    to_print += '..'
                    break
            to_print += ': ' + str(self.Dm[0])
        return to_print


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

        self.c_prior = prior(concepts)
        self.n_clusters = len(entities)
        self.pi = pi

        self.e_tipicality = defaultdict(dict)
        for concept in concepts:
            # p(e|c)
            self.e_tipicality[concept] = tipicality(concepts, concept)

        # self.e_prior = prior(entities)
        # self.c_tipicality = defaultdict(dict)
        # for entity in entities:
        #     # p(c|e)
        #     self.c_tipicality[entity] = tipicality(entities, entity)

        self.nodes = set()
        self.concepts = defaultdict(set)
        for entity in entities:
            common_concepts = set(entities[entity].keys())
            new_node = Node([entity], common_concepts, label=entity)
            for concept in common_concepts:
                self.concepts[concept].add(new_node)
            self.nodes.add(new_node)

    def __repr__(self):
        ret = ''
        for node in self.nodes:
            # ret += node.__repr__()
            print_tree(node)
        return ret

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
            return None, 0

        data = Ti.Dm + Tj.Dm
        Tm = Node(data, common_concepts)
        Tm.children.extend([Ti, Tj])
        Tm.likelihood = self.node_likelihood(Tm)
        return Tm, Tm.likelihood

    def absorb(self, Ti, Tj):
        """
        Absorb 1 node.
        Input:
            - Ti (Node), absorbing node
            - Tj (Node), absorbed node
        """
        if len(Ti.children) == 0:
            # The node selected should have at least 1 child
            return None, 0

        data = Ti.Dm + Tj.Dm
        common_concepts = Ti.Cm & Tj.Cm
        if len(common_concepts) == 0:
            return None, 0

        Tm = Node(data, common_concepts)
        Tm.children.append(Tj)
        Tm.likelihood = self.node_likelihood(Tm)
        return Tm, Tm.likelihood

    def collapse(self, Ti, Tj):
        """
        Collapse 2 nodes.
        """
        if len(Ti.children) or len(Tj.children) == 0:
            return None, 0

        data = Ti.Dm + Tj.Dm
        common_concepts = Ti.Cm & Tj.Cm
        if len(common_concepts) == 0:
            return None, 0

        Tm = Node(data, common_concepts)
        Tm.likelihood = self.node_likelihood(Tm)
        return Tm, Tm.likelihood

    def algo(self, k=1000, verbose=False):
        """
        Algorithm revised.
        """

        for i in tqdm(range(k)):

            if verbose:
                print("{} remaining nodes".format(len(self.nodes)))

            node, pair = self.select_pair()
            if node is None:
                print("Interrupted")
                break
            self.select_label(node)
            for concept in node.Cm:
                self.concepts[concept].add(node)
            self.nodes.add(node)

            Ti, Tj = pair[0], pair[1]
            self.remove(Ti)
            self.remove(Tj)

        return

    def select_pair(self):
        """
        Fine the pair of trees Ti and Tj and the merge operation
        that can maximize the likelihood ratio:

                            p(Dm | Tm)
                L(Tm) = _____________________
                        p(Di | Ti) p(Dj | Tj)
        """

        best_score = 0
        best_node = None
        best_pair = (None, None)
        # for concept in self.concepts:
        for pair in combinations(self.nodes, 2):
        # for pair in combinations(self.concepts[concept], 2):
            Ti, Tj = pair[0], pair[1]
            if len(Ti.Cm & Tj.Cm) == 0:
                continue
            den = Ti.likelihood * Tj.likelihood
            join_node, join_score = self.join(Ti, Tj)
            absorb_node, absorb_score = self.absorb(Ti, Tj)
            # absorb_node, absorb_score = None, 0
            collapse_node, collapse_score = self.collapse(Ti, Tj)
            # collapse_node, collapse_score = None, 0
            maxim = max(join_score, absorb_score, collapse_score)
            if maxim == join_score:
                new_node = join_node
            elif maxim == absorb_score:
                new_node = absorb_node
            else:
                new_node = collapse_node
            new_score = maxim / den
            if new_score > best_score:
                best_score = new_score
                best_node = new_node
                best_pair = (Ti, Tj)
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

    def remove(self, node):
        """
        Update all dictionaries once the best pair is found.
        """
        self.nodes.remove(node)
        for concept in node.Cm:
            self.concepts[concept].remove(node)


if __name__ == '__main__':
    brt = bayes_rose_tree()
