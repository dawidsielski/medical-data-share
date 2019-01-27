from variant_db.VariantDB import VariantDB

from subprocess import Popen, PIPE
import os


class TabixedTableVarinatDB(VariantDB):

    @staticmethod
    def get_variants(chrom=None, start=None, end=None):
        """Call tabix and generate an array of strings for each line it returns."""
        variants_path = os.path.join(os.getcwd(), 'data')
        genome_filename = os.path.join(variants_path, 'gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz')

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
