import sys
from os.path import dirname, abspath
from itertools import product

import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def write_R_script_to_fit_models():
    '''
    Write a R script that fits each model and computes the predictions for each model
    Also write a csv with model names and 
    '''
    egfr_knot_options = ['0', '3', '4', '5', '5s', '6']
    age_knot_options  = [0, 3, 4, 5, 6]
    trt_date_knot_options = [0, 3, 4, 5, 6]
    output_str  = ''
    model_names = []
    num_params  = []
    pred_df_str = 'predictions_df <- data.frame('
    for num_egfr_knots, num_age_knots, num_trt_date_knots in product(egfr_knot_options, age_knot_options, trt_date_knot_options):
        setting = 'e' + num_egfr_knots + '_a' + str(num_age_knots) + '_t' + str(num_trt_date_knots)
        no_random_effect_setting = '_without_random_effects_' + setting
        random_intercept_setting = '_with_random_intercepts_' + setting
        random_slope_setting     = '_with_random_slopes_'     + setting
        no_random_effect_str = 'model' + no_random_effect_setting \
                             + ' <- glm(metformin ~ egfr_z + age_z + trt_date_z + heart_failure + male'
        random_intercept_str = 'model' + random_intercept_setting \
                             + ' <- glmer(metformin ~ egfr_z + age_z + trt_date_z + heart_failure + male + (1 | npi)'
        random_slope_str     = 'model' + random_slope_setting \
                             + ' <- glmer(metformin ~ age_z + trt_date_z + heart_failure + male'
        slope_term_str       = ' + (egfr_z '
        no_random_effect_num_params = 6
        random_intercept_num_params = 7
        random_slope_num_params     = 6
        
        if num_egfr_knots == '5s':
            egfr_terms = '+ egfr_z_stage_knot1of5 + egfr_z_stage_knot2of5 + egfr_z_stage_knot3of5'
            no_random_effect_str += ' ' + egfr_terms
            random_intercept_str += ' ' + egfr_terms
            slope_term_str       += egfr_terms + ' '
            no_random_effect_num_params += 3
            random_intercept_num_params += 3
            random_slope_num_params     += 10
        elif num_egfr_knots == '0':
            random_slope_num_params     += 3
        else:
            int_num_egfr_knots = int(num_egfr_knots)
            for knot_idx in range(int_num_egfr_knots - 2):
                knot_term = '+ egfr_z_knot' + str(knot_idx + 1) + 'of' + num_egfr_knots
                no_random_effect_str += ' ' + knot_term
                random_intercept_str += ' ' + knot_term
                slope_term_str       += knot_term + ' '
            no_random_effect_num_params += int_num_egfr_knots - 2
            random_intercept_num_params += int_num_egfr_knots - 2
            random_slope_num_params     += int((int_num_egfr_knots)*(int_num_egfr_knots - 1)/2) + int_num_egfr_knots - 2
        slope_term_str += '| npi)'
        random_slope_str += slope_term_str
        
        if num_age_knots > 0:
            for knot_idx in range(num_age_knots - 2):
                knot_term = ' + age_z_knot' + str(knot_idx + 1) + 'of' + str(num_age_knots)
                no_random_effect_str += knot_term
                random_intercept_str += knot_term
                random_slope_str     += knot_term
            no_random_effect_num_params += num_age_knots - 2
            random_intercept_num_params += num_age_knots - 2
            random_slope_num_params     += num_age_knots - 2
        
        if num_trt_date_knots > 0:
            for knot_idx in range(num_trt_date_knots - 2):
                knot_term = ' + trt_date_z_knot' + str(knot_idx + 1) + 'of' + str(num_trt_date_knots)
                no_random_effect_str += knot_term
                random_intercept_str += knot_term
                random_slope_str     += knot_term
            no_random_effect_num_params += num_trt_date_knots - 2
            random_intercept_num_params += num_trt_date_knots - 2
            random_slope_num_params     += num_trt_date_knots - 2
                
        finish_model_str = ', family = binomial(), data = df)\n'
        no_random_effect_pred_name = 'glm' + no_random_effect_setting
        no_random_effect_prediction_str = no_random_effect_pred_name + ' <- predict(model' + no_random_effect_setting \
                                        + ', newdata = df)\n'
        no_random_effect_str += finish_model_str + no_random_effect_prediction_str
        output_str += no_random_effect_str
        model_names.append(no_random_effect_pred_name)
        num_params.append(no_random_effect_num_params)
        pred_df_str += no_random_effect_pred_name + ', '
        
        random_intercept_pred_name = 'glm' + random_intercept_setting
        random_intercept_prediction_str = random_intercept_pred_name + ' <- predict(model' + random_intercept_setting \
                                        + ', newdata = df)\n'
        random_intercept_str += finish_model_str + random_intercept_prediction_str
        output_str += random_intercept_str
        model_names.append(random_intercept_pred_name)
        num_params.append(random_intercept_num_params)
        pred_df_str += random_intercept_pred_name + ', '
        
        random_slope_pred_name = 'glm' + random_slope_setting
        random_slope_prediction_str = random_slope_pred_name + ' <- predict(model' + random_slope_setting \
                                    + ', newdata = df)\n'
        random_slope_str += finish_model_str + random_slope_prediction_str
        output_str += random_slope_str
        model_names.append(random_slope_pred_name)
        num_params.append(random_slope_num_params)
        pred_df_str += random_slope_pred_name + ', '
        
    pred_df_str = pred_df_str[:-2] + ')\nwrite.csv(predictions_df, paste(outpath, "model_predictions.csv", sep=""))\n'
    output_str += pred_df_str
    
    with open('generated_script_to_fit_glms.R', 'w') as f:
        f.write(output_str)
    
    num_params_df = pd.DataFrame(data    = {'model_name': model_names,
                                            'num_params': num_params},
                                 columns = ['model_name', 'num_params'])
    num_params_df.to_csv(config.output_dir + 'glm_num_params.csv', index = False)
    
if __name__ == '__main__':
    
    write_R_script_to_fit_models()