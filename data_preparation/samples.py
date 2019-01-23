import os
import logging
import pandas as pd

import path_processing
import data_preparation


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('logs/samples.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_coverage_sample_summary_table(run_id, sample_id):
    path = path_processing.get_coverage_sample_summary_path(run_id, sample_id)
    logger.debug(f'Coverage sample summary path {path}')
    coverage_sample_summary = pd.read_csv(path, delimiter='\t', index_col=False).dropna()
    return coverage_sample_summary.to_html(classes='table table-sm table-hover', index=False)


def get_variations_sample_df(run_id, sample_id, save_pickle=False):
    def read_data(sample_path):
        table, table_lines = False, []
        with open(sample_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('#CHROM') or table:
                    table = True
                    table_lines.append(line.strip().split('\t'))
        return table_lines

    def process_sample_vcf(table_lines):
        df = pd.DataFrame(table_lines)
        df.drop([2, 6], axis=1, inplace=True)
        df.columns = df.iloc[0]
        df.drop(0, inplace=True)
        return df

    def process_row(row):
        new_cols = row.FORMAT.split(':')
        new_cols_value = row[row.keys()[-1]].split(':')
        external_information = pd.Series(new_cols_value, index=new_cols)
        return row.append(external_information)

    important_columns = ['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']

    path = path_processing.get_sample_variations_path(run_id, sample_id)
    logger.debug(f'Sample variations path: {path}')

    sample_folder_path = path_processing.get_sample_path(run_id, sample_id)
    logger.debug(f'Sample path: {sample_folder_path}')

    pickle_path = os.path.join(sample_folder_path, f'{sample_id}.sample_variants.pkl')

    if path_processing.check_existence(pickle_path):
        logger.info(f'Variations sample df loaded from file. {pickle_path}')
        return pd.read_pickle(pickle_path)[important_columns]

    logger.info(f'Started processing vcf file {sample_id} in {run_id}, ')
    lines = read_data(path)
    df = process_sample_vcf(lines)

    s = [process_row(row) for index, row in df.iterrows()]
    data = pd.DataFrame(s).drop('INFO', axis=1)

    df = data[['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']]

    if save_pickle:
        df.to_pickle(os.path.join(sample_folder_path, f'{sample_id}.sample_variants.pkl'))
        logger.info(f'Save processed vcf file to pickle. Run ID: {run_id} Sample ID: {sample_id}.')

    return data[important_columns]


def get_gene_coverage_sample_summary(run_id, sample_id):
    gene_coverage_path = path_processing.get_sample_gene_summary_path(run_id, sample_id)
    logger.debug(f'Sample gene summary path: {gene_coverage_path}')

    coverage_sample_gene_summary = pd.read_csv(gene_coverage_path, delimiter='\t', index_col=False)

    df = data_preparation.prepare_mean_columns_df(coverage_sample_gene_summary)
    df.fillna(-1, inplace=True)

    return df


def prepare_tables_for_sample_page(run_id, sample_id):
    data = {}

    if path_processing.check_existence(path_processing.get_coverage_sample_summary_path(run_id, sample_id)):
        logger.info(f'Preparing coverage sample summary table for {run_id} run {sample_id} sample')
        data['coverage_sample_summary'] = data_preparation.get_coverage_sample_summary_table(run_id, sample_id)
    else:
        logger.info(f'There is no coverage sample summary table for {run_id} run {sample_id} sample')
        data['coverage_sample_summary_exists'] = False

    # gene coverage
    if path_processing.check_existence(path_processing.get_sample_gene_summary_path(run_id, sample_id)):
        logger.info(f'Preparing gene coverage sample summary for {run_id} run {sample_id} sample')
        data['coverage_sample_list'] = data_preparation.get_gene_coverage_sample_summary(run_id,
                                                                                         sample_id).values.tolist()
    else:
        logger.info(f'There is no gene coverage sample summary for {run_id} run {sample_id} sample')
        data['gene_coverage_exists'] = False

    # sample variants
    if path_processing.check_existence(path_processing.get_sample_variations_path(run_id, sample_id)):
        logger.info(f'Preparing variations sample df for {run_id} run {sample_id} sample')
        data['sample_variations'] = data_preparation.get_variations_sample_df(run_id, sample_id, True).values.tolist()
    else:
        logger.info(f'There is no variations sample file for {run_id} run {sample_id} sample')
        data['sample_variants_exists'] = False

    return data


def links_to_external_download_data_and_reports(run_id, sample_id):
    data = {}

    # download files
    data['fastq_path_r1'] = path_processing.get_fastq_r1_download_path(run_id, sample_id).replace(os.sep, '/')
    data['fastq_path_r2'] = path_processing.get_fastq_r2_download_path(run_id, sample_id).replace(os.sep, '/')
    data['bam_path'] = path_processing.get_bam_download_path(run_id, sample_id).replace(os.sep, '/')
    data['vcf_path'] = path_processing.get_vcf_download_path(run_id, sample_id).replace(os.sep, '/')

    # reports
    data['fq1_fastqc'] = path_processing.get_fastq_fq1_download_path(run_id, sample_id).replace(os.sep, '/')
    data['fq2_fastqc'] = path_processing.get_fastq_fq2_download_path(run_id, sample_id).replace(os.sep, '/')
    data['R1_001_fastqc'] = path_processing.get_fastqc_report_path(run_id, sample_id, 1).replace(os.sep, '/')
    data['R2_001_fastqc'] = path_processing.get_fastqc_report_path(run_id, sample_id, 2).replace(os.sep, '/')

    return data
