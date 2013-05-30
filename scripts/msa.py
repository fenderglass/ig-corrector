
import subprocess
import fasta_reader as fr

def align_muscle(headers, seqs):
	fasta_dict = {h: seqs[h] for h in headers}

	cmdline = ["muscle", "-diags", "-maxiters", "2", "-quiet"]
	child = subprocess.Popen(cmdline, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
	fr.write_fasta(fasta_dict, child.stdin)
	#fr.write_fasta(fasta_dict, open("dump-muscle.fasta", "w"))
	child.stdin.close()
		#for line in child.stderr:
	#	sys.stderr.write(line)
	out_dict = fr.read_fasta(child.stdout)
	return out_dict


def get_consensus(headers, seqs):
	if len(headers) == 1:
		return seqs[headers[0]]

	align = align_muscle(headers, seqs)

	seq_len = len(align[align.keys()[0]])
	s = ""
	for i in xrange(seq_len):
		freq = {}
		for h in align:
			mult = int(h.split("_")[1])
			freq[align[h][i]] = freq.get(align[h][i], 0) + mult

		n = max(freq, key = freq.get)
		if n != "-":
			s += n
	return s

