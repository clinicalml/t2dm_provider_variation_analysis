CREATE SCHEMA IF NOT EXISTS {t2dm_schema};

DROP TABLE IF EXISTS {t2dm_schema}.{cohort_table_name};
CREATE TABLE {t2dm_schema}.{cohort_table_name} (
    person_id integer NOT NULL,
    end_date date NOT NULL,
    metformin integer NOT NULL,
    npi integer NOT NULL,
    egfr numeric NOT NULL,
    heart_failure integer NOT NULL,
    age integer NOT NULL,
    male integer NOT NULL,
    race varchar(50) NOT NULL
);