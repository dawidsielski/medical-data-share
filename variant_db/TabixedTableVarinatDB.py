from variant_db.VariantDB import VariantDB

from subprocess import Popen, PIPE
import os


class TabixedTableVarinatDB(VariantDB):

    @staticmethod
    def get_genome_filename(genome_type):
        variants_path = os.path.join(os.getcwd(), 'data')
        if genome_type == 'hg38':
            return os.path.join(variants_path, 'hg38', 'tmp_hg38_sorted.tsv.gz')
        return os.path.join(variants_path, 'hg19', 'gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz')

    @staticmethod
    def get_variants(chrom=None, start=None, end=None, genome_type='hg19'):
        """Call tabix and generate an array of strings for each line it returns."""
        genome_filename = TabixedTableVarinatDB.get_genome_filename(genome_type)

        if chrom is None:
            query = ''
        elif start is None:
            query = '{}'.format(chrom)
        elif end is not None:
            query = '{}:{}-{}'.format(chrom, start, end)
        else:
            query = ''

        process = Popen(['tabix', '-f', genome_filename, query], stdout=PIPE)
        for line in process.stdout:
            yield [element.decode() for element in line.strip().split()]
