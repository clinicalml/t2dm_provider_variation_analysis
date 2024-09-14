import sys
from os.path import dirname, abspath

import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def filter_frequent_providers():
    '''
    Read in T2DM cohort and filter down to providers with at least 10 patients
    Add prv_id column that numbers providers from 1 to N_prv
    @return: None
    '''
    df = pd.read_csv(config.data_dir + 't2dm_cohort_data.csv')
    prv_counts = df.npi.value_counts().to_dict()
    frequent_npi = set()
    for npi in prv_counts:
        if prv_counts[npi] >= 10:
            frequent_npi.add(npi)
    filtered_df = df.loc[df['npi'].isin(frequent_npi)]
    frequent_npi = list(frequent_npi)
    frequent_npi.sort()
    npi_ids = {frequent_npi[i]: i + 1 for i in range(len(frequent_npi))}
    filtered_df['prv_id'] = [npi_ids[filtered_df['npi'].values[i]] for i in range(len(filtered_df))]
    filtered_df.to_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv',
                       index = False)
    
if __name__ == '__main__':
    
    filter_frequent_providers()