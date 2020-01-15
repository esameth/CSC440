import rubik
from collections import deque

# Class to store the state of the node
class node_info:
    def __init__(self, st, parent, order):
        self.st = st
        self.parent = parent
        self.order = order

# Gets the next frontier
def next_frontier(frontier, p_nodes):
    starting_order = frontier[0].order

    # At each iteration, we are looking at the nodes in the frontier of the same order as starting_order
    while starting_order == frontier[0].order:
        elm = frontier.popleft()
        # Changes the rubik state
        for move in rubik.quarter_twists:
            move_st = rubik.perm_apply(move, elm.st)
            # Checks to see if the new move_st is not in the nodes list
            if move_st not in p_nodes:
                # new node_info with the new move_st, the move command it took
                # frontier that was popped, and the new depth of node
                new_st = node_info(move_st, (move, elm), elm.order + 1)
                frontier.append(new_st)
                p_nodes.append(move_st)

"""
Using 2-way BFS, finds the shortest path from start_position to
end_position. Returns a list of moves.
You can use the rubik.quarter_twists move set.
Each move can be applied using rubik.perm_apply
"""
def shortest_path(start, end):
    # Start side of BFS
    start_init = node_info(start, (None, None), 0)
    s_frontier = deque([start_init])
    s_parents = []

    # End side of BFS
    end_init = node_info(end, (None, None), 0)
    e_frontier = deque([end_init])
    e_parents = []
    
    # Flag determines which side we need to advance the frontier
    # When flag is 1 it means that we might advance the left frontier
    # When flag is -1 it means we might advance the right frontier
    flag = 1

    # Test to see if the two given states (start, end) are the same
    # We know to return an empty list

    for l_elm in s_frontier:
        for r_elm in e_frontier:
            if l_elm.st == r_elm.st:
                return []

    found = False

    # Given that we have not found a solution, the function will alternate between the start and end 
    # sides (bidirectional) to create a new frontier and check its values for a solution
    while not found:
        # Checks the depth of the nodes in both frontiers
        # If their order exceeds 7, then there is no shortest path
        if s_frontier[0].order > 6 and e_frontier[0].order > 6:
            return None

        # Flag alternates the sides
        if flag == 1:
            # Gets the next frontier
            next_frontier(s_frontier, s_parents)
            flag = flag * (-1)
        else:
            # Gets the next frontier
            next_frontier(e_frontier, e_parents)
            flag = flag * (-1)

        # Checking to see if there is the same block state in each list
        
        # Grabs a left element from the starting frontier
        for l_elm in s_frontier:
            # Compares it to each of the right elements from the end frontier
            for r_elm in e_frontier:
                # If we find an element that matches
                if l_elm.st == r_elm.st:
                    # Find the intersect of the two lists
                    intersect = (l_elm, r_elm)
                    # We set found to true
                    found = True
                    # Then break out of the loop
                    break
            # If the element was found we can break out of this loop as well
            if found == True:
                break
    # Creates a lsit for return
    final_list = []
    # Temp variable to hold l_elm
    l_temp = intersect[0]
    
    # Gets the parent of l_temp (l_elm) until the start state
    while (l_temp.st != start):
        final_list.insert(0, l_temp.parent[0])
        l_temp = l_temp.parent[1]

    r_temp = intersect[1]

    # Gets the parent of r_temp (r_elm) until the end state
    # Perm inverse is because we have to do the inverse of each move to get the parent.
    while (r_temp.st != end):
        final_list.append(rubik.perm_inverse(r_temp.parent[0]))
        r_temp = r_temp.parent[1]

    return final_list
