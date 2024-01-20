features = [
    [['cls', 1, 12], ['eige', 0, 10], ['eige', 6, 7], ['eige', 9, 14], ['eige', 10, 6]]
]

for feature_list in features:
    print('[', end='')
    for feature in feature_list:
        print('(', end='')
        team, role = feature[1]%2, feature[1]//2
        if role == 5:
            print(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
        else:
            print(f"'{feature[0]}', 'T{team+1}-R{role+1}', {feature[2]}", end='')
        if feature != feature_list[-1]:
            print('), ', end='')
        else:
            print(')', end='')
    print('],')