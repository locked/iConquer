'''
 * iConquer - Online C&C-like game
 * Copyright (C) 2009-2010 Adam Etienne <etienne.adam@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * $Id$
'''
import os,sys,getopt,time,datetime,random
from math import sqrt

class AStarJS:
	def __init__(self, Grid):
		self.myGrid = Grid

	def findPath(self, Start, Goal, Find="Euclidean"):
		self.Start = Start
		self.Goal = Goal
		self.Find = Find
		self.cols = len(self.myGrid[0])
		self.rows = len(self.myGrid)
		self.limit = self.cols * self.rows
		self.Distance = { 'Diagonal': 'Diagonal', 'DiagonalFree': 'Diagonal', 'Euclidean': 'Euclidean', 'EuclideanFree': 'Euclidean', 'Manhattan': 'Manhattan' }
		if self.Find not in self.Distance:
			self.Find = 'Manhattan'
		return self.Path()

	def Grid(self, x, y):
		if x>=0 and y>=0 and x<self.cols-1 and y<self.rows-1:
			if (self.myGrid[y][x][0]>0 and self.myGrid[y][x][0]<20) or self.myGrid[y][x][1]>0:
				return False
			return True
		return False

	def Node(self, Parent, Point):
		return { 'Parent': Parent, 'value': Point['x'] + (Point['y'] * self.cols), 'x': Point['x'], 'y': Point['y'], 'f': 0, 'g': 0 };

	def Path(self):
		myStart = self.Node(None, { 'x': self.Start[0], 'y': self.Start[1] })
		myGoal = self.Node(None, { 'x': self.Goal[0], 'y': self.Goal[1] })
		AStar = {}
		Open = [myStart]
		Closed = []
		result = []
		length = len(Open)
		length=len(Open)
		print "SEARCH PATH: ", myStart['x'], myStart['y'], myGoal['x'], myGoal['y']
		while length>0:
			max = self.limit
			min = -1
			for i in range( 0, len(Open) ):
				o = Open[i]
				if (o['f'] < max):
					max = o['f']
					min = i
			myNode = Open[min]
			del Open[min] # = None
			if myNode['value']==myGoal['value']:
				#print "GOAL",
				#print self.Start,
				#print self.Goal
				#print self.myGrid
				Closed.append(myNode)
				myPath = Closed[len(Closed)-1]
				#print "myPath:",
				#print myPath
				while myPath:
					result.append([myPath['x'], myPath['y'], 0])
					myPath = myPath['Parent']
				AStar = Closed = Open = []
				result.reverse()
				#print "result:",
				#print result
				if result:
					result = result[1:len(result)]
				#print "result:",
				#print result
			else:
				mySuccessors = self.Successors(myNode['x'], myNode['y'])
				#print "--------------"
				#print "mySuccessors",
				for myS in mySuccessors:
					#print myS,
					myPath = self.Node(myNode, myS)
					if not myPath['value'] in AStar:
						if self.Find=="Manhattan":
							myPath['g'] = myNode['g'] + self.Manhattan(myS, myNode)
							myPath['f'] = myPath['g'] + self.Manhattan(myS, myGoal)
						else:
							myPath['g'] = myNode['g'] + self.Diagonal(myS, myNode)
							myPath['f'] = myPath['g'] + self.Diagonal(myS, myGoal)
						Open.append(myPath)
						AStar[myPath['value']] = True
				Closed.append(myNode)
			length=len(Open)
		return result

	def Successors(self, x, y):
		N = y - 1
		S = y + 1
		E = x + 1
		W = x - 1
		myN = N > -1 and self.Grid(x, N)
		myS = S < self.rows and self.Grid(x, S)
		myE = E < self.cols and self.Grid(E, y)
		myW = W > -1 and self.Grid(W, y)
		result = []
		if myN:
			result.append({ 'x': x, 'y': N })
		if myE:
			result.append({ 'x': E, 'y': y })
		if myS:
			result.append({ 'x': x, 'y': S })
		if myW:
			result.append({ 'x': W, 'y': y })
		
		if self.Find=="Diagonal" or self.Find=="Euclidean":
			result = self.DiagonalSuccessors(myN, myS, myE, myW, N, S, E, W, result)
		if self.Find=="DiagonalFree" or self.Find=="EuclideanFree":
			result = self.DiagonalSuccessors2(myN, myS, myE, myW, N, S, E, W, result)
		return result

	def DiagonalSuccessors(self, myN, myS, myE, myW, N, S, E, W, result):
		if myN:
			if (myE and self.Grid(E, N)):
				result.append({ 'x': E, 'y': N })
			if (myW and self.Grid(W, N)):
				result.append({ 'x': W, 'y': N })
		if myS:
			if (myE and self.Grid(E, S)):
				result.append({ 'x': E, 'y': S })
			if (myW and self.Grid(W, S)):
				result.append({ 'x': W, 'y': S })
		return result

	def DiagonalSuccessors2(self, myN, myS, myE, myW, N, S, E, W, result):
		myN = N > -1
		myS = S < self.rows
		myE = E < self.cols
		myW = W > -1
		if myE:
			if (myN and self.Grid(E, N)):
				result.append({ 'x': E, 'y': N })
			if (myS and self.Grid(E, S)):
				result.append({ 'x': E, 'y': S })
		if myW:
			if (myN and self.Grid(W, N)):
				result.append({ 'x': W, 'y': N })
			if (myS and self.Grid(W, S)):
				result.append({ 'x': W, 'y': S })
		return result

	def Diagonal(self, Point, Goal):
		return mymax(abs(Point['x'] - Goal['x']), abs(Point['y'] - Goal['y']))

	def Euclidean(self, Point, Goal):
		return sqrt(pow(Point['x'] - Goal['x'], 2) + pow(Point['y'] - Goal['y'], 2))

	def Manhattan(self, Point, Goal):
		return abs(Point['x'] - Goal['x']) + abs(Point['y'] - Goal['y'])

def mymax(a,b):
	if a>b:
		return a
	return b
