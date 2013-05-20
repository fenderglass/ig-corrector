#!/usr/bin/env python

import fasta_reader as fr
import sys
from Bio import pairwise2
from itertools import product, combinations

class Sequence:
	def __init__(self, hdr, cdr):
		self.header = hdr
		self.cdr = cdr

class Cluster:
	def __init__(self):
		self.seqs = []

def parse_cdr(filename):
	clusters = []
	cl = None
	header = ""
	for line in open(filename, "r"):
		line = line.strip()
		if line.startswith("Cluster"):
			if cl:
				clusters.append(cl)
			cl = Cluster()
		elif line.startswith(">"):
			header = line[1:]
		elif len(line) > 0:
			cl.seqs.append(Sequence(header, line))
	return clusters

def correct_indels(cdr_map, weight, threshold):
	sorted_r = sorted(weight, key = weight.get, reverse = True)
	for cdr1, cdr2 in combinations(sorted_r, 2):
		if cdr1 not in cdr_map or cdr2 not in cdr_map:
			continue

		align = pairwise2.align.globalms(cdr1, cdr2, 0, -1, -2, -2)[0]
		#print align
		n_miss = 0
		for i in xrange(len(align[0])):
			if align[0][i] != align[1][i] and align[0][i] != "-" and align[1][i] != "-":
				n_miss += 1
		if n_miss != 0:
			continue
		
		if weight[cdr1] / weight[cdr2] >= threshold:
			true_cdr, false_cdr = cdr1, cdr2
		elif len(cdr1) % 3 == 0 and len(cdr2) % 3 != 0:
			true_cdr, false_cdr = cdr1, cdr2
		elif len(cdr2) % 3 == 0 and len(cdr1) % 3 != 0:
			true_cdr, false_cdr = cdr2, cdr1
		else:
			sys.stderr.write("Ambigious cdrs! " + str(align) + "\n")
			true_cdr, false_cdr = cdr1, cdr2
		#print false_cdr, "to", true_cdr, weight[false_cdr], weight[true_cdr], len(cdr_map)

		cdr_map[true_cdr] += cdr_map[false_cdr]
		del cdr_map[false_cdr]
		weight[true_cdr] += weight[false_cdr]
		del weight[false_cdr]

def correct_missmatches(cdr_map, weight, seqs):
	pass


def correct_cdr(cluster, seqs):
	THRESHOLD = 2

	cdr_map = {}
	weight = {}
	for s in cluster.seqs:
		if not s.cdr in cdr_map:
			cdr_map[s.cdr] = []
		cdr_map[s.cdr].append(s.header)
		qty = int(s.header.split("_")[1])
		weight[s.cdr] = weight.get(s.cdr, 0) + qty
	
	if len(cdr_map) == 1:
		return [cluster]
	
	correct_indels(cdr_map, weight, THRESHOLD)
	correct_missmatches(cdr_map, weight, seqs)

	#reconstruct clusters
	clusters = []
	for cdr in cdr_map:
		clust = Cluster()
		for head in cdr_map[cdr]:
			clust.seqs.append(Sequence(head, cdr))
		clusters.append(clust)
	return clusters
	
def out_cluster(cluster, name, seqs):
	sys.stdout.write(name + "\n")
	for seq in cluster.seqs:
		sys.stdout.write(">{0} {1}\n{2}\n".format(seq.header, seq.cdr, seqs[seq.header]))
	sys.stdout.write("\n")

def main():
	if len(sys.argv) < 3:
		print "USAGE: correct_cdr.py cdr_cluster_file reads_file"
		return

	seqs = fr.get_seqs(sys.argv[2])
	clusters = parse_cdr(sys.argv[1])
	counter = 0
	cl_id = 0
	for c in clusters:
		sys.stderr.write(str(counter) + "\n")
		counter += 1
		for cluster in correct_cdr(c, seqs):
			out_cluster(cluster, "Cluster_" + str(cl_id), seqs)
			cl_id += 1
	
	
if __name__ == "__main__":
	main()