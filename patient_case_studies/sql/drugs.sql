WITH person_drug_exposures AS (
    SELECT
        drug_concept_id,
        drug_exposure_start_datetime 
    FROM
        {cdm_schema}.drug_exposure
    WHERE
        person_id = {person_id}
    AND 
        DATE(drug_exposure_start_datetime) <= DATE('{end_date}')
)
SELECT 
    p.drug_concept_id || ' - drug - ' || COALESCE (
        c.concept_name, 'no match'
    ) AS concept_name,
    DATE(p.drug_exposure_start_datetime) AS feature_start_date
FROM
    person_drug_exposures p
LEFT JOIN 
    {cdm_schema}.concept c
ON
    p.drug_concept_id = c.concept_id