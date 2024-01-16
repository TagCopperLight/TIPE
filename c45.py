import math


class Node:
    def __init__(self, is_leaf, label, threshold):
        self.label = label
        self.threshold = threshold
        self.is_leaf = is_leaf
        self.children = []


class C45:
    def __init__(self, data, classes, features):
        self.data = data
        self.classes = classes
        self.features = features

        self.tree = None

    def get_majority_class(self, data):
        return max(set([e["class"] for e in data]), key=[e["class"] for e in data].count)
    
    def split_attribute(self, data, features):
        splitted_data = []
        best_feature = None
        best_threshold = None
        max_gain = -1

        for feature in features:
            sorted_data = sorted(data, key=lambda x: x[feature])
            for i in range(len(sorted_data) - 1):
                threshold = (sorted_data[i][feature] + sorted_data[i + 1][feature]) / 2
                left = [e for e in sorted_data if e[feature] <= threshold]
                right = [e for e in sorted_data if e[feature] > threshold]
                gain = self.gain(data, left, right)
                if gain > max_gain:
                    max_gain = gain
                    splitted_data = [left, right]
                    best_feature = feature
                    best_threshold = threshold
                    
        return best_feature, best_threshold, [subset for subset in splitted_data if subset]
    
    def gain(self, parent, left, right):
        return self.entropy(parent) - self.entropy(left) * len(left) / len(parent) - self.entropy(right) * len(right) / len(parent)
    
    def entropy(self, data):
        if len(data) == 0:
            return 0
        classes = [e["class"] for e in data]
        return -1 * sum([classes.count(c) / len(data) * math.log(classes.count(c) / len(data), 2) for c in set(classes)])

    def generate_tree(self):
        self.tree = self.__generate_tree_rec(self.data, self.features)

    def __generate_tree_rec(self, data, features):
        # If all data is of the same class, return a leaf node with that class
        if len(set([e["class"] for e in data])) == 1:
            return Node(True, data[0]["class"], None)
        
        # If there are no more features to split on, return a leaf node with the majority class
        if len(features) == 0:
            return Node(True, self.get_majority_class(data), None)
        
        best_feature, best_threshold, splitted_data = self.split_attribute(data, features)
        remaining_features = features.copy()
        remaining_features.remove(best_feature)

        node = Node(False, best_feature, best_threshold)
        node.children = [self.__generate_tree_rec(subset, remaining_features) for subset in splitted_data]

        return node
    
    def print_node(self, node, depth=0):
        if node.is_leaf:
            return
        else:
            left = node.children[0]
            if left.is_leaf:
                print(' ' * depth + node.label + ' <= ' + str(node.threshold) + ' : ' + left.label)
            else:
                print(' ' * depth + node.label + ' <= ' + str(node.threshold) + ' : ')
                self.print_node(left, depth + 4)
            if len(node.children) == 2:
                right = node.children[1]

                if right.is_leaf:
                    print(' ' * depth + node.label + ' > ' + str(node.threshold) + ' : ' + right.label)
                else:
                    print(' ' * depth + node.label + ' > ' + str(node.threshold) + ' : ')
                    self.print_node(right, depth + 4)

    def print_tree(self):
        self.print_node(self.tree)

    def get_accuracy(self):
        return self.__get_accuracy_rec(self.tree, self.data) / len(self.data)
    
    def __get_accuracy_rec(self, node, data):
        if node.is_leaf:
            return sum([1 for e in data if e["class"] == node.label])
        else:
            left_data = [e for e in data if e[node.label] <= node.threshold]
            if len (node.children) == 2:
                right_data = [e for e in data if e[node.label] > node.threshold]
                return self.__get_accuracy_rec(node.children[0], left_data) + self.__get_accuracy_rec(node.children[1], right_data)
            else:
                return self.__get_accuracy_rec(node.children[0], left_data)
        
    def predict(self, data):
        return self.__predict_rec(self.tree, data)
    
    def __predict_rec(self, node, data):
        if node.is_leaf:
            return node.label
        else:
            if data[node.label] <= node.threshold:
                return self.__predict_rec(node.children[0], data)
            else:
                return self.__predict_rec(node.children[1], data)
            
    def k_fold_cross_validation(self, k):
        save = self.data.copy()
        data = self.data.copy()
        data = [data[i::k] for i in range(k)]
        accuracies = []
        
        for i in range(k):
            test_data = data[i]
            train_data = []
            for j in range(k):
                if j != i:
                    train_data += data[j]
            
            self.data = train_data
            self.generate_tree()
            self.data = test_data
            accuracies.append(self.get_accuracy())
            
        self.data = save
        return sum(accuracies) / len(accuracies)