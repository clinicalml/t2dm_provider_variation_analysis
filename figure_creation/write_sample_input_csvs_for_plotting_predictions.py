import sys
from os.path import dirname, abspath
from itertools import product

import numpy as np
import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def write_sample_csvs():
    '''
    Write sample values for plot to csv
    eGFR value ranges from minimum to maximum in dataset
    No heart failure, F, age 50, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, F, age 70, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, F, age 70, treatment date middle between 2017-09-26 and 2020-10-21
    No heart failure, M, age 50, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, M, age 70, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, M, age 70, treatment date middle between 2017-09-26 and 2020-10-21
    For each category, create 1 csv without npi column and 1 csv with every npi included
    '''
    orig_df    = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    npis_df    = pd.read_csv(config.output_dir + 'npi_glrt_pvalues.csv')
    npis       = npis_df['NPI'].values
    
    egfr_min          = orig_df['egfr'].min()
    egfr_max          = orig_df['egfr'].max()
    egfr_vals_to_plot = np.arange(egfr_min, egfr_max + 1)
    
    category_heart_failures   = [0, 0, 0, 0, 0, 0]
    category_sexes            = [0, 0, 0, 1, 1, 1]
    category_ages             = [50, 70, 70, 50, 70, 70]
    category_trt_date_ranges  = [['2013-02-18', '2015-08-29'], ['2013-02-18', '2015-08-29'], ['2017-09-26', '2020-10-21'],
                                 ['2013-02-18', '2015-08-29'], ['2013-02-18', '2015-08-29'], ['2017-09-26', '2020-10-21']]
    category_trt_dates        = []
    for trt_date_range in category_trt_date_ranges:
        ref_datetime          = pd.to_datetime('2000-01-01')
        range_start_timedelta = pd.to_datetime(trt_date_range[0]) - ref_datetime
        range_end_timedelta   = pd.to_datetime(trt_date_range[1]) - ref_datetime
        range_mid_timedelta   = (range_start_timedelta + range_end_timedelta)/2.
        mid_datetime          = ref_datetime + range_mid_timedelta
        category_trt_dates.append(mid_datetime.strftime('%Y-%m-%d'))

    for category_idx in range(len(category_heart_failures)):
        num_samples   = len(egfr_vals_to_plot)
        hf_val        = category_heart_failures[category_idx]
        sex_val       = category_sexes[category_idx]
        age_val       = category_ages[category_idx]
        trt_date_val  = category_trt_dates[category_idx]
        category_data = {'heart_failure'       : [hf_val       for _ in range(num_samples)],
                         'male'                : [sex_val      for _ in range(num_samples)],
                         'age'                 : [age_val      for _ in range(num_samples)],
                         'first_treatment_date': [trt_date_val for _ in range(num_samples)],
                         'egfr'                : egfr_vals_to_plot}
        category_df   = pd.DataFrame(data    = category_data,
                                     columns = ['heart_failure', 'male', 'age', 'first_treatment_date', 'egfr'])
        category_df.to_csv(config.output_dir + 'category_' + str(category_idx) + '_samples_for_plotting.csv',
                           index = False)
        
        num_npi_samples   = num_samples * len(npis)
        category_npi_data = {'heart_failure'       : [hf_val       for _ in range(num_npi_samples)],
                             'male'                : [sex_val      for _ in range(num_npi_samples)],
                             'age'                 : [age_val      for _ in range(num_npi_samples)],
                             'first_treatment_date': [trt_date_val for _ in range(num_npi_samples)],
                             'egfr'                : np.tile(egfr_vals_to_plot, len(npis)),
                             'npi'                 : np.repeat(npis, num_samples)}
        category_npi_df   = pd.DataFrame(data    = category_npi_data,
                                         columns = ['heart_failure', 'male', 'age', 'first_treatment_date', 'egfr', 'npi'])
        category_npi_df.to_csv(config.output_dir + 'category_' + str(category_idx) + '_samples_with_npis_for_plotting.csv',
                               index = False)

if __name__ == '__main__':
    
    write_sample_csvs()