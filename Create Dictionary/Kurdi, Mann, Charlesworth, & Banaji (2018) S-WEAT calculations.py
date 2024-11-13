import json
import random
import numpy as np
from scipy import spatial
from itertools import combinations
import pandas as pd
import csv

vectors = {}
with open("Create Dictionary/Kurdi, Mann, Charlesworth, & Banaji (2018) Vectors.csv", "r") as f:
	i = 0
	for database, category, word, vector in csv.reader(f):
		if i > 0:
			if database not in vectors.keys():
				vectors[database] = {}
			if category not in vectors[database].keys():
				vectors[database][category] = {}
			vectors[database][category][word] = json.loads(vector)
		i += 1

def s_weat(X, A, B, database = "glove", permt = 0, perm_n = 10000):

	def diff_sim(X, A, B, effect=1):

		sum_A = 0
		sum_B = 0

		all_sims = []
		for a in A:
			a_ = a.reshape(1, -1)
			results = spatial.distance.cdist(a_, X, 'cosine')
			sum_X = (1 - results).sum()
			val = sum_X/len(X)
			sum_A += val
			all_sims.append(val)
		ave_A = sum_A/len(A)

		for b in B:
			b_ = b.reshape(1, -1)
			results = spatial.distance.cdist(b_, X, 'cosine')
			sum_X = (1 - results).sum()
			val = sum_X/len(X)
			sum_B += val
			all_sims.append(val)
		ave_B = sum_B/len(B)

		difference = ave_A - ave_B

		if effect == 1:
			standard_dev = np.std(all_sims, ddof=1)
			effect_size = difference/standard_dev

			return difference, standard_dev, effect_size

		else:
			return difference

	def permutation_test(X, A, B):
		jointlist = np.array(list(A) + list(B))
		permutations = []
		nums = list(range(len(jointlist)))
		for comb in combinations(nums, len(A)):
			set1 = [item for i, item in enumerate(jointlist) if i in comb]
			set2 = [item for i, item in enumerate(jointlist) if i not in comb]
			permutations.append(diff_sim(X, set1, set2, effect=0))
		return permutations

	def rand_test(X, A, B, perm_n):
		jointlist = np.array(list(A) + list(B))
		np.random.shuffle(jointlist)
		permutations = []
		count = 0
		midpoint = len(A)
		while count < perm_n:
			np.random.shuffle(jointlist)
			set1 = jointlist[:midpoint]
			set2 = jointlist[midpoint:]
			permutations.append(diff_sim(X, set1, set2, effect=0))
			count += 1
		return permutations

	Cat1 = np.array([vector for vector in vectors[database][X].values()])
	Att1 = np.array([vector for vector in vectors[database][A].values()])
	Att2 = np.array([vector for vector in vectors[database][B].values()])

	difference, standard_dev, effect_size = diff_sim(Cat1, Att1, Att2)

	if permt == 1 or permt == 2:
		if permt == 1:
			permutations = np.array(permutation_test(Cat1, Att1, Att2))
		elif permt == 2:
			permutations = np.array(rand_test(Cat1, Att1, Att2, perm_n = perm_n))
		perm_mean = np.mean(permutations)
		permutations = permutations - perm_mean
		sum_c = difference - perm_mean
		Pleft = (sum(i <= sum_c for i in permutations)+1)/(len(permutations)+1)
		Pright = (sum(i >= sum_c for i in permutations)+1)/(len(permutations)+1)
		Ptwo = (sum(abs(i) >= abs(sum_c) for i in permutations)+1)/(len(permutations)+1)

	if permt == 1 or permt == 2:
		return difference, standard_dev, effect_size, Pleft, Pright, Ptwo
	else:
		return difference, standard_dev, effect_size


tests = [
	("Warm", "Cold"),
	("Competence", "Incompetence"),
	("higharousal_samevalence", "lowarousal_samevalence"),
	("highvalence_samearousal", "lowvalence_samearousal"),
	("highvalence", "lowvalence"),
]

results = []

for databasename, database in vectors.items():
	for att1, att2 in tests:
		for group in database.keys():
			if group not in [term for pair in tests for term in pair]:
				difference, standard_dev, effect_size = s_weat(group, att1, att2, databasename, permt=0)
				results.append((databasename, group, att1 + "/" + att2, difference, standard_dev, effect_size))
				# For p-values, change permt from 0 to 1 for an exhaustive 
				# permutation test, or 2 for randomization test with perm_n iterations, e.g.:
				## difference, standard_dev, effect_size, pleft, pright, ptwo = s_weat(group, att1, att2, databasename, permt=2, perm_n=1000)
				## results.append((databasename, group, att1 + "/" + att2, difference, standard_dev, effect_size, pleft, pright, ptwo))
			

labels = ["database", "group", "test", "difference", "std", "eff_size"]
# if significance testing:
## labels = ["database", "group", "test", "difference", "std", "eff_size", "p_left", "p_right", "p_twotailed"]
df = pd.DataFrame.from_records(results, columns = labels)
df.to_csv("Kurdi, Mann, Charlesworth, & Banaji (2018) Study 3.csv", index = False)
