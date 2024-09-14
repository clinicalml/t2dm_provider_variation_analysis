import os
import sys
import argparse
from copy import deepcopy
from os.path import dirname, abspath
from pathlib import Path

import json
import pandas as pd

from omop_learn.data.cohort import Cohort
from omop_learn.data.feature import Feature
from omop_learn.utils.config import Config
from omop_learn.omop import OMOPDataset
from omop_learn.backends.postgres import PostgresBackend

sys.path.append(dirname(dirname(abspath(__file__))))
import config_private as config

def extract_omop_dataset(database_name,
                         t2dm_schema):
    '''
    Extract omop dataset to create data.json file
    @param database_name: str, name of database
    @param t2dm_schema: str, name of schema containing cohort table for case studies
    @return: None
    '''
    cohort_table_name = 'small_pval_provider_patients'
    omop_dir          = config.output_dir + 'omop_datasets'
    
    # set up database connection
    config_params = {"cdm_schema"   : "cdm",
                     "prefix_schema": t2dm_schema,
                     "datasets_dir" : omop_dir,
                     "path"         : "postgresql://localhost/" + str(database_name)}
    omop_config   = Config(config_params)
    connect_args  = {"host": '/var/run/postgresql/'}
    omop_backend  = PostgresBackend(omop_config, connect_args)

    # extract cohort
    cohort_params = {"cohort_table_name": cohort_table_name,
                     "schema_name"      : t2dm_schema}
    sql_dir = "sql/"
    omop_cohort   = Cohort.from_prebuilt(omop_backend, params = cohort_params)
    print("omop_v" + str(omop_version) + " cohort has " + str(len(omop_cohort)) + " patients")
    
    # extract features
    feature_paths = [sql_dir + "drugs.sql", 
                     sql_dir + "conditions.sql",
                     sql_dir + "procedures.sql",
                     sql_dir + "visit_types.sql",
                     sql_dir + "visit_specialties.sql",
                     sql_dir + "labs.sql"]
    feature_names = ["drugs", "conditions", "procedures", "visit_types", "visit_specialties", "labs"]
    features = [Feature(n, p) for n, p in zip(feature_names, feature_paths)]
    omop_dataset_args = {
        "name"       : "t2dm_provider_variation_case_studies_" + database_name,
        "config"     : omop_config,
        "cohort"     : omop_cohort,
        "features"   : features,
        "backend"    : omop_backend,
        "data_dir"   : Path(config_params['datasets_dir']),
        "num_workers": 1
    }
    omop_dataset = OMOPDataset(**omop_dataset_args)
    
def write_features_to_file(database_name,
                           schema_name):
    '''
    Extract all conditions, drugs, procedures, visit types, visit specialties, labs ordered + results
    up to first-line T2DM treatment date for each patient
    @param database_name: str, name of database
    @param schema_name: str, name of schema in databases that contains cohort table for case studies
    @return: None
    '''
    output_subdir     = config.output_dir + 'case_studies/'
    omop_dir          = config.output_dir + 'omop_datasets/'
    sample_df         = pd.read_csv(output_subdir + 'case_study_patients.csv')

    data_json = omop_dir + 't2dm_provider_variation_case_studies_' + database_name + '/data.json'
    
    if not os.path.exists(data_json):
        extract_omop_dataset(database_name,
                             schema_name)

    patient_dates_to_visits = dict() # patients -> {date: visit}
    with open(data_json, 'r') as json_fh:
        for line in json_fh:
            patient_data = json.loads(line)
            person_id    = patient_data['person_id']
            visits       = patient_data['visits']
            dates        = patient_data['dates']
            patient_dates_to_visits[person_id] = {dates[i]: visits[i] for i in range(len(visits))}

    for person_id in patient_dates_to_visits:
        person_dates  = sorted(patient_dates_to_visits[person_id])[::-1]
        patient_df    = sample_df.loc[sample_df['person_id'] == person_id]
        treatment_date_str = str(patient_df['end_date'].values[0])
        if patient_df['metformin'].values[0] == 1:
            treatment = 'Metformin'
        else:
            treatment = 'DPP-4i / Sulfonylurea'
        npi  = str(patient_df['npi'].values[0])
        egfr = str(patient_df['egfr'].values[0])
        age  = str(patient_df['age'].values[0])
        race = str(patient_df['race'].values[0])
        if patient_df['heart_failure'].values[0] == 1:
            heart_failure_str = 'Heart failure: Yes'
        else:
            heart_failure_str = 'Heart failure: No'
        if patient_df['male'].values[0] == 1:
            sex_str = 'Male'
        else:
            sex_str = 'Female'
        person_output = 'Person ID: ' + str(person_id) + '\nTreatment date: ' + treatment_date_str \
                      + '\nTreatment: ' + treatment + '\nProvider: ' + npi + '\neGFR: ' + egfr + '\n' \
                      + heart_failure_str + '\nAge: ' + age + '\n' + sex_str + '\nRace: ' + race + '\n'
        for date in person_dates:
            person_output += date + '\n'
            for concept in set(patient_dates_to_visits[person_id][date]):
                if concept is not None:
                    person_output += concept + '\n'
        if databases != 'both':
            output_file = output_subdir + str(person_id) + '_' + databases + '_concepts.txt'
        else:
            output_file = output_subdir + str(person_id) + '_concepts.txt'
        with open(output_file, 'w') as f:
            f.write(person_output)
            
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Extract features from all prior visits for each patient.')
    parser.add_argument('--database_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify name of database to extract patient data from.')
    parser.add_argument('--schema_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify schema name that contains cohort table for case studies.')
    args = parser.parse_args()
    
    write_features_to_file(args.database_name,
                           args.schema_name)