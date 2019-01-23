import logging
import pandas as pd

import path_processing

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('logs/runs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_summary(run_id):
    columns = ['sample_id', 'total', 'mean', '%_bases_above_5', '%_bases_above_10', '%_bases_above_20']
    new_columns = ['Sample ID', 'Total', 'Mean', 'Above 5%', 'Above 10%', 'Above 20%']

    summary_path = path_processing.get_sample_coverage_path(run_id)
    logger.debug(f'Sample coverage path: {summary_path}')

    sample_summary = pd.read_csv(summary_path, delimiter='\t', index_col=False, usecols=columns)
    sample_summary.rename(columns=dict(zip(columns, new_columns)), inplace=True)

    sample_summary.drop(sample_summary.index[-1], inplace=True)

    return sample_summary[new_columns]


def get_gene_summary(run_id):
    summary_path = path_processing.get_sample_gene_coverage_path(run_id)
    logger.debug(f'Sample gene summary path {summary_path}')

    sample_gene_summary = pd.read_csv(summary_path, delimiter='\t', index_col=False)
    return sample_gene_summary


def extract_data_from_multisample_stats(path):
    lines = []
    with open(path, 'r') as file:
        for line in file.readlines():
            if line.startswith('PSC'):
                lines.append(line.strip().split('\t'))

    return lines


# variants
def get_multisample_stats_df(run_id):
    path = path_processing.get_multisample_vcf_stats_path(run_id)
    logger.debug(f'Multisample vcf stats path {path}')

    if not path_processing.check_existence(path):
        return False, False

    lines = extract_data_from_multisample_stats(path)
    labels = ['PSC', 'id', 'Sample', 'nRefHom', 'nNonRefHom', 'nHets', 'nTransitions', 'nTransversions', 'nIndels',
              'average depth', 'nSingletons', 'nHapRef', 'nHapAlt', 'nMissing']

    df = pd.DataFrame(lines, columns=labels)
    df.drop(columns=['PSC', 'id'], axis=1, inplace=True)
    df['Total'] = df['nNonRefHom'] + df['nHets'] + df['nIndels']

    return df.to_html(classes='table table-sm table-hover', index=False), df


def prepare_sample_summary_html_table(df, run_id):
    with pd.option_context('display.max_colwidth', -1):
        df.loc[:, 'Sample ID'] = df['Sample ID'].apply(
            lambda x: '<a href=\"/runs/{run_id}/{sample_id}">{sample_id}</a>'.format(sample_id=x, run_id=run_id))
        return df.to_html(classes='table table-sm table-hover', escape=False, index=False)
