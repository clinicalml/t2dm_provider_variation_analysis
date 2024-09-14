WITH person_visit_occurrences AS (
    SELECT
        visit_concept_id,
        visit_start_date
    FROM
        {cdm_schema}.visit_occurrence
    WHERE
        person_id = {person_id}
    AND 
        DATE(visit_start_date) <= DATE('{end_date}')
)
SELECT 
    p.visit_concept_id || ' - visit type - ' || COALESCE (
        c.concept_name, 'no match'
    ) AS concept_name,
    DATE(p.visit_start_date) AS feature_start_date
FROM
    person_visit_occurrences p
LEFT JOIN 
    {cdm_schema}.concept c
ON
    p.visit_concept_id = c.concept_id