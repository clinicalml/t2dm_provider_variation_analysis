SELECT
    person_id,
    first_treatment_date AS end_date
FROM {schema_name}.{cohort_table_name}