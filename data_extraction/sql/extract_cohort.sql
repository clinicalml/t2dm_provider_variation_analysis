DROP TABLE IF EXISTS {schema_name}.t2dm_cohort_with_missing_data;
CREATE TABLE {schema_name}.t2dm_cohort_with_missing_data AS (
    WITH diabetes_ingredient_concepts AS ( 
        SELECT DISTINCT 
            concept_id AS ingredient_concept_id, 
            LOWER(concept_name) AS drug_class_name 
        FROM cdm.concept 
        WHERE LOWER(concept_name) IN 
            ('metformin','sitagliptin','vildagliptin','saxagliptin',
             'linagliptin','gemigliptin','anagliptin','teneligliptin',
             'acetohexamide','carbutamide','chlorpropamide','glycyclamide',
             'tolcyclamide','metahexamide','tolazamide','tolbutamide',
             'glibenclamide','glyburide','glibornuride','gliclazide',
             'glipizide','gliquidone','glisoxepide','glyclopyramide','glimepiride')
    ),
    diabetes_drug_concepts AS (
        SELECT 
            ds.drug_concept_id, 
            dic.drug_class_name 
        FROM diabetes_ingredient_concepts dic 
        JOIN cdm.drug_strength ds 
        ON dic.ingredient_concept_id = ds.ingredient_concept_id 
        JOIN cdm.concept_ancestor ca 
        ON ca.descendant_concept_id = ds.drug_concept_id 
        WHERE ca.ancestor_concept_id = 21600712 
    ), 
    diabetes_treatment_occurrences AS ( 
        SELECT DISTINCT de.person_id, 
               ddc.drug_class_name, 
               de.drug_exposure_start_date,
               de.provider_id 
        FROM diabetes_drug_concepts ddc 
        JOIN cdm.drug_exposure de 
        ON de.drug_concept_id = ddc.drug_concept_id 
        WHERE de.person_id != -1 
    ),
    diabetes_first_treatment_date AS ( 
        SELECT person_id, 
               MIN(drug_exposure_start_date) AS first_treatment_date 
        FROM diabetes_treatment_occurrences 
        GROUP BY person_id 
    ), 
    egfr_concepts AS (
        SELECT concept_id
        FROM cdm.concept
        WHERE concept_name LIKE 'Glomerular filtration rate/1.73 sq M%'
    ),
    all_egfr_measurements AS (
        SELECT m.person_id,
               m.measurement_date,
               m.value_as_number
        FROM egfr_concepts c
        JOIN cdm.measurement m
        ON c.concept_id = m.measurement_concept_id
    ),
    prior_egfr_measurements AS ( 
        SELECT 
            m.person_id, 
            m.measurement_date, 
            CASE WHEN MAX(m.value_as_number) = 0
                 THEN NULL
                 ELSE MAX(m.value_as_number)
            END AS egfr,
            1 AS egfr_lab_measured
        FROM diabetes_first_treatment_date dc 
        JOIN all_egfr_measurements m
        ON 
            dc.person_id = m.person_id AND 
            m.measurement_date <= dc.first_treatment_date AND 
            m.measurement_date >= dc.first_treatment_date - INTERVAL '6 months' 
        GROUP BY m.person_id, m.measurement_date 
    ), 
    most_recent_measurement_date AS ( 
        SELECT person_id, 
               MAX(measurement_date) AS measurement_date 
        FROM prior_egfr_measurements 
        GROUP BY person_id 
    ), 
    diabetes_conditions AS ( 
        SELECT concept_id 
        FROM cdm.concept 
        WHERE LOWER(concept_name) LIKE '%diabet%' 
    ), 
    t1dm_conditions AS ( 
        SELECT concept_id 
        FROM cdm.concept 
        WHERE (
            LOWER(concept_name) LIKE '%type 1 diabet%' OR 
            LOWER(concept_name) LIKE '%type i diabet%' OR 
            LOWER(concept_name) LIKE '%diabet%type 1%' OR 
            LOWER(concept_name) LIKE '%diabet%type i %' ) AND 
            LOWER(concept_name) NOT LIKE '%type 2 diabet%' AND 
            LOWER(concept_name) NOT LIKE '%type ii diabet%' AND 
            LOWER(concept_name) NOT LIKE '%diabet%type 2%' AND 
            LOWER(concept_name) NOT LIKE '%diabet%type ii%' 
    ),
    gestational_diabetes_conditions AS ( 
        SELECT concept_id 
        FROM cdm.concept 
        WHERE 
            LOWER(concept_name) LIKE '%gestat%' OR 
            LOWER(concept_name) LIKE '%pregnan%' OR 
            LOWER(concept_name) LIKE '%diabetes of the young%' OR 
            LOWER(concept_name) LIKE '%neonatal%diabet%' OR 
            LOWER(concept_name) LIKE '%diabet%neonatal%' 
    ), 
    cohort_with_diabetes AS ( 
        SELECT DISTINCT td.person_id 
        FROM diabetes_first_treatment_date td 
        JOIN cdm.condition_occurrence co 
        ON 
            td.person_id = co.person_id AND 
            co.condition_start_date <= td.first_treatment_date AND 
            co.condition_start_date >= td.first_treatment_date - INTERVAL '1 year' 
        WHERE co.condition_concept_id IN ( 
            SELECT dc.concept_id FROM diabetes_conditions dc 
        ) 
    ), cohort_with_t1dm_gestational AS ( 
        SELECT DISTINCT td.person_id 
        FROM diabetes_first_treatment_date td 
        JOIN cdm.condition_occurrence co 
        ON 
            td.person_id = co.person_id AND 
            co.condition_start_date <= td.first_treatment_date AND 
            co.condition_start_date >= td.first_treatment_date - INTERVAL '1 year'
        WHERE co.condition_concept_id IN ( 
            SELECT t1c.concept_id FROM t1dm_conditions t1c 
        ) OR co.condition_concept_id IN ( 
            SELECT gdc.concept_id FROM gestational_diabetes_conditions gdc 
        ) 
    ), cohort_inclusion_exclusion AS ( 
        SELECT ci.person_id 
        FROM cohort_with_diabetes ci 
        WHERE NOT EXISTS ( 
            SELECT 
            FROM cohort_with_t1dm_gestational ce 
            WHERE ci.person_id = ce.person_id 
        ) 
    ), 
    cohort_obs_length AS (
        SELECT 
            dc.person_id, 
            td.first_treatment_date, 
            SUM(GREATEST(EXTRACT(EPOCH 
                                 FROM (LEAST(o.observation_period_end_date, 
                                             td.first_treatment_date) 
                                       - GREATEST(o.observation_period_start_date, 
                                                  td.first_treatment_date - INTERVAL '3 years')))
                         /(24*60*60),
                         0)) 
            AS num_days 
        FROM cohort_inclusion_exclusion dc 
        JOIN diabetes_first_treatment_date td 
        ON dc.person_id = td.person_id 
        JOIN cdm.observation_period o 
        ON dc.person_id = o.person_id AND o.observation_period_start_date <= td.first_treatment_date 
        GROUP BY dc.person_id, td.first_treatment_date 
    ),
    observed_cohort AS (
        SELECT *
        FROM cohort_obs_length
        WHERE num_days > 0.95 * EXTRACT(EPOCH FROM (INTERVAL '3 years'))/(24*60*60)
    ),
    provider AS (
        SELECT DISTINCT
            pr.provider_id,
            pr.npi
        FROM diabetes_treatment_occurrences dt
        JOIN cdm.provider pr
        ON pr.provider_id = dt.provider_id
    )
    SELECT DISTINCT 
        co.person_id, 
        co.first_treatment_date, 
        dt.drug_class_name, 
        CASE WHEN dt.drug_class_name = 'metformin'
             THEN 1 
             ELSE 0
        END AS metformin, 
        pr.npi,
        pm.egfr, 
        COALESCE(pm.egfr_lab_measured, 0) AS egfr_lab_measured,
        md.measurement_date 
    FROM observed_cohort co 
    JOIN diabetes_treatment_occurrences dt 
    ON co.person_id = dt.person_id 
    AND co.first_treatment_date = dt.drug_exposure_start_date 
    LEFT JOIN most_recent_measurement_date md 
    ON co.person_id = md.person_id 
    LEFT JOIN prior_egfr_measurements pm 
    ON co.person_id = pm.person_id 
    AND md.measurement_date = pm.measurement_date 
    LEFT JOIN provider pr
    ON dt.provider_id = pr.provider_id
    ORDER BY person_id
);

DROP TABLE IF EXISTS {schema_name}.t2dm_cohort;
CREATE TABLE {schema_name}.t2dm_cohort AS (
    WITH n_treatment_types AS (
        SELECT person_id,
               COUNT(DISTINCT metformin) AS treatment_types
        FROM {schema_name}.t2dm_cohort_with_missing_data
        GROUP BY person_id
    ),
    n_providers_per_patient AS (
        SELECT person_id,
               COUNT(DISTINCT npi) AS n_providers
        FROM {schema_name}.t2dm_cohort_with_missing_data
        WHERE npi IS NOT NULL
        GROUP BY person_id
    )
    SELECT DISTINCT
        c.person_id, 
        c.first_treatment_date, 
        c.metformin, 
        c.npi,
        c.egfr, 
        COALESCE(c.egfr_lab_measured, 0) AS egfr_lab_measured,
        c.measurement_date 
    FROM {schema_name}.t2dm_cohort_with_missing_data c
    JOIN n_treatment_types t
    ON c.person_id = t.person_id
    JOIN n_providers_per_patient p
    ON c.person_id = p.person_id
    WHERE c.egfr IS NOT NULL
    AND t.treatment_types = 1
    AND p.n_providers = 1
);