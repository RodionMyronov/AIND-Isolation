# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 13:03:48 2017

@author: Rodion
"""
import random

def random_score(game, player):
    return random.random()

def utility_score(game, player):
    return game.utility(player)

def openmove_div_score(game, player):
    if game.utility(player) != 0:
        return game.utility(player)
    my_moves = game.get_legal_moves(player)
    opponent_moves = game.get_legal_moves(game.get_opponent(player))
    if len(opponent_moves) == 0:
        return float("+inf")
    result = len(my_moves)/len(opponent_moves)
    if player != game.active_player and len([m for m in my_moves if m in opponent_moves]) > 0:
        result -= 1/len(opponent_moves)
    return float(result)


def get_drill_value(loc, blanks, is_active_player, opp_moves, maxdepth, depth = 1):
    if len(blanks) == 0 or maxdepth == 0:
        return 0
    result = 0
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),  (1, 2), (2, -1),  (2, 1)]
    # get all blanks reachable from current location
    moves = [(loc[0] + dr, loc[1] + dc) for dr,dc in directions if (loc[0] + dr, loc[1] + dc) in blanks]
    if not is_active_player and len(opp_moves) > 0 :
        common_moves_count = len([m for m in moves if m in opp_moves])
    else:
        common_moves_count = 0
    for move in moves:
        newblanks = blanks[:]
        newblanks.remove(move)
        reductor = 1 if common_moves_count == 0 else (common_moves_count-1)/common_moves_count
        result = result + reductor*(depth + get_drill_value(move,newblanks,False,[],maxdepth-1, depth+1))
    return float(result)
    
def drilldown_score(game, player):
    if game.utility(player) != 0:
        return game.utility(player)
    blanks = game.get_blank_spaces()
    my_drill = get_drill_value(game.get_player_location(player)
                              ,blanks
                              ,player == game.active_player
                              ,game.get_legal_moves(game.get_opponent(player))
                              ,5)
    opp_drill = get_drill_value(game.get_player_location(game.get_opponent(player))
                               ,blanks
                               ,player != game.active_player
                               ,game.get_legal_moves(player)
                               ,5)
    if opp_drill != 0:
        return float(my_drill/opp_drill)
    else:
        return float("+inf")
    #return float(my_drill - opp_drill)

def centroid_score(game, player):
    if game.utility(player) != 0:
        return game.utility(player)
    my_loc = game.get_player_location(player)
    return float(abs(my_loc[0]-game.height/2) + abs(my_loc[1]-game.width/2))
    

def longest_path_value(loc, blanks):
    if len(blanks) == 0:
        return 0
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),  (1, 2), (2, -1),  (2, 1)]
    # get all blanks reachable from current location
    moves = [(loc[0] + dr, loc[1] + dc) for dr,dc in directions if (loc[0] + dr, loc[1] + dc) in blanks]
    max_result = float("-inf")
    for move in moves:
        newblanks = blanks[:]
        newblanks.remove(move)
        result = 1 + longest_path_value(move,newblanks)
        if result > max_result:
            max_result = result
    return float(max_result)

def longest_path_score(game, player):
    my_path = longest_path_value(game.get_player_location(player),game.get_blank_spaces())
    opp_path = longest_path_value(game.get_player_location(game.get_opponent(player)),game.get_blank_spaces())
    return float(my_path-opp_path)

def combined_score_v1(game, player):
    free_board_part = len(game.get_blank_spaces())/(game.width*game.height)
    if free_board_part >= 0.6:
        return openmove_div_score(game, player)
    else:
        return drilldown_with_opponent_score(game, player)
    
def combined_score_v2(game, player):
    free_board_part = len(game.get_blank_spaces())/(game.width*game.height)
    if free_board_part >= 0.5:
        return openmove_div_score(game, player)
    else:
        return longest_path_score(game, player)


def agressive_score(game, player):
    moves = game.get_legal_moves()
    side_coef = 1 if player == game.active_player else -1
    
    if len(moves) == 0:
        result = float("-inf")
    else:
        result = len(moves)
        
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),  (1, 2), (2, -1),  (2, 1)]
    player_pos = game.get_player_location(player)
    opponent_pos = game.get_player_location(game.get_opponent(player))
    if player_pos in [(opponent_pos[0]+dr,opponent_pos[1]+dc) for dr, dc in directions]:
        result -= 0.5
    else:
        result += 0.5

    return float(result*side_coef)

'''
def width_and_depth_score(game, player):
    if game.utility(player) != 0:
        return game.utility(player)
    
    board_size = game.width * game.height
    blanks = game.get_blank_spaces()
    if len(blanks)/board_size > 0.33:
        return len(game.get_legal_moves(player))-len(game.get_legal_moves(game.get_opponent(player)))
    else:
'''
 


def open_positions_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    moves = game.get_legal_moves()
    side_coef = 1 if player == game.active_player else -1
    
    if len(moves) == 0:
        result = float("-inf")
    else:
        result = len(moves)
        
    
    return float(result*side_coef)

custom_score = drilldown_score