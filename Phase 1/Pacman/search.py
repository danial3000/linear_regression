# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state
        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def depthFirstSearch(problem):
    q = util.Queue()
    empty_action_list = []
    visited = set()
    q.push((problem.getStartState(), empty_action_list))
    visited.add(problem.getStartState())
    while not q.isEmpty():
        current_node, list_of_actions = q.pop()
        if problem.isGoalState(current_node):
            return list_of_actions
        for info in problem.getSuccessors(current_node):
            successor, action, step_cost = info
            if successor not in visited:
                new_list = list_of_actions + [action]
                q.push((successor, new_list))
                visited.add(successor)

    return empty_action_list


def breadthFirstSearch(problem):
    q = util.Queue()
    empty_action_list = []
    visited = set()
    q.push((problem.getStartState(), empty_action_list))
    visited.add(problem.getStartState())
    while not q.isEmpty():
        current_node, list_of_actions = q.pop()
        if problem.isGoalState(current_node):
            return list_of_actions
        for info in problem.getSuccessors(current_node):
            successor, action, step_cost = info
            if successor not in visited:
                new_list = list_of_actions + [action]
                q.push((successor, new_list))
                visited.add(successor)

    return empty_action_list


def uniformCostSearch(problem):

    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


def nullHeuristic(state, problem=None):
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):

    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
