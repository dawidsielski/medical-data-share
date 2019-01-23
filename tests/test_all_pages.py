import requests
import urllib
import os
import pytest

import path_processing


BASE_LINK = 'http://127.0.0.1:5000'
DOWNLOAD_PATH = 'http://127.0.0.1:5000/download/'


def slash_join(*args):
    return "/".join(arg.strip("/") for arg in args)


def check_status_code(link):
    request = requests.get(link)
    return request.status_code


def test_run_page():
    path = urllib.parse.urljoin(BASE_LINK, 'runs')
    status_code = check_status_code(path)
    assert status_code == 200


def test_specific_run_page():
    all_runs = path_processing.get_all_runs_names()
    path = urllib.parse.urljoin(BASE_LINK, 'runs', all_runs[0])
    status_code = check_status_code(path)
    assert status_code == 200


def test_samples_page():
    path = urllib.parse.urljoin(BASE_LINK, 'samples')
    status_code = check_status_code(path)
    assert status_code == 200


def test_specific_sample_page():
    all_runs = path_processing.get_all_runs_names()
    samples_for_given_run = path_processing.get_samples_from_run_name(all_runs[0])
    path = slash_join(BASE_LINK, 'runs', all_runs[0], samples_for_given_run[0])
    status_code = check_status_code(path)
    assert status_code == 200


def test_download_buttons():
    all_runs = path_processing.get_all_runs_names()
    run_id = all_runs[0]
    samples_for_given_run = path_processing.get_samples_from_run_name(run_id)
    sample_id = samples_for_given_run[0]

    download_path = path_processing.get_fastq_r1_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_fastq_r2_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_bam_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_vcf_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200


def test_report_buttons():
    all_runs = path_processing.get_all_runs_names()
    run_id = all_runs[0]
    samples_for_given_run = path_processing.get_samples_from_run_name(run_id)
    sample_id = samples_for_given_run[0]

    download_path = path_processing.get_fastq_fq1_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_fastq_fq2_download_path(run_id, sample_id).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_fastqc_report_path(run_id, sample_id, 1).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200

    download_path = path_processing.get_fastqc_report_path(run_id, sample_id, 2).replace(os.sep, '/')
    path = urllib.parse.urljoin(DOWNLOAD_PATH, download_path)
    assert check_status_code(path) == 200
