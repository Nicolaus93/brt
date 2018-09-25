
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
    p = 1.
    for entity in Dm:
        p *= e_tipicality[entity]
    return p


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
