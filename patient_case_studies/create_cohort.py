import os
import sys
import argparse
from os.path import dirname, abspath

import pandas as pd
import sqlalchemy

sys.path.append(dirname(dirname(abspath(__file__))))
import config
from utils import session_scope, create_sql_engine

def create_case_study_csv():
    '''
    Create csv containing cohort table entries for case study patients
    @return: None
    '''
    output_subdir = config.output_dir + 'case_studies/'
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    sample_df     = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    columns       = ['person_id', 'first_treatment_date', 'metformin', 'npi', 'egfr', 'heart_failure', 'age', 'male', 'race']
    case_study_patients_df = sample_df.loc[sample_df['npi'].isin(set(config.outlying_npis))][columns]
    case_study_file_name   = output_subdir + 'case_study_patients.csv'
    case_study_patients_df.rename(columns = {'first_treatment_date': 'end_date'},
                                  inplace = True)
    case_study_patients_df.to_csv(case_study_file_name,
                                  index = False)
    
def create_empty_cohort_table(database_name,
                              t2dm_schema):
    '''
    Create empty cohort table in database
    @param database_name: str, name of database
    @param t2dm_schema: str, name of schema to create table in
    @return: None
    '''
    with open('sql/create_cohort_table.sql', 'r') as f:
        cohort_sql = f.read().format(t2dm_schema       = t2dm_schema,
                                     cohort_table_name = 'small_pval_provider_patients')
    engine = create_sql_engine(database_name)
    with session_scope(engine) as session:
        session.execute(sqlalchemy.text(cohort_sql))
        session.commit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Create case study csv and empty case study cohort tables.')
    parser.add_argument('--database_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify name of database to create case study cohort in.')
    parser.add_argument('--schema_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify schema name to create tables in.')
    args = parser.parse_args()

    create_case_study_csv()
    create_empty_cohort_table(args.database_name,
                              args.schema_name)