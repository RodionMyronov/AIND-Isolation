"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass

def openmove_div_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.
    Divide # of player's open moves to # of opponent open moves.
    Reduce score if player is not active and at least on of his open moves
    can be occupied by opponent at the next ply.

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
    # return immediate result if the game is in terminal state
    if game.utility(player) != 0:
        return game.utility(player)
    # calculate score
    my_moves = game.get_legal_moves(player)
    opponent_moves = game.get_legal_moves(game.get_opponent(player))
    if len(opponent_moves) == 0:
        return float("+inf")
    result = len(my_moves)/len(opponent_moves)
    # reduce score for passive player if needed
    if player != game.active_player and len([m for m in my_moves if m in opponent_moves]) > 0:
        result -= 1/len(opponent_moves)
        
    return float(result)

def get_drill_value(loc, blanks, is_active_player, opp_moves, maxdepth, depth = 1):
    """Return "value" of the board location.
    See heuristic_analysis.pdf for rationale and details.
    
    Parameters
    ----------
    loc : (<int>,<int>) 
        Some location at he game board
        
    blanks: [(<int>,<int>)]
        A list of non-occupied locations at the board
        
    is_active_player: boolean
        If value is calculated for active player or not
        
    opp_moves: [(<int>,<int>)]
        list of locations available from current opponent's location
        
    maxdepth: int
        maximum recursion depth allowed
        
    depth: int
        current recursion depth

    Returns
    -------
    float
        The heuristic value of the given location.
    
    """
    if len(blanks) == 0 or maxdepth == 0:
        return 0
    
    # copied from isolation.py. It would be better if Board class externalized this.
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),  (1, 2), (2, -1),  (2, 1)]
    
    # get all blanks reachable from current location
    moves = [(loc[0] + dr, loc[1] + dc) for dr,dc in directions if (loc[0] + dr, loc[1] + dc) in blanks]
    
    # check if we should account for opponent's next ply 
    if not is_active_player and len(opp_moves) > 0 :
        common_moves_count = len([m for m in moves if m in opp_moves])
    else:
        common_moves_count = 0
      
    # recursuvely calculate the value of current location
    result = 0
    for move in moves:
        newblanks = blanks[:]
        newblanks.remove(move)
        # if some blank field can be occupied by active opponent at the next ply, reduce its value
        reductor = 1 if common_moves_count == 0 else (common_moves_count-1)/common_moves_count
        result = result + reductor*(depth + get_drill_value(move,newblanks,False,[],maxdepth-1, depth+1))
    return float(result)

def drilldown_score(game, player):
    """Calculate "Drilldown" heuristic score.
    Value is calculated as a rate bitween player's drill value 
    and opponent's drill value
    """
    
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
    

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.
    Use openmove_div_score if 60% or more of game board is free.
    Use drilldown_score otherwise.

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
    free_board_part = len(game.get_blank_spaces())/(game.width*game.height)
    if free_board_part >= 0.6:
        return openmove_div_score(game, player)
    else:
        return drilldown_score(game, player)



class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        assert self.method in ['minimax','alphabeta'], 'Invalid search method {0}'.format(self.method)
        self.search_function = self.minimax if self.method == 'minimax' else self.alphabeta
        

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left
        best_move = (-1,-1)
        # exit if there are no legal moves
        if len(legal_moves) == 0:
            return (-1,-1)

        current_depth = 1
        try:
            if self.iterative:
                # TODO: invent better iterative deepening exit condition?
                while current_depth <= len(game.get_blank_spaces()):
                    _, best_move = self.search_function(game, current_depth)
                    current_depth += 1
            else:
                _, best_move = self.search_function(game, self.search_depth)
        except Timeout:
            # No actions currently, we just return the best move found
            #print('Blanks = {0}, timeout depth = {1}'.format(len(game.get_blank_spaces()),current_depth))
            pass

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
            
       
        # if max. depth is reached or this is a leaf node - return score
        if depth == 0 or len(game.get_legal_moves()) == 0:
            return self.score(game, self), (-1,-1) # we are not looking for move here, so returning (-1,-1)
        # get scores for all child states
        best_score = float("-inf") if maximizing_player else float("inf")
        best_move = (-1,-1)
        for move in game.get_legal_moves():
            score, _ = self.minimax(game.forecast_move(move), depth-1, not maximizing_player)
            if (maximizing_player and score > best_score) or (not maximizing_player and score < best_score):
                best_score, best_move = score, move
             
        return best_score, best_move
    
    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
            
         # if max. depth is reached or this is a leaf node - return score
        if depth == 0 or len(game.get_legal_moves()) == 0:
            return self.score(game, self), (-1,-1) # we are not looking for move here, so returning (-1,-1)
            
        # get scores for all child states
        best_score = float("-inf") if maximizing_player else float("inf")
        best_move = (-1,-1)
        new_alpha, new_beta = alpha, beta
        for move in game.get_legal_moves():
            score, _ = self.alphabeta(game.forecast_move(move), depth-1, new_alpha, new_beta,not maximizing_player)
            if (maximizing_player and score > best_score) or (not maximizing_player and score < best_score):
                best_score, best_move = score, move
                # set new alpha or beta value
                if maximizing_player:
                    new_alpha = best_score
                else:
                    new_beta = best_score
            # alpha-beta pruning
            if (maximizing_player and score >= beta) or (not maximizing_player and score <= alpha):
                break 
             
        return best_score, best_move
