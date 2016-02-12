#coding:utf-8

import json
import random
import copy
import math
import numpy as np
import threading
import copy
import multiprocessing

class Ga:
	def __init__(self, fname, mutRate=3.0, numGen=1000, numGenes = 20, numParent = 2):	
		f = open(fname)

		# 生のデータ
		self.data = json.load(f)
		f.close()

		# 染色体数 
		self.numElem = len(self.data)

		# 突然変異率
		self.mutRate = mutRate
		
		# 世代制限
		self.numGen = numGen

		# 個体数
		self.numGenes = numGenes

		# 染色体表現
		self.genes = np.random.randint(2, size=(self.numGenes, self.numElem))

		# ランキングの合計
		self.fit_sum = sum(range(1, self.numGenes))
		
		# 交叉時の親の数
		self.numParent = numParent
	
	def __calc_fit(self, umaibou):
		# うまい棒の適合度を計算する
		sum = 0
		sum += umaibou[u'energy']
		sum += umaibou[u'protein']
		sum += umaibou[u'carbon']
		sum += umaibou[u'natrium']
		return sum

	def __calc_comb_fat(self, comb):
		fat = 0
		for i, c in enumerate(comb):
			if c == 1:
				fat+= self.data[i][u'fat']

		return fat

	def __calc_comb_fit(self):
		# 組み合わせの適合度計算
		fitness = np.zeros(self.numGenes)
		for i, comb in enumerate(self.genes):
			fats = 0
			for j, isExs in enumerate(comb):
				if isExs == 1:
					fitness[i] += self.__calc_fit(self.data[j])
					fats+= self.data[j][u'fat']

					# 脂質25以下という制約条件を超えると適合度は0になる
					if fats > 25:
						fitness[i] = 0
						break
		return fitness

	def __ranking(self, fitness):
		# 適合度を昇順に並べ替え
		indice = np.argsort(fitness)
		# 適合度が小さいほうからランク付けしていく1-
		rank = 1
		ranking = np.zeros(len(indice))
		for i in indice:
			ranking[i] = rank
			rank+=1
		return ranking


	def __show_umaibou(self, umaibou):
		print('Name: %s' % umaibou[u'name'])
		print('energy: %f' % umaibou[u'energy'])
		print('protein: %f' % umaibou[u'protein'])
		print('carbon: %f' % umaibou[u'carbon'])
		print('natrium: %f' % umaibou[u'natrium'])
		print('fat: %f' % umaibou[u'fat'])


	def __show_comb(self, genes):
		for i, v in enumerate(genes):
			if v == 1:
				self.__show_umaibou(self.data[i])

	def __choice_parents(self, rank):
		parents = []
		for i in xrange(self.numParent):
			index = random.randint(0, self.fit_sum)
			sumFit = 0
			# ランキングを降順にソートしインデックスを取得
			indice = np.argsort(rank)[-1::-1]
			for i in indice:
				sumFit += rank[i]
				if sumFit > index and not i in parents:
					parents.append(i)
					break

		return parents
	
	def __crossover(self, parents):
		child = np.zeros(self.numElem)
		for i in xrange(self.numElem):
			r = random.randint(0, self.numParent-1)
			child[i] = self.genes[parents[r]][i]

		return child

	def __mutation(self):
		for i, v in enumerate(self.genes):
			r = random.randint(0, 100)
			if r < self.mutRate:
				pos = random.randint(0, self.numElem-1)
				if v[pos] == 0:
					self.genes[i][pos] = 1
				else:
					self.genes[i][pos] = 0

	def ga(self):

		for i in xrange(0, self.numGen):

			#適合度行列を計算
			fitness = self.__calc_comb_fit()
			ranking = self.__ranking(fitness)
			parents = self.__choice_parents(ranking)
			child = self.__crossover(parents)
			indice = np.argsort(fitness)
			self.genes[indice[0]] = child
			self.__mutation()
			#print(fitness)
			#print(fitness[indice[self.numElem-1]])
			
		fitness = self.__calc_comb_fit()
		indice = np.argsort(fitness)[-1::-1]
		return fitness[indice[0]], self


	def show_result(self):
		fitness = self.__calc_comb_fit()
		indice = np.argsort(fitness)[-1::-1]
		print('適合度: %f' % fitness[indice[0]])
		print('脂質: %f' % self.__calc_comb_fat(self.genes[indice[0]]))
		self.__show_comb(self.genes[indice[0]])
	

max_fitness = 0.0
ga = None
lock = threading.Lock()


def conc():
	global max_fitness
	global ga
	global lock
	g = Ga("../data/umaibou.json", numGen=1000, mutRate=5.0)
	fitness, ga_tmp = g.ga()
	lock.acquire()
	try:
		print("finished calcurate")
		if max_fitness < fitness:
			max_fitness = fitness
			ga = copy.copy(ga_tmp)
	finally:
		lock.release()
	
for i in range(multiprocessing.cpu_count()):
	t = threading.Thread(target=conc)
	t.start()

main_thread = threading.currentThread()
for t in threading.enumerate():
	if t is not main_thread:
		t.join()

ga.show_result()
