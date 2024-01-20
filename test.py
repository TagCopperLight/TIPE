features = [
    [['outdeg', 0, 12], ['outdeg', 4, 11], ['cls', 8, 2], ['btw', 9, 8], ['eige', 10, 9]]
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