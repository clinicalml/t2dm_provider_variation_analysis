WITH person_visit_occurrences AS (
    SELECT
        provider_id,
        visit_start_date
    FROM
        {cdm_schema}.visit_occurrence
    WHERE
        person_id = {person_id}
    AND 
        DATE(visit_start_date) <= DATE('{end_date}')
    AND
        provider_id IS NOT NULL
),
person_provider_specialties AS (
    SELECT
        p.provider_id,
        p.visit_start_date,
        s.specialty_concept_id
    FROM
        person_visit_occurrences p
    JOIN
        {cdm_schema}.provider s
    ON p.provider_id = s.provider_id
    WHERE
        s.specialty_concept_id IS NOT NULL
)
SELECT 
    p.specialty_concept_id || ' - specialty - ' || COALESCE (
        c.concept_name, 'no match'
    ) AS concept_name,
    DATE(p.visit_start_date) AS feature_start_date
FROM
    person_provider_specialties p
LEFT JOIN 
    {cdm_schema}.concept c
ON
    p.specialty_concept_id = c.concept_id