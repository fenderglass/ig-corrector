#!/usr/bin/env python

import fasta_reader as fr
import sys
import subprocess
import logging
from collections import namedtuple, defaultdict

XALIGN_EXEC = "xalign"

AlignInfo = namedtuple("AlignInfo", ["begin", "end", "score"])

def xalign(fasta_dict, query, threshold):
    logging.getLogger(__name__).debug("Calling xalign with querry \"{0}\" and threshold {1}".
                                                                    format(query, threshold))
    cmdline = [XALIGN_EXEC, "-t", str(threshold), "-q", query]
    child = subprocess.Popen(cmdline, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    fr.write_fasta(fasta_dict, child.stdin)
    child.stdin.close()

    out_dict = {}
    for line in child.stdout:
        values = line.strip().split(" ")
        header = values[0]
        assert header.startswith(">")
        out_dict[header[1:]] = []
        for align in values[1:]:
            start, end, score = align[1:-1].split(",")
            out_dict[header[1:]].append(AlignInfo(int(start), int(end), int(score)))
    logging.getLogger(__name__).debug("xalign finished")
    return out_dict


def find_cdr3(in_stream, start_seqs, end_seqs, threshold, out_stream):
    MIN_CDR_LEN = 30
    MAX_CDR_LEN = 90

    logging.getLogger(__name__).info("Finding cdr regions (size from {0} to {1}) started".
                                                        format(MIN_CDR_LEN, MAX_CDR_LEN))
    seqs = fr.read_fasta(in_stream)
    start_align = defaultdict(list)
    end_align = defaultdict(list)
    for qry in start_seqs:
        for h, alns in xalign(seqs, qry, threshold).iteritems():
            start_align[h].extend(alns)
    for qry in end_seqs:
        for h, alns in xalign(seqs, qry, threshold).iteritems():
            end_align[h].extend(alns)

    for h, seq in seqs.iteritems():
        candidates = []
        for start in start_align[h]:
            for end in end_align[h]:
                dist = end.begin - start.begin
                if (MIN_CDR_LEN <= dist and dist <= MAX_CDR_LEN and
                                        start.begin > len(seq) / 2):
                    candidates.append(AlignInfo(start.begin, end.begin - 1, start.score + end.score))

        if len(candidates) == 0:
            logging.getLogger(__name__).debug("{0} : no cdr found".format(h))
            continue

        max_score = 0
        cand = None
        for c in candidates:
            if c.score > max_score:
                cand = c
                max_score = c.score

        cdr = seq[cand.begin : cand.end + 1]
        out_stream.write(">{0}\n{1}\n".format(h, cdr))
        logging.getLogger(__name__).debug("{0} : cdr found with score {1}".
                                                            format(h, max_score))
    logging.getLogger(__name__).info("Finding cdr regions finished")


def main():
    logging.basicConfig(level = logging.DEBUG)
    CDR3_START = "YYC"
    CDR3_END = "WG[QKR]"
    #CDR3_END = "GTK"
    THRESHOLD = 15
    if len(sys.argv) < 2:
        print "USAGE: find_cdr3.py reads_file"
        return

    find_cdr3(open(sys.argv[1], "r"), [CDR3_START], [CDR3_END], THRESHOLD, sys.stdout)

if __name__ == "__main__":
    main()
