# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

import random
from AI import AI
from Action import Action

class block:

	def __init__(self, pos_x, pos_y, rowDimension, colDimension):

		# pos where this block is in
		self.x = pos_x
		self.y = pos_y

		# size of the board
		self.board_x = rowDimension
		self.board_y = colDimension

		# adjacent blocks must be in {3,5,8}, i.e. corner, side, middle blocks
		self.adjacent_blocks = 8
		if self.x == 0 or self.x == self.board_x-1:
			self.adjacent_blocks = self.adjacent_blocks - 3
		if self.y == 0 or self.y == self.board_y-1:
			self.adjacent_blocks = self.adjacent_blocks - 3
		if self.adjacent_blocks == 2:
			self.adjacent_blocks = 3

		# block status {-2:unknown, -1:flag, 0~n:number}
		self.status = -2

		self.adjacent_mines = 0
		self.adjacent_numbers = 0

	def uncover(self, num) -> None:
		if num<0:
			#print("Error, not positive result",num)
			return
		self.status = num

	def flag(self) -> None:
		if self.status >= 0:
			#print("can NOT flag an uncovered block.")
			return
		self.status = -1


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		print("start:",startX,startY)
		self.rows = rowDimension
		self.cols = colDimension
		self.tot_mine = totalMines
		self.board = \
			[
				[
					block(row, col, rowDimension, colDimension) for col in range(self.cols)
				]
				for row in range(self.rows)
			]

		self.last_move = Action(AI.Action.UNCOVER,startX,startY)


		self.solved = [] 		# List of Block Object
		self.solvable = [] 		# List of Action Object
		self.outer_edge = []	# List of Block Object

		#self.last_x = startX
		#self.last_y = startY
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		pass
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":
		# add the last result to board, and find a solve using logical inference
		x = self.last_move.getX()
		y = self.last_move.getY()
		if number >= 0:
			self.board[x][y].uncover(number)
			#print("last:",x, y,number)
			if (not self.board[x][y] in self.solved) and (not self.board[x][y] in self.outer_edge):
				self.outer_edge.append(self.board[x][y])
		else:
			#print("last flag:", x, y, number)
			self.board[x][y].flag()

		self.find_solve()

		if not self.solvable:
			self.logic_infer()

		# if can't make a inference, make a guess with possibility
		if not self.solvable:
			self.make_a_guess()

		next_move = self.solvable.pop()
		self.last_move = next_move
		#print("visit",next_move.getX(),next_move.getY(),next_move.getMove())
		return next_move




		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		#return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	# get the blocks around a block on the board
	def get_block_around(self, b) -> list:
		block_list = []
		x = b.x
		y = b.y
		for i in range(-1,2):
			for j in range(-1,2):
				if i==0 and j==0:
					continue
				if (x+i>=0 and x+i<self.rows) and (y+j>=0 and y+j<self.cols):
					block_list.append(self.board[x+i][y+j])
		#print("block_list size:", len(block_list))
		return block_list

	# find certain solves with the current map we have
	def solve_block(self, b) -> None:
		if b.status==-2:
			print("Can't slove blocks around an unsolved block.")
			return
		if b.status==-1:
			print("Can't slove blocks around a Mine.")
			return

		# check how many blocks around are solved or are mines.
		block_list = self.get_block_around(b)
		mine_cnt = 0
		uncovered_cnt = 0
		unsolved = []
		for adj_block in block_list:
			if adj_block.status == -1:
				mine_cnt = mine_cnt + 1
			elif adj_block.status >= 0:
				uncovered_cnt = uncovered_cnt + 1
			elif adj_block.status == -2:
				unsolved.append(adj_block)
			else:
				print("Error status in this block:", b.x, b.y)
				return

		# if all blocks around has a status>=-1, the block is solved
		if mine_cnt + uncovered_cnt == b.adjacent_blocks:
			self.solved.append(b)
			self.outer_edge.remove(b)

		#print("mine, uncovered, unsolved, status:" ,mine_cnt,uncovered_cnt,len(unsolved),b.status)
		# if all are solvable (i.e. enough mines flagged around)
		if mine_cnt==b.status:
			for solvable_block in unsolved:
				act = Action(AI.Action.UNCOVER, solvable_block.x, solvable_block.y)
				if not act in self.solvable:
					self.solvable.append(act)

		# if all are mines (i.e. all uncovered blocks around are mines)
		if len(unsolved) == b.status-mine_cnt:
			for solvable_block in unsolved:
				act = Action(AI.Action.FLAG, solvable_block.x, solvable_block.y)
				if not act in self.solvable:
					self.solvable.append(act)


	# find direct solve from outer_edge if possible
	def find_solve(self) -> None:
		for block_edge in self.outer_edge:
			print("Solving block:", block_edge.x, block_edge.y)
			self.solve_block(block_edge)

	# if direct solve from outer_edge is impossible, try get one using login inference
	def logic_infer(self) -> None:
		for block_edge in self.outer_edge:
			print("Solving block:", block_edge.x, block_edge.y)
			self.solve_block(block_edge)

	# if both direct solve and logic solve failed, uncover any block(evaluate probability in each block and uncover one
	def make_a_guess(self) -> None:
		x = random.randrange(self.cols)
		y = random.randrange(self.rows)
		if (not self.board[x][y] in self.solved) and (not self.board[x][y] in self.outer_edge):
			self.solvable.append(Action(AI.Action.UNCOVER,x,y))
			print("guess:",x,y)
		else:
			self.make_a_guess()
