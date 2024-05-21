import logging

import importer as importer


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def show_rules(rules):
    """
    Show the rules.
    """

    for rule in rules:
        log.info(f'IF ', end='')
        for node in rules[rule]["path"]:
            if node[1] == 'leaf':
                log.info(f'THEN {node[0].label} win', end='')
            else:
                log.info(f'{node[0].label} {node[1]} {node[0].threshold} & ', end='')
        log.info(f'\n{rule.label} (support: {rules[rule]["support"]}, confidence: {rules[rule]["confidence"]})')
        log.info(f'\n(support: {rules[rule]["support"]}, confidence: {rules[rule]["confidence"]})')
    log.info()

def get_rules(tree, confidence, support):
    """
    Get the rules from the decision tree, with a minimum confidence and support.
    """
    
    rules = {}

    data = importer.get_graphs_files()[1]

    def __get_path_rec(data, node, path):
        if node.is_leaf:
            path.append((node, 'leaf'))
            return path
        else:
            if data[node.label] <= node.threshold:
                path.append((node, '<='))
                return __get_path_rec(data, node.children[0], path)
            elif len(node.children) == 2:
                path.append((node, '>'))
                return __get_path_rec(data, node.children[1], path)

    for game in data:
        path = __get_path_rec(game, tree.tree, [])
        
        if path[-1][0] not in rules:
            rules[path[-1][0]] = {'support': 1, 'confidence': 0}
            rules[path[-1][0]]['path'] = path
        else:
            rules[path[-1][0]]["support"] += 1

        if path[-1][0].label == game["class"]:
            rules[path[-1][0]]["confidence"] += 1

    for rule in rules:
        rules[rule]["confidence"] /= rules[rule]["support"]

    rules = {rule: rules[rule] for rule in rules if rules[rule]["confidence"] >= confidence and rules[rule]["support"] >= support}

    return rules