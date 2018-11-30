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

class block():

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

"""
# logic unit of knowledge_base class
class statement():

	def __init__(self):
		self.tile_list = []	# list of tiles in the statement
		self.mine_cnt = 0	# number of mines in tile list

	# get result from two knowledge base statements,
	# return a new statement if the input statement covers a part of this statement,
	# if two statements can't resolve return None.
	# e.g. stmt1 = ([a,b,c], 1 mine), stmt2 = ([b,c], 1 mine),
	# stmt1 - stmt2 = ([a],0 mine)
	def minus(self, stmt) -> "statement Object":
		all_in_stmt = True
		for tile in stmt.tile_list:
			if tile not in self.tile_list:
				all_in_stmt = False
				break
		if all_in_stmt :
			result = statement()
			for tile in self.tile_list:
				if tile not in stmt.tile_list:
					result.tile_list.append(tile)
			result.mine_cnt = self.mine_cnt - stmt.mine_cnt
			return result
		else:
			return None
"""

class knowledge_base():

	def __init__(self, board, solvable, outer_edge, tot_mine, rows, cols):
		self.board = board
		self.solvable = solvable
		self.outer_edge = outer_edge
		self.tot_mine = tot_mine
		self.rows = rows
		self.cols = cols
		self.statement_list = []	# list of true statements
		self.infer_result = []		# list of solvable statements

		# stmt representing all uncovered tiles
		stmt = {"tile_list":[],"mine_cnt":0}
		mine_flaged = 0
		for (x,line) in enumerate(board):
			for (y,tile) in enumerate(line):
				if tile.status==-1:
					mine_flaged = mine_flaged + 1
				elif tile.status==-2:
					stmt["tile_list"].append(tile)

		stmt["mine_cnt"] = tot_mine - mine_flaged
		if stmt["mine_cnt"] <= 5:	# don't search global if to much of the board is unsolved
			self.statement_list.append(stmt)

		# add a statement when the tile is uncovered and on the edge
		for tile in outer_edge:
			if tile.status >= 0:
				adj_mine = 0
				stmt = {"tile_list":[],"mine_cnt":0}
				block_list = self.get_block_around(tile)
				for adj_block in block_list:
					if adj_block.status==-2:
						stmt["tile_list"].append(adj_block)
					elif adj_block.status==-1:
						adj_mine = adj_mine + 1
				stmt["mine_cnt"] = tile.status-adj_mine
				if stmt not in self.statement_list:
					self.statement_list.append(stmt)

		#print("KB init ends")

	def get_block_around(self, b) -> list:
		block_list = []
		x = b.x
		y = b.y
		for i in range(-1, 2):
			for j in range(-1, 2):
				if i == 0 and j == 0:
					continue
				if (x + i >= 0 and x + i < self.rows) and (y + j >= 0 and y + j < self.cols):
					block_list.append(self.board[x + i][y + j])
		# print("block_list size:", len(block_list))
		return block_list

	# if the number of tiles is the same with mine or there is no mines.
	def is_solveable(self,stmt) -> bool:
		if not stmt["tile_list"]: # must be at least 1 element in list
			return False
		if stmt["mine_cnt"]==0 or len(stmt["tile_list"])==stmt["mine_cnt"]:
			return True
		return False

	def minus(self, stmt1, stmt2) -> dict:
		all_in_stmt = True
		for tile in stmt1["tile_list"]:
			if tile not in stmt2["tile_list"]:
				all_in_stmt = False
				break
		if all_in_stmt:
			result = {"tile_list":[],"mine_cnt":0}
			for tile in stmt2["tile_list"]:
				if tile not in stmt1["tile_list"]:
					result["tile_list"].append(tile)
			result["mine_cnt"] = stmt2["mine_cnt"] - stmt1["mine_cnt"]
			return result
		else:
			return None


	# find solvable statements in self.infer_result;
	def solve(self) -> None:
		# when new statement is found, search again
		found_new_statement = True
		while found_new_statement:
			found_new_statement = False
			# for each pair of statements, try generate new statement using the two
			new_stmt_list = []
			for stmt in self.statement_list:
				for other_stmt in self.statement_list:
					if stmt!=other_stmt:
						new_stmt = self.minus(stmt, other_stmt)
						if new_stmt!=None:	# new statement is valid
							if self.is_solveable(new_stmt):
								if new_stmt not in self.infer_result:
									self.infer_result.append(new_stmt)
							else:
								if (new_stmt not in self.statement_list) and (new_stmt not in new_stmt_list):
									new_stmt_list.append(new_stmt)
									found_new_statement = True
			self.statement_list.extend(new_stmt_list)
			#print(len(new_stmt_list))

		# add the solvables found to list
		for stmt in self.infer_result:
			if stmt["mine_cnt"]==0:
				for tile in stmt["tile_list"]:
					self.solvable.append(Action(AI.Action.UNCOVER,tile.x,tile.y))
			elif len(stmt["tile_list"])==stmt["mine_cnt"]:
				for tile in stmt["tile_list"]:
					self.solvable.append(Action(AI.Action.FLAG,tile.x,tile.y))


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.rows = colDimension
		self.cols = rowDimension
		#print("max row & col:",self.rows,self.cols)
		self.tot_mine = totalMines
		self.board = \
			[
				[
					block(row, col, self.rows, self.cols) for col in range(self.cols)
				]
				for row in range(self.rows)
			]

		self.last_move = Action(AI.Action.UNCOVER,startX,startY)
		self.first_step = (startX,startY)

		self.solved = [] 		# List of Block Object , where everything around such block is a number or a flag
		self.solvable = [] 		# List of Action Object, to be uncovered or flaged
		self.outer_edge = []	# List of Block Object , blocks uncovered but has surrounded blocks untouched.

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
				#print("outer_edge added",x,y)
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

		#for act in self.solvable:
			#print(act.getX(),act.getY())
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

	# find certain solves around b with the current map we have
	def solve_block(self, b) -> None:
		if b.status==-2:
			#print("Can't slove blocks around an unsolved block.")
			return
		if b.status==-1:
			#print("Can't slove blocks around a Mine.")
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
				#print("Error status in this block:", b.x, b.y)
				return

		# if all blocks around has a status>=-1, the block is solved
		if mine_cnt + uncovered_cnt == b.adjacent_blocks:
			self.solved.append(b)
			self.outer_edge.remove(b)
			#print("outer_edge removed",b.x,b.y,mine_cnt,uncovered_cnt)

		#print("mine, uncovered, unsolved, status:" ,mine_cnt,uncovered_cnt,len(unsolved),b.status)
		# if all are solvable (i.e. enough mines flagged around)
		if mine_cnt==b.status:
			for solvable_block in unsolved:
				act = Action(AI.Action.UNCOVER, solvable_block.x, solvable_block.y)
				exist = False
				for sol in self.solvable:
					if sol.getX()==solvable_block.x and sol.getY()==solvable_block.y:
						exist = True
				if not exist:
					#print("from",b.x,b.y,"solve",solvable_block.x,solvable_block.y)
					self.solvable.append(act)

		# if all are mines (i.e. all uncovered blocks around are mines)
		if len(unsolved) == b.status-mine_cnt:
			for solvable_block in unsolved:
				act = Action(AI.Action.FLAG, solvable_block.x, solvable_block.y)
				exist = False
				for sol in self.solvable:
					if sol.getX() == solvable_block.x and sol.getY() == solvable_block.y:
						exist = True
				if not exist:
					#print("from",b.x,b.y,"solve",solvable_block.x,solvable_block.y)
					self.solvable.append(act)


	# find direct solve from outer_edge if possible
	def find_solve(self) -> None:
		for block_edge in self.outer_edge:
			#print("Solving block:", block_edge.x, block_edge.y)
			self.solve_block(block_edge)

	# if direct solve from outer_edge is impossible, try get one using login inference
	def logic_infer(self) -> None:
		#"""
		#print(self.solvable)
		KB = knowledge_base(board=self.board, solvable=self.solvable, outer_edge=self.outer_edge, tot_mine=self.tot_mine, rows=self.rows, cols=self.cols)
		KB.solve()
		#print(self.solvable)
		#"""
		pass

	# if both direct solve and logic solve failed, uncover any block(evaluate probability in each block and uncover one
	def make_a_guess(self) -> None:
		unsolved_list = [self.first_step]
		for x in range(0,self.rows):
			for y in range(0,self.cols):
				if(self.board[x][y].status==-2):
					unsolved_list.append((x,y))

		(x,y) = random.choice(unsolved_list)
		#if (not self.board[x][y] in self.solved) and (not self.board[x][y] in self.outer_edge):
		self.solvable.append(Action(AI.Action.UNCOVER,x,y))
		#print("guess:",x,y)
		#print("outer_edge")
		#for tile in self.outer_edge:
			#print("(",tile.x,tile.y,")",end=' ')
		#else:
			#self.make_a_guess()
