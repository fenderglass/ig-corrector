from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def read_fasta(stream):
    records = SeqIO.parse(stream, "fasta")
    seqs = {}
    for rec in records:
        seqs[rec.id] = str(rec.seq)
    return seqs


def read_fastq(stream):
    records = SeqIO.parse(stream, "fastq")
    seqs = {}
    for rec in records:
        seqs[rec.id] = str(rec.seq)
    return seqs


def write_fasta(fasta_dict, stream):
    for h, seq in fasta_dict.iteritems():
        SeqIO.write(SeqRecord(Seq(seq), id=h, description=""), stream, "fasta")


def read_cluster(stream):
    clusters = {}

    fasta_buffer = ""
    clust_header = None
    for line in stream:
        if line.startswith("="):
            if clust_header:
                clusters[clust_header] = read_fasta(iter(fasta_buffer.splitlines()))
            clust_header = line.strip()[1:]
            fasta_buffer = ""
        else:
            fasta_buffer += line
    if clust_header:
        clusters[clust_header] = read_fasta(iter(fasta_buffer.splitlines()))
    return clusters


def write_cluster(clusters, stream):
    for cl in clusters:
        stream.write("=" + cl + "\n")
        write_fasta(clusters[cl], stream)
