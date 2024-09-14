WITH person_condition_occurrences AS (
    SELECT
        condition_concept_id,
        condition_start_datetime
    FROM
        {cdm_schema}.condition_occurrence
    WHERE
        person_id = {person_id}
    AND 
        DATE(condition_start_datetime) <= DATE('{end_date}')
)
SELECT 
    p.condition_concept_id || ' - condition - ' || COALESCE (
        c.concept_name, 'no match'
    ) AS concept_name,
    DATE(p.condition_start_datetime) AS feature_start_date
FROM
    person_condition_occurrences p
LEFT JOIN 
    {cdm_schema}.concept c
ON
    p.condition_concept_id = c.concept_id