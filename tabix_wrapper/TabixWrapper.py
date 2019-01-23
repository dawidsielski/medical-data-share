from subprocess import Popen, PIPE


def bgzip(filename):
    """Call bgzip to compress a file."""
    Popen(['bgzip', '-f', filename])


def tabix_index(filename, preset="gff", chrom=1, start=4, end=5, skip=0, comment="#"):
    """Call tabix to create an index for a bgzip-compressed file."""
    Popen(['tabix', '-p', preset, '-s', chrom, '-b', start, '-e', end,
        '-S', skip, '-c', comment])


def tabix_query(filename, chrom=None, start=None, end=None):
    """Call tabix and generate an array of strings for each line it returns."""
    if chrom is None:
        query = ''
    elif start is None:
        query = '{}'.format(chrom)
    elif end is not None:
        query = '{}:{}-{}'.format(chrom, start, end)
    else:
        query = ''

    process = Popen(['tabix', '-f', filename, query], stdout=PIPE)
    for line in process.stdout:
        yield [element.decode() for element in line.strip().split()]
