# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 19:38:22 2017

@author: Rodion
"""
'''
import isolation
import game_agent

p1 = game_agent.CustomPlayer()
p2 = game_agent.CustomPlayer()
b = isolation.Board(p1,p2,2,2)
p1.get_move(b,b.get_legal_moves(),lambda: 50)
'''

import heuristics

'''
blanks = [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5)
         ,(1,0),(1,1),(1,4),(1,5),(1,6)
         ,(2,0),(2,6)
         ,(3,0),(3,5),(3,6)
         ,(4,0),(4,5),(4,6)
         ,(5,0),(5,1),(5,2),(5,5),(5,6)
         ,(6,0),(6,2),(6,3),(6,4),(6,5),(6,6)
         ]
'''
blanks = [(0,0)]
opp_moves = [(0,0)]

my_loc = (1,2)
opp_loc = (2,1)


print(heuristics.get_drill_value_with_opponent(my_loc,blanks,True, opp_moves,10))
print(heuristics.get_drill_value_with_opponent(opp_loc,blanks,False, opp_moves,10))