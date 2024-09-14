import sys
from os.path import dirname, abspath
from itertools import product

import numpy as np
import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def examine_outlying_providers():
    '''
    Examine patients from outlying providers
    '''
    sample_df = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    columns   = ['person_id', 'first_treatment_date', 'metformin', 'npi', 'egfr', 'heart_failure', 'age', 'male', 'race']
    for npi in config.outlying_providers:
        print(sample_df.loc[sample_df['npi'] == npi][columns])
    
    sex_categories = [0, 1]
    age_categories = [[35, 44], [45, 54], [55, 64], [65, 74], [75, 84]]
    trt_date_categories = [['2000-01-01', '2013-03-07'], ['2013-07-07', '2015-11-18'],
                           ['2016-03-18', '2017-10-23'], ['2018-02-23', '2020-11-08'],
                           ['2021-03-08', '2024-01-01']]
    sex_labels = ['F', 'M']
    
    print('# patients prescribed metformin, prescribed other, '
          + ', '.join(['NPI ' + str(npi) + ' prescribed metformin, NPI ' + str(npi) + ' prescribed other'
                       for npi in config.outlying_providers]))
    for sex, age_range, trt_date_range in product(sex_categories, age_categories, trt_date_categories):
        category_df = sample_df.loc[np.logical_and.reduce((sample_df['heart_failure'] == 0,
                                                           sample_df['male'] == sex,
                                                           sample_df['age'] >= age_range[0],
                                                           sample_df['age'] <= age_range[1],
                                                           sample_df['first_treatment_date'] >= trt_date_range[0],
                                                           sample_df['first_treatment_date'] <= trt_date_range[1]))]
        category_num_metformin = category_df['metformin'].sum()
        category_num_other     = len(category_df) - category_num_metformin
        
        category_counts = [category_num_metformin, category_num_other]
        for npi in config.outlying_providers:
            category_npi_df            = category_df.loc[category_df['npi'] == npi]
            category_npi_num_metformin = category_npi_df['metformin'].sum()
            category_npi_num_other     = len(category_npi_df) - category_npi_num_metformin
            category_counts.extend([category_npi_num_metformin, category_npi_num_other])
        
        if np.sum(category_counts[3:]) > 1:
            print('No heart failure, ' + sex_labels[sex] + ', age between ' + str(age_range[0]) + ' and ' + str(age_range[1])
                  + ', treatment date between ' + trt_date_range[0] + ' and ' + trt_date_range[1] + ': '
                  + ', '.join(map(str, category_counts)))

if __name__ == '__main__':
    
    examine_outlying_providers()