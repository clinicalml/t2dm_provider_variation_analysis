DROP TABLE IF EXISTS {schema_name}.t2dm_cohort_covariates; 
CREATE TABLE {schema_name}.t2dm_cohort_covariates AS
(
    with heart_failure AS (
        SELECT DISTINCT
            co.person_id,
            1 AS occurred
        FROM {schema_name}.t2dm_cohort p
        JOIN cdm.condition_occurrence co
        ON co.person_id = p.person_id
        WHERE
            co.condition_concept_id IN (
                SELECT
                    c.concept_id
                FROM cdm.concept c
                JOIN cdm.concept_ancestor ca
                ON c.concept_id = ca.descendant_concept_id
                WHERE ca.ancestor_concept_id = 316139
            )
        AND p.first_treatment_date >= co.condition_start_datetime
        AND p.first_treatment_date <= co.condition_start_datetime + INTERVAL '730 days'
    ),
    demographics AS (
        SELECT DISTINCT
            p.person_id,
            DATE_PART('year', DATE(tc.first_treatment_date)) - p.year_of_birth AS age,
            CASE WHEN p.gender_concept_id = 8507
                 THEN 1
                 ELSE 0 
            END AS male,
            c.concept_name AS race
        FROM {schema_name}.t2dm_cohort tc
        JOIN cdm.person p
        ON p.person_id = tc.person_id
        JOIN cdm.concept c
        ON p.race_concept_id = c.concept_id
    )
    SELECT
        c.*,
        COALESCE(hd.occurred, 0) AS heart_failure,
        d.age,
        d.male,
        d.race
    FROM {schema_name}.t2dm_cohort c
    LEFT JOIN heart_failure hd
    ON c.person_id = hd.person_id
    JOIN demographics d
    ON c.person_id = d.person_id
);