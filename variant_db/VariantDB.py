from abc import ABC, abstractmethod


class VariantDB(ABC):

    @staticmethod
    @abstractmethod
    def get_variants(chrom=None, start=None, end=None):
        pass
