# T2DM provider variation analysis

The code in this repository can be used to assess variation in first-line type 2 diabetes treatment empirically using a large health insurance claims dataset. Since metformin, the guideline-recommended first-line treatment, is contraindicated for severe chronic kidney disease, we examine variation in this treatment decision on two axes: across estimated glomerular filtration rate (eGFR) measurements from the patient and across preferences from the prescribing provider.

## Set-up

Separate two conda environments for running R and Python scripts.

1. Create a conda environment for R with `conda create -n r_env r-base==4.3.2 r-essentials`.
2. Open `R` in terminal. Then run
```
install.packages("lme4", repos = "http://cran.us.r-project.org")
install.packages("rms", repos = "http://cran.us.r-project.org")
install.packages("dplyr", repos = "http://cran.us.r-project.org")
```
3. Create a conda environment for running Python scripts with `conda env create --file=python_env.yml`.
4. Set `data_dir` and `output_dir` in `config.py` to point to your data and output directories.
5. Set `inpath` and `outpath` in `regression_modeling/analysis_setup.R` to match `data_dir` and `output_dir`, respectively.

## Data extraction

We assume data is in a postgres database following the OMOP CDM format (https://www.ohdsi.org/data-standardization/). These steps extract the patients in the cohort, the first-line treatments they, the providers who prescribe these treatments, and the following features for each patient: most recent eGFR measurement, age, treatment date, history of heart failure, and sex.

1. Create the schema in the database by running `psql {database_name}` => (in psql) `CREATE SCHEMA {schema_name}`
2. Extract the first occurrence of diabetes treatment for each person by running `python3 extract_data.py --database_name={database_name} --schema_name={schema_name} --step=first_treatment`
3. Extract the csv for downstream analyses by running in `psql {database_name}` => (in psql):
   ```
   SET search_path TO {schema_name};
   \copy t2dm_cohort_with_covariates
   TO t2dm_cohort_data.csv
   WITH (FORMAT CSV, HEADER);
   ```
4. To filter down to only patients whose providers have at least 10 patients for the second stage of the analysis, run `python3 filter_data_with_frequent_providers.py`.
5. To compute cohort statistics, run `python3 compute_cohort_stats.py --database_name={database_name} --schema_name={schema_name}`.

## Testing for variation across eGFR levels

The output from the previous step includes the numbers required for running the chi-squared test for variation in first-line T2DM treatments across eGFR levels. To run the chi-squared test for variation across eGFR levels, enter the `variation_tests` directory, add these numbers to a 2 x 5 array in `run_test_for_egfr_variation.py`, and run the script.

## Fitting regression models

To run generalized likelihood ratio tests (GLRTs) for provider variation, we need to fit models of metformin prescribing patterns. We build generalized linear models with cubic splines of the eGFR, age, and treatment date features. We also include the binary features sex and occurrence of heart failure. These were extracted in the previous part. In this part, we fit the models using R and select the models with the highest likelihood.

1. From within the `regression_modeling` directory, run `python3 write_R_script_to_fit_models.py` to write the R script for fitting models. This script fits models with up to 6 knots. As mentioned in step 5 below, if you are restricting the model to at most 4 knots, this script can be modified to reduce the time required to fit all the models.
2. From the root directory of this repository, open `R` in terminal. Keep this workspace open throughout this analysis, including step 3 under creating figures.
3. Run `source('regression_modeling/analysis_setup.R')` to create the cubic spline features. This script will print the knot values in Table 2.
4. Run `source('regression_modeling/generated_script_to_fit_glms.R')` to fit the regression models.
5. Run `python3 select_best_models.py` to identify the models with and without random effects that have the highest log likelihood. Set `best_model_without_random_effects` and `best_model_with_random_effects` to the model names with the highest log likelihood. These names start with `glm`. Also set the best model names in `make_predictions_for_plots.R`. This script is looking for the models, not the predictions, so replace `glm` with `model` in the names in the R script. The Python script in this step also outputs the models with the lowest AIC. This is useful if we want to select a model with fewer parameters to avoid overfitting. However, for the GLRT, the model with the highest log likelihood should be selected. Thus, we decide to restrict the models to at most 4 knots in this step. 

## Testing for provider variation and examining outliers

This section runs a GLRT for variation across all providers and a GLRT for each provider. Results for the latter are typically insignificant since there are few samples per provider. In that case, only step 1 below needs to be performed.

1. Enter the `variation_tests` directory and run `python3 run_tests_for_provider_variation.py` to test for variation across providers.
2. View the results at `npi_glrt_pvalues.csv` in the output directory set in `config.py`. Add the NPIs of providers with small p-values to `config.py`.
3. Run `python3 examine_outlying_providers.py` to see the patient profiles for any identified outlying providers.

## Creating figures

We create two figures to visualize how first-line treatment decisions relate to eGFR for individual providers. The first shows the observed decisions for each provider. The second shows the estimated prescribing policies from the generalized linear models.

1. Create Figure 1 by running `python3 create_provider_v_egfr_plot.py` from within the `figure_creation` directory. A smaller version of this figure is used for the graphical abstract and can be created by running `python3 make_graphical_abstract.py`.
2. Generating Figure 2 requires making predictions for different patient profiles (values of the features other than eGFR). The choice of feature values can be guided by frequency in the population or by frequency among patients seen by outlying providers. We recommend setting the feature values between two knots to avoid the sharp change in behavior around a knot. These feature values need to be set in `write_sample_input_csvs_for_plotting_predictions.py` and `plot_treatment_policy_vs_egfr.py`. Then run `python3 write_sample_input_csvs_for_plotting_predictions.py` to generate csvs that can be inputted for making predictions in the next step.
3. Get model predictions by running `source('figure_creation/make_predictions_for_plots.R')` in the R environment the regression models were fit in.
4. Create Figure 2 by running `python3 plot_treatment_policy_vs_egfr.py`. This script also outputs a plot showing the metformin probability for multiple patient profiles and the distribution of eGFR levels observed for patients with similar profiles. 

## Patient case studies

To examine specific patients seen by specific providers, for instance to see if there are other contraindications for metformin, we provide scripts for extracting the conditions, procedures, drugs, labs, visit types, and provider specialties for a patient up to their first treatment date.

1. Install `omop-learn v2.0` from https://github.com/clinicalml/omop-learn/tree/v2.0
2. Enter the `patient_case_studies` directory. Run `python3 create_cohort.py --schema_name={schema_name}` to create the cohort csv and empty cohort tables in the postgres databases.
3. In `psql {database_name}` => (in psql) :
```
\copy {schema_name}.small_pval_provider_patients FROM '{output_dir}/case_studies/case_study_patients.csv' DELIMITER ',' CSV HEADER;
```
4. Run `python3 extract_patient_data.py --database_name={database_name} --schema_name={schema_name}` to extract all patient records up to the first treatment date. These will be written to text files in `{output_dir}/case_studies/`