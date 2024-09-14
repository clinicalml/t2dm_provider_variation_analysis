import argparse
import sqlalchemy

from utils import session_scope, create_sql_engine

def extract_cohort_and_covariates(database_name,
                                  schema_name,
                                  skip_cohort):
    '''
    Create cohort and covariate tables in database schema
    @param database_name: str, name of database
    @param schema_name: str, schema to create tables in
    @param skip_cohort: bool, whether to skip cohort table creation, assumes already exists
    @return: None
    '''
    if not skip_cohort:
        with open('sql/extract_cohort.sql', 'r') as f:
            cohort_sql = f.read().format(schema_name = schema_name)
    with open('sql/extract_covariates.sql', 'r') as f:
        covariate_sql = f.read().format(schema_name   = schema_name)

    engine = create_sql_engine(database_name)
    with session_scope(engine) as session:
        if not skip_cohort:
            session.execute(sqlalchemy.text(cohort_sql))
            session.commit()
        session.execute(sqlalchemy.text(covariate_sql))
        session.commit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Extract type 2 diabetes cohort and covariates.')
    parser.add_argument('--database_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify name of database to extract cohort and covariates in.')
    parser.add_argument('--schema_name',
                        action  = 'store',
                        type    = str,
                        help    = 'Specify schema name to create tables in.')
    parser.add_argument('--skip_cohort',
                        action  = 'store_true',
                        default = False,
                        help    = 'Specify to skip cohort table creation. (Assumes already created.)')
    args = parser.parse_args()
    extract_cohort_and_covariates(args.database_name,
                                  args.schema_name,
                                  args.skip_cohort)