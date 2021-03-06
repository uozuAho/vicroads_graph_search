""" Convert vicroads declared roads kml to a graph """


import unittest

import kd_tree


def placemarks_to_graph(placemarks):
    """ Converts all points in the given placemarks to graph nodes, connecting
        nodes on the same road, and nodes that are close to each other
    """
    print('pm to nodes...')
    nodes = placemarks_to_nodes(placemarks)
    print('join close nodes...')
    add_edges_between_close_nodes(nodes)
    print('done')
    return nodes


def add_edges_between_close_nodes(nodes, max_dist_squared=.0000000000001):
    tree = kd_tree.create(nodes)
    for node in nodes:
        nearest_kdnode, dist_squared = tree.search_knn(node.xy, 2)[1]
        if dist_squared <= max_dist_squared:
            nearest_node = nearest_kdnode.data
            node.adjacent.add(nearest_node.idx)
            nearest_node.adjacent.add(node.idx)


def placemarks_to_nodes(placemarks):
    """ Extract placemark points to Nodes """
    nodes = []
    nodes_idx = 0
    for p in placemarks:
        for point_num in range(len(p.points)):
            point = p.points[point_num]
            node = road_point_to_node(point, nodes_idx)
            # add edge between points on same placemark (same road)
            if point_num > 0:
                nodes[-1].adjacent.add(nodes_idx)
                node.adjacent.add(nodes_idx - 1)
            nodes.append(node)
            nodes_idx += 1
    return nodes


def road_point_to_node(point, idx):
    return Node(idx, point.lon, point.lat)


class Node:
    def __init__(self, idx, x, y):
        self.idx = idx
        self.x = x
        self.y = y
        self.xy = (x, y)
        # adjacent Node idxs
        self.adjacent = set([])

    def __len__(self):
        return 2

    def __getitem__(self, i):
        return self.xy[i]

    def __str__(self):
        return '{}: ({}, {})'.format(self.idx, self.x, self.y)


class KmlToGraphTests(unittest.TestCase):
    def test_kd_tree_basics(self):
        n1 = Node(1, 0, 0)
        n2 = Node(2, 5, 0)
        n3 = Node(3, 5, 5)
        nodes = [n1, n2, n3]
        tree = kd_tree.create(nodes)
        closest_to_origin = [n.data.idx for n, dist in tree.search_knn((0, 0), 2)]
        self.assertEqual(closest_to_origin, [1, 2])

    def test_add_close_node_edges(self):
        n1 = Node(1, 0, 0)
        n2 = Node(2, 5, 0)
        n3 = Node(3, 5, 5)
        nodes = [n1, n2, n3]
        add_edges_between_close_nodes(nodes, 25)
        self.assertEqual(n1.adjacent, set([2]))
        self.assertEqual(n2.adjacent, set([1, 3]))
        self.assertEqual(n3.adjacent, set([2]))

    def test_placemarks_to_nodes(self):
        pm1 = TestPlacemark([TestPoint(0, 0)])
        pm2 = TestPlacemark([TestPoint(1, 0), TestPoint(1, 1)])
        nodes = placemarks_to_nodes([pm1, pm2])
        self.assertEqual(len(nodes), 3)
        n0 = nodes[0]
        n1 = nodes[1]
        n2 = nodes[2]
        self.assertEqual(n0.adjacent, set([]))
        self.assertEqual(n1.adjacent, set([2]))
        self.assertEqual(n2.adjacent, set([1]))


class TestPlacemark:
    def __init__(self, points):
        self.points = points


class TestPoint:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

if __name__ == '__main__':
    unittest.main()
    # main()