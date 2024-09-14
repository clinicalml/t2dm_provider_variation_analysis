-- number of patients prescribed a diabetes drug;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_with_missing_data;

-- number of patients prescribed a diabetes drug w/ eGFR lab taken;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_with_missing_data
WHERE egfr_lab_measured = 1;

-- number of patients prescribed a diabetes drug w/ eGFR value recorded;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_with_missing_data
WHERE egfr IS NOT NULL;

-- number of patients w/ multiple treatment types on first date and no eGFR value;
WITH n_treatment_types AS (
    SELECT person_id,
           COUNT(DISTINCT metformin) AS treatment_types
    FROM {schema_name}.t2dm_cohort_with_missing_data
    WHERE egfr IS NOT NULL
    GROUP BY person_id
)
SELECT COUNT(DISTINCT person_id) AS stat
FROM n_treatment_types
WHERE treatment_types > 1;

-- number of patients w/ one treatment type on first date and eGFR value;
WITH n_treatment_types AS (
    SELECT person_id,
           COUNT(DISTINCT metformin) AS treatment_types
    FROM {schema_name}.t2dm_cohort_with_missing_data
    WHERE egfr IS NOT NULL
    GROUP BY person_id
)
SELECT COUNT(DISTINCT person_id) AS stat
FROM n_treatment_types
WHERE treatment_types = 1;

-- number of patients w/ one treatment type on first date, eGFR value, and at least 1 provider;
WITH n_treatment_types AS (
    SELECT person_id,
           COUNT(DISTINCT metformin) AS treatment_types
    FROM {schema_name}.t2dm_cohort_with_missing_data
    GROUP BY person_id
),
n_providers AS (
    SELECT person_id,
           COUNT(DISTINCT npi) AS num_providers
    FROM {schema_name}.t2dm_cohort_with_missing_data
    WHERE npi IS NOT NULL
    GROUP BY person_id
)
SELECT COUNT(DISTINCT c.person_id) AS stat
FROM {schema_name}.t2dm_cohort_with_missing_data c
JOIN n_treatment_types t
ON c.person_id = t.person_id
JOIN n_providers p
ON c.person_id = p.person_id
WHERE t.treatment_types = 1
AND p.num_providers >= 1
AND c.egfr IS NOT NULL;

-- number of patients after applying all exclusion criteria: one treatment type on first date, has eGFR value, and 1 provider;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates;

-- number of patients w/ only metformin on first date;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1;

-- number of patients w/ only non-metformin on first date;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0;

-- number of patients w/ heart failure (HF) + metformin (M);
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND heart_failure = 1;

-- number of patients w/ HF + non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND heart_failure = 1;

-- number of patients w/ no HF + M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND heart_failure = 0;

-- number of patients w/ no HF + non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND heart_failure = 0;

-- number of patients male + M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND male = 1;

-- number of patients male + non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND male = 1;

-- number of patients female + M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND male = 0;

-- number of patients female + non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND male = 0;

-- number of patients eGFR < 30 w/ M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND egfr < 30;

-- number of patients eGFR < 30 w/ non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND egfr < 30;

-- number of patients eGFR 30-44 w/ M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND egfr >= 30
AND egfr < 45;

-- number of patients eGFR 30-44 w/ non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND egfr >= 30
AND egfr < 45;

-- number of patients eGFR 45-59 w/ M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND egfr >= 45
AND egfr < 60;

-- number of patients eGFR 45-59 w/ non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND egfr >= 45
AND egfr < 60;

-- number of patients eGFR 60-89 w/ M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND egfr >= 60
AND egfr < 90;

-- number of patients eGFR 60-89 w/ non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND egfr >= 60
AND egfr < 90;

-- number of patients eGFR >= 90 w/ M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 1
AND egfr >= 90;

-- number of patients eGFR >= 90 w/ non-M;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_covariates
WHERE metformin = 0
AND egfr >= 90;

-- number of providers;
SELECT COUNT(DISTINCT npi) AS stat
FROM {schema_name}.t2dm_cohort_covariates;

-- number of providers w/ at least 10 patients;
WITH num_patients_per_provider AS (
    SELECT npi,
           COUNT(DISTINCT person_id) AS num_patients
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY npi
)
SELECT COUNT(DISTINCT npi) AS stat
FROM num_patients_per_provider
WHERE num_patients >= 10;

-- eGFR value;
SELECT egfr AS stat
FROM {schema_name}.t2dm_cohort_covariates;

-- age;
SELECT age AS stat
FROM {schema_name}.t2dm_cohort_covariates;

-- first treatment date;
SELECT first_treatment_date AS stat
FROM {schema_name}.t2dm_cohort_covariates;

-- number of patients per provider;
WITH num_patients_per_provider AS (
    SELECT npi,
           COUNT(DISTINCT person_id) AS stat
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY npi
)
SELECT stat
FROM num_patients_per_provider;

-- number of patients per provider with at least 10 patients;
WITH num_patients_per_provider AS (
    SELECT npi,
           COUNT(DISTINCT person_id) AS stat
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY npi
)
SELECT stat
FROM num_patients_per_provider
WHERE stat >= 10;

-- metformin prescription rate per provider;
WITH num_patients_per_provider AS (
    SELECT npi,
           COUNT(DISTINCT person_id) AS num_patients,
           SUM(metformin) AS num_metformin_prescriptions
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY npi
)
SELECT CAST(num_metformin_prescriptions AS DECIMAL) / num_patients AS stat
FROM num_patients_per_provider;

-- metformin prescription rate per provider with at least 10 patients;
WITH num_patients_per_provider AS (
    SELECT npi,
           COUNT(DISTINCT person_id) AS num_patients,
           SUM(metformin) AS num_metformin_prescriptions
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY npi
)
SELECT CAST(num_metformin_prescriptions AS DECIMAL) / num_patients AS stat
FROM num_patients_per_provider
WHERE num_patients >= 10;

-- number of patients prescribed a diabetes drug w/ prescribing provider recorded;
SELECT COUNT(DISTINCT person_id) AS stat
FROM {schema_name}.t2dm_cohort_with_missing_data
WHERE npi IS NOT NULL;

-- number of patients w/ multiple prescribing providers;
WITH n_providers_per_patient AS (
    SELECT person_id,
           COUNT(DISTINCT npi) AS n_providers
    FROM {schema_name}.t2dm_cohort_covariates
    GROUP BY person_id
)
SELECT COUNT(DISTINCT person_id) AS stat
FROM n_providers_per_patient
WHERE n_providers > 1;

-- number of patients w/ multiple treatment types on first date;
WITH n_treatment_types AS (
    SELECT person_id,
           COUNT(DISTINCT metformin) AS treatment_types
    FROM {schema_name}.t2dm_cohort_with_missing_data
    WHERE egfr IS NOT NULL
    AND npi IS NOT NULL
    GROUP BY person_id
)
SELECT COUNT(DISTINCT person_id) AS stat
FROM n_treatment_types
WHERE treatment_types > 1;