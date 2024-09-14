WITH person_measurements AS (
    SELECT
        measurement_concept_id,
        value_as_number,
        unit_source_value,
        DATE(measurement_datetime) AS feature_start_date
    FROM
        {cdm_schema}.measurement
    WHERE
        person_id = {person_id}
    AND
        DATE(measurement_datetime) <= DATE('{end_date}')
),
measurement_concept_ids AS (
    SELECT
        DISTINCT measurement_concept_id
    FROM
        person_measurements
),
measurement_concept_names AS (
    SELECT
        m.measurement_concept_id,
        c.concept_name
    FROM
        measurement_concept_ids m
    JOIN
        cdm.concept c
    ON
        m.measurement_concept_id = c.concept_id
)
SELECT
    p.measurement_concept_id || ' - lab - ' || COALESCE(
        c.concept_name, 'no match'
    ) || ' - ' || p.value_as_number || ' ' || p.unit_source_value AS concept_name,
    feature_start_date
FROM
    person_measurements p
LEFT JOIN
    measurement_concept_names c
ON
    p.measurement_concept_id = c.measurement_concept_id