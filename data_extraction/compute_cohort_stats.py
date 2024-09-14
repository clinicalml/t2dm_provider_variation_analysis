import os
import sys
from os.path import dirname, abspath
import argparse

import sqlalchemy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(dirname(dirname(abspath(__file__))))
import config
from utils import session_scope, create_sql_engine

def compute_cohort_stats(database_name,
                         schema_name):
    '''
    Compute statistics about T2DM cohort that was created in database schema
    @param database_name: str, name of database
    @param schema_name: str, schema tables were created in
    @return: None
    '''
    engine = create_sql_engine(omop_version)
    
    with open('sql/compute_cohort_stats.sql', 'r') as f:
        stats_sql = f.read().format(schema_name = schema_name)
    
    queries = stats_sql.split(';')
    if queries[-1].strip() == '':
        queries.pop()
    assert len(queries) % 2 == 0
    
    output = ''
    output_dir = config.output_dir + 'cohort_stats/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with session_scope(engine) as session:
        for query_idx in range(int(len(queries)/2)):
            query_description = queries[2*query_idx].strip()[3:]
            query = queries[2*query_idx+1].strip() + ';'
            if query_description.startswith('number of ') \
                and not query_description.startswith('number of patients per provider'):
                result = session.execute(sqlalchemy.text(query)).fetchone()
                output += query_description + ': ' + str(result['stat']) + '\n'
            else:
                df = pd.read_sql(query, engine)
                # compute summary stats
                output += query_description + ':\n'
                output += 'min: ' + str(df['stat'].min()) + '\n'
                if not query_description.startswith('first treatment date'):
                    output += '25th percentile: ' + str(df['stat'].quantile(q = .25)) + '\n'
                    output += 'median: ' + str(df['stat'].quantile(q = .5)) + '\n'
                    output += 'mean: ' + str(df['stat'].mean()) + '\n'
                    output += '75th percentile: ' + str(df['stat'].quantile(q = .75)) + '\n'
                    output += 'std: ' + str(df['stat'].std()) + '\n'
                output += 'max: ' + str(df['stat'].max()) + '\n'
                
                # plot histogram
                df.rename(columns = {'stat': query_description},
                          inplace = True)
                plt.clf()
                sns.histplot(data = df,
                             x    = query_description)
                plt.savefig(output_dir + query_description.replace(' ', '_') + '_hist.pdf')
                
            session.commit()
    
    with open(output_dir + 'cohort_stats.txt', 'w') as f:
        f.write(output)
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Compute cohort statistics.')
    parser.add_argument('--database_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify name of database containing cohort and covariates.')
    parser.add_argument('--schema_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify schema name to read data from.')
    args = parser.parse_args()
    
    compute_cohort_stats(args.database_name,
                         args.schema_name)