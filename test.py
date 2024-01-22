features = [
    [['outdeg', 0, 12], ['btw', 4, 7], ['btw', 8, 5], ['eige', 3, 9], ['eige', 4, 8], ['eige', 9, 1]],
    [['outdeg', 1, 5], ['btw', 1, 11], ['eige', 0, 0], ['eige', 1, 11], ['eige', 3, 7], ['eige', 5, 12]],
    [['outdeg', 4, 11], ['outdeg', 4, 14], ['btw', 4, 14], ['btw', 5, 8], ['eige', 0, 11]],
    [['indeg', 10, 10], ['cls', 3, 8], ['btw', 4, 7], ['eige', 4, 0], ['eige', 4, 5]]
]

for feature_list in features:
    print('[', end='')
    for feature in feature_list:
        print('(', end='')
        team, role = feature[1]%2, feature[1]//2
        if feature[1] == 10:
            print(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
        else:
            print(f"'{feature[0]}', '{['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]}', {feature[2]}", end='')
        if feature != feature_list[-1]:
            print('), ', end='')
        else:
            print(')', end='')
    print('],')