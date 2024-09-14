WITH person_procedure_occurrences AS (
    SELECT
        procedure_concept_id,
        procedure_datetime
    FROM
        {cdm_schema}.procedure_occurrence
    WHERE
        person_id = {person_id}
    AND 
        DATE(procedure_datetime) <= DATE('{end_date}')
)
SELECT 
    p.procedure_concept_id || ' - procedure - ' || COALESCE (
        c.concept_name, 'no match'
    ) AS concept_name,
    DATE(p.procedure_datetime) AS feature_start_date
FROM
    person_procedure_occurrences p
LEFT JOIN 
    {cdm_schema}.concept c
ON
    p.procedure_concept_id = c.concept_id