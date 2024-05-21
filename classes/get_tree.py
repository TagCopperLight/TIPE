import json

from classes.c45 import C45

VOID_METRICS = {
    'indeg': {'T1-R1': 0, 'T1-R2': 0, 'T1-R3': 0, 'T1-R4': 0, 'T1-R5': 0, 'T2-R1': 0, 'T2-R2': 0, 'T2-R3': 0, 'T2-R4': 0, 'T2-R5': 0, 'DEATH': 0},
    'outdeg': {'T1-R1': 0, 'T1-R2': 0, 'T1-R3': 0, 'T1-R4': 0, 'T1-R5': 0, 'T2-R1': 0, 'T2-R2': 0, 'T2-R3': 0, 'T2-R4': 0, 'T2-R5': 0, 'DEATH': 0},
    'cls': {'T1-R1': 0.0, 'T1-R2': 0.0, 'T1-R3': 0.0, 'T1-R4': 0.0, 'T1-R5': 0.0, 'T2-R1': 0.0, 'T2-R2': 0.0, 'T2-R3': 0.0, 'T2-R4': 0.0, 'T2-R5': 0.0, 'DEATH': 0.0},
    'btw': {'T1-R1': 0.0, 'T1-R2': 0.0, 'T1-R3': 0.0, 'T1-R4': 0.0, 'T1-R5': 0.0, 'T2-R1': 0.0, 'T2-R2': 0.0, 'T2-R3': 0.0, 'T2-R4': 0.0, 'T2-R5': 0.0, 'DEATH': 0.0},
    'eige': {'T1-R1': 0.30151134457776363, 'T1-R2': 0.30151134457776363, 'T1-R3': 0.30151134457776363, 'T1-R4': 0.30151134457776363, 'T1-R5': 0.30151134457776363, 'T2-R1': 0.30151134457776363, 'T2-R2': 0.30151134457776363, 'T2-R3': 0.30151134457776363, 'T2-R4': 0.30151134457776363, 'T2-R5': 0.30151134457776363, 'DEATH': 0.30151134457776363}
}


def create_decision_tree_files(games, features, create_files=True):
    features_names = {}
    for feature in features:
        features_names[feature] = f'{feature[0]} of {feature[1]} in time frame {feature[2]}'

    names = {"classes": ["T1", "T2"], "features": list(features_names.values())}
    if create_files:
        with open("graph_data/names.json", "w") as file:
            json.dump(names, file, indent=4)

    with open('graph_data/graphs.json', 'r') as file:
        graphs = json.load(file)

    data = []
    for game in games:
        data_to_tree = {"class": "T1"} if game.winner == 'blue' else {"class": "T2"}
        for feature in features:
            game_metrics = [graph for graph in graphs if graph["game_id"] == game.game_id][0]

            if feature[2] < len(game_metrics["time_frames"]):
                metrics = game_metrics["time_frames"][feature[2]]["metrics"]
            else:
                metrics = VOID_METRICS

            if feature[0] == 'indeg':
                data_to_tree[features_names[feature]] = metrics['indeg'][feature[1]]
            elif feature[0] == 'outdeg':
                data_to_tree[features_names[feature]] = metrics['outdeg'][feature[1]]
            elif feature[0] == 'cls':
                data_to_tree[features_names[feature]] = metrics['cls'][feature[1]]
            elif feature[0] == 'btw':
                data_to_tree[features_names[feature]] = metrics['btw'][feature[1]]
            elif feature[0] == 'eige':
                data_to_tree[features_names[feature]] = metrics['eige'][feature[1]]
        
        data.append(data_to_tree)

    if create_files:
        with open("graph_data/data.json", "w") as file:
            json.dump(data, file, indent=4)

    return names, data
        
def create_decision_tree():
    with open("graph_data/names.json", "r") as file:
        names = json.load(file)

    with open("graph_data/data.json", "r") as file:
        data = json.load(file)

    c45 = C45(data, names["classes"], names["features"])
    c45.generate_tree()

    return c45

def create_decision_tree_from_dict(names, data):
    c45 = C45(data, names["classes"], names["features"])
    c45.generate_tree()

    return c45