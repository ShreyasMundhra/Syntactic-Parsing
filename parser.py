#!/usr/local/bin/python2.7

import sys
import os
import json
from collections import Counter
from copy import copy

# find words from parse tree
def find_words(tree):
	words = []

	if isinstance(tree[1], basestring):
		words.append(tree[1])
		return words

	child1 = tree[1]
	child2 = tree[2]
	words.extend(find_words(child1))
	words.extend(find_words(child2))
	return words

# count frequencies of words in the parse file
def count(parse_file):
	words = []
	for l in open(parse_file):
		t = json.loads(l)
		words.extend(find_words(t))

	counts = Counter(words)
	return counts

# get indices of words in the parse tree
def get_word_indices(tree):
	indices = []

	if isinstance(tree[1], basestring):
		indices.append([1])
		return indices

	child1 = tree[1]
	child2 = tree[2]

	indices1 = get_word_indices(child1)
	for index_list in indices1:
		index_list.insert(0, 1)
		indices.append(index_list)

	indices2 = get_word_indices(child2)
	for index_list in indices2:
		index_list.insert(0, 2)
		indices.append(index_list)

	return indices

# replace infrequent words with a symbol
def replace_infreq_words(in_file, out_file, thresh=5, rare_symbol="_RARE_"):
	counts = count(in_file)
	freq_words = set()

	json_list = []
	for l in open(in_file):
		t = json.loads(l)
		indices = get_word_indices(t)
		for index_list in indices:
			dup = t
			for i in range(0, len(index_list) - 1):
				index = index_list[i]
				dup = dup[index]
			if counts[dup[index_list[-1]]] < thresh:
				dup[index_list[-1]] = rare_symbol
			else:
				freq_words.add(dup[index_list[-1]])

		json_list.append(json.dumps(t))

	write_to_file(out_file, json_list)
	return json_list, freq_words

# write list of strings to file
def write_to_file(filename, str_list):
	with open(filename, 'w') as f:
		text = '\n'.join(str_list)
		f.write(text)

# read frequencies of rules and non-terminals from counts file
def read_counts(counts_file):
	unary = {}
	binary = {}
	nonterm = {}
	for l in open(counts_file):
		words = l.split()
		if words[1] == "UNARYRULE":
			unary[(words[2], words[3])] = int(words[0])
		elif words[1] == "BINARYRULE":
			binary[(words[2], words[3], words[4])] = int(words[0])
		elif words[1] == "NONTERMINAL":
			nonterm[words[2]] = int(words[0])
		else:
			print("Invalid line: " + l)
	return unary, binary, nonterm

# calculate parameters of all rules
def compute_rule_parameters(counts_file):
	unary, binary, nonterm = read_counts(counts_file)
	q = {"UNARY": {}, "BINARY": {}}
	for rule in unary:
		if rule[0] not in q["UNARY"]:
			q["UNARY"][rule[0]] = {}
		q["UNARY"][rule[0]][rule[1]] = unary[rule]/float(nonterm[rule[0]])
	for rule in binary:
		if rule[0] not in q["BINARY"]:
			q["BINARY"][rule[0]] = {}
		q["BINARY"][rule[0]][(rule[1], rule[2])] = binary[rule]/float(nonterm[rule[0]])
	return q

# CKY parsing algorithm
def CKY(words, q):
	pi = {}
	bp = {}

	is_left_rhs = {}
	is_right_rhs = {}

	nonterms = set()
	for rule_type in q:
		for nonterm in q[rule_type]:
			nonterms.add(nonterm)

	for i in range(len(words)):
		word = words[i]
		pi[(i, i)] = {}
		bp[(i, i)] = {}

		for nonterm in nonterms:
			if i == 0:
				is_left_rhs[nonterm] = {}
				is_right_rhs[nonterm] = {}

			if nonterm in q["UNARY"] and word in q["UNARY"][nonterm]:
				pi[(i, i)][nonterm] = q["UNARY"][nonterm][word]
				is_left_rhs[nonterm][i] = True
				is_right_rhs[nonterm][i] = True
			else:
				pi[(i, i)][nonterm] = 0.0
				is_left_rhs[nonterm][i] = False
				is_right_rhs[nonterm][i] = False

	for l in range(1, len(words)):
		for i in range(0, len(words) - l):
			j = i + l
			pi[(i, j)] = {}
			bp[(i, j)] = {}
			for X in nonterms:
				pi[(i, j)][X] = 0.0
				if X in q["BINARY"]:
					for Y, Z in q["BINARY"][X]:
						if not is_left_rhs[Y][i] or not is_right_rhs[Z][j]:
							continue
						for s in range(i, j):
							if pi[(i, s)][Y] == 0 or pi[(s + 1, j)][Z] == 0:
								continue
							prob = q["BINARY"][X][(Y, Z)] * pi[(i, s)][Y] * pi[(s + 1, j)][Z]
							if prob >= pi[(i, j)][X]:
								pi[(i, j)][X] = prob
								bp[(i, j)][X] = (Y, Z, s)
					if pi[(i, j)][X] > 0:
						is_left_rhs[X][i] = True
						is_right_rhs[X][j] = True
	return pi, bp

# main function for saving and parsing sentences in the test set
def parse(counts_file, sentences_file, prediction_file, freq_words, rare_symbol="_RARE_"):
	q = compute_rule_parameters(counts_file)

	json_list = []
	for l in open(sentences_file):
		words = l.split()
		rare_replaced = copy(words)
		for i in range(len(words)):
			word = words[i]
			if word not in freq_words:
				rare_replaced[i] = rare_symbol
		pi, bp = CKY(rare_replaced, q)

		json_tree = construct_json_tree(pi, bp, words)
		json_list.append(json.dumps(json_tree))

	write_to_file(prediction_file, json_list)
	return json_list

# create json object of parse tree using output from CKY algorithm
def construct_json_tree(pi, bp, words, root=None, start=None, stop=None):
	tree = []

	if root is None and start is None and stop is None:
		n = len(words)
		root = "S"
		if pi[(0, n-1)]["S"] == 0:
			root = sorted(pi[(0, n-1)], key=pi[(0, n-1)].get, reverse=True)[0]
		start, stop = 0, n - 1

	tree.append(root)
	if start == stop:
		tree.append(words[start])
		return tree

	Y, Z, s = bp[(start, stop)][root]

	left_subtree = construct_json_tree(pi, bp, words, Y, start, s)
	right_subtree = construct_json_tree(pi, bp, words, Z, s + 1, stop)
	tree.append(left_subtree)
	tree.append(right_subtree)

	return tree

def usage():
	sys.stderr.write("""Usage: python parser.py [question] [input file] [output file]\n""")

if __name__ == "__main__":
	question = sys.argv[1]
	rare_symbol = "_RARE_"

	if question == "q4":
		in_file = sys.argv[2]
		out_file = sys.argv[3]
		json_list, freq_words = replace_infreq_words(in_file, out_file, 5, rare_symbol=rare_symbol)
		os.system("python count_cfg_freq.py " + out_file + " > cfg.counts")

	elif question in ["q5", "q6"]:
		train_file = sys.argv[2]
		dev_file = sys.argv[3]
		out_file = sys.argv[4]

		freq_words = set()
		for l in open(train_file):
			t = json.loads(l)
			freq_words = freq_words.union(set(find_words(t)))
		freq_words.remove(rare_symbol)

		parse('cfg.counts', dev_file, out_file, freq_words, rare_symbol)