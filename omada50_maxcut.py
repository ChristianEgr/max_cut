import argparse
import random as rng

import networkx as nx


def cut_calculator(G, A, B):
    cut = 0
    for NODE in A:
        (sum_own_side, sum_other_side) = total_weight_of_sides(G, NODE, A, B);
        cut += sum_other_side
    return cut


def total_weight_of_sides(G, v, A, B):
    sum_own_side = 0
    sum_other_side = 0
    if v in A:
        # print("v blongs to A");
        Vgroup = A
        OtherGroup = B
    elif v in B:
        # print("v belongs to B");
        Vgroup = B
        OtherGroup = A
    # get all neigbors of v
    vNodeNeigbors = list(G.neighbors(v));
    for NODE in vNodeNeigbors:
        if NODE in Vgroup:
            # print("same group");
            obj1 = G.get_edge_data(v, NODE)
            sum_own_side += obj1['weight']
        elif NODE in OtherGroup:
            # print("other group");
            obj2 = G.get_edge_data(v, NODE)
            sum_other_side += obj2['weight']
    return sum_own_side, sum_other_side


def local_search_maxcut_orig(G, A, B):
    Anew = A[:]
    Bnew = B[:]
    cut = cut_calculator(G, A, B)
    same = 0
    print(cut)
    for i in range(50):
        for NODE in Anew:
            # Get the weigts for a specific node
            (sum_own_side, sum_other_side) = total_weight_of_sides(G, NODE, Anew, Bnew)
            # Check if own sum weight >= other sum weight
            if sum_own_side > sum_other_side:
                # If so , flip (i.e remove node from A and put node to B)
                Anew.remove(NODE)
                Bnew.append(NODE)
        for NODE in Bnew:
            # Get the weights for a specific node
            (sum_own_side, sum_other_side) = total_weight_of_sides(G, NODE, Anew, Bnew)
            # Check if own sum weight >= other sum weight
            if sum_own_side > sum_other_side:
                # If so , flip (i.e remove node from A and put node to B)
                Bnew.remove(NODE)
                Anew.append(NODE)

        new_cut = cut_calculator(G, Anew, Bnew)
        print(f'Cut: {new_cut}')

        if new_cut == cut:
            same += 1
        cut = new_cut
        if same > 5:
            break
    return Anew, Bnew


def local_search_maxcut_kl(G, A, B):
    Anew = A[:]
    Bnew = B[:]
    cut = cut_calculator(G, A, B)
    print(cut)
    flipped = []
    same = 0
    for i in range(1000):
        flip_gain_of_node = {}
        for NODE in Anew:
            # Get the weights for a specific node
            (sum_own_side, sum_other_side) = total_weight_of_sides(G, NODE, Anew, Bnew)
            # Check if own sum weight >= other sum weight
            if sum_own_side > sum_other_side:
                flip_gain_of_node[NODE] = sum_own_side-sum_other_side

        for NODE in Bnew:
            # Get the weights for a specific node
            (sum_own_side, sum_other_side) = total_weight_of_sides(G, NODE, Anew, Bnew)
            # Check if own sum weight >= other sum weight
            if sum_own_side > sum_other_side:
                flip_gain_of_node[NODE] = sum_own_side-sum_other_side

        sorted_nodes = sorted(flip_gain_of_node, key=flip_gain_of_node.get, reverse=True)
        k = 3
        for best_node in sorted_nodes[0:k]:
            if best_node not in flipped:
                if best_node in Anew:
                    Anew.remove(best_node)
                    Bnew.append(best_node)
                else:
                    Anew.append(best_node)
                    Bnew.remove(best_node)
                flipped.append(best_node)

        new_cut = cut_calculator(G, Anew, Bnew)
        print(new_cut)
        if new_cut == cut:
            same += 1
        cut = new_cut
        if same > 10:
            break

    return Anew, Bnew

def local_search_maxcut(G, A, B):
    Anew = A[:]
    Bnew = B[:]
    A_B = [*Anew, *Bnew]
    CUT = cut_calculator(G, A, B)
    print(CUT)
    k = 1
    for i in range(10):
        print(f'Iteration i={i}')
        for j in range(0, len(A_B), k):
            nodes = list()
            if j+k <= len(A):
                nodes = A_B[j:j+k]
            else:
                nodes = A_B[j:len(A_B)]
            # Get the weights for a specific node
            current_cut = cut_calculator(G, Anew, Bnew)
            if current_cut > 2580000:
                break
            print(f'Current cut={current_cut}')
            A_tmp = Anew.copy()
            B_tmp = Bnew.copy()
            for node in nodes:
                if node in A_tmp:
                    A_tmp.remove(node)
                    B_tmp.append(node)
                else:
                    B_tmp.remove(node)
                    A_tmp.append(node)
            new_cut = cut_calculator(G, A_tmp, B_tmp)
            # Check if cut is better
            if new_cut > current_cut:
                Anew = A_tmp.copy()
                Bnew = B_tmp.copy()
                print(f'New cut={new_cut}')

    return Anew, Bnew


def compute_partitions(G):
    # Implement your maxcut algorithm
    n = len(G.nodes)
    middle = int(n / 2)
    A = list(range(0, middle))
    B = list(range(middle, n))
    all = list(range(0, n))
    rng.shuffle(all)
    partition_A = all[0:middle]
    partition_B = all[middle:n]
    return partition_A, partition_B


parser = argparse.ArgumentParser()
G = nx.read_weighted_edgelist('maxcut_challenge_graph.edgelist', nodetype=int)
parser.add_argument('-print_partition', action='store_true', help='Print the partition A, B')
SEED = 33
rng = rng.Random(SEED)
A, B = compute_partitions(G)

print('Initiated local search')
A, B = local_search_maxcut_kl(G, A, B)
print('Local search finished')

cut_size = nx.algorithms.cut_size(G, A, weight='weight')
if cut_size >= 2600000:
    print(True)
else:
    print(f'The cut_size is {cut_size} but must be at least 2600000')

args = parser.parse_args()
all_flag_values = parser.parse_args()
flag_print_partition = all_flag_values.print_partition
if flag_print_partition:
    print(f'{A=}')
    print(f'{B=}')
