import sys
from os.path import dirname, abspath

import numpy as np
import pandas as pd
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def plot_treatment_policy_vs_egfr():
    '''
    Plot estimated metformin probability vs eGFR
    1. black solid line for model without random effects
    2. faded blue lines for model with provider-specific random effects
    3. green and purple solid lines for 2 outlying providers
    Plot general population histograms for eGFR levels per medication within category of patient characteristics,
    blue for metformin, orange for other
    Plot the outlying provider's eGFR levels per medication on separate lines on top of histograms,
    match line color with dot for metformin and x for other
    Title each subplot with age, treatment date, heart failure, and sex of category:
    No heart failure, F, age 50, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, F, age 70, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, F, age 70, treatment date middle between 2017-09-26 and 2020-10-21
    No heart failure, M, age 50, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, M, age 70, treatment date middle between 2013-02-18 and 2015-08-29
    No heart failure, M, age 70, treatment date middle between 2017-09-26 and 2020-10-21
    Also create a stand-alone plot with just estimated metformin probability vs eGFR for the first category
    '''
    plt.rcParams.update({'axes.titlesize' : 14,
                         'axes.labelsize' : 14,
                         'xtick.labelsize': 12,
                         'ytick.labelsize': 12,
                         'legend.fontsize': 12})
    fig, ax = plt.subplots(nrows       = 4,
                           ncols       = 3,
                           figsize     = (4.8 * 3, 4.8 * 1.5 * 2),
                           gridspec_kw = {'height_ratios': [1, 2, 1, 2]},
                           sharex      = 'all',
                           sharey      = 'row')
    indiv_fig, indiv_ax = plt.subplots(nrows = 1,
                                       ncols = 1,
                                       figsize = (6.4, 4.8))
    
    sample_df           = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    npi_df              = pd.read_csv(config.output_dir + 'npi_glrt_pvalues.csv')
    pred_df_without_npi = pd.read_csv(config.output_dir + 'category_predictions_for_plotting.csv')
    pred_df_with_npi    = pd.read_csv(config.output_dir + 'category_predictions_with_npis_for_plotting.csv')
    
    sample_df.rename(columns = {'egfr': 'eGFR'},
                     inplace = True)
    egfr_min          = sample_df['eGFR'].min()
    egfr_max          = sample_df['eGFR'].max()
    egfr_vals_to_plot = np.arange(egfr_min, egfr_max + 1)
    
    sample_df['Treatment'] = np.where(sample_df['metformin'] == 1, 'Metformin', 'DPP-4i / Sulfonylurea')
    treatment_order        = ['Metformin', 'DPP-4i / Sulfonylurea']
    
    npis               = npi_df['NPI'].values
    num_npis           = len(npis)
    outlying_colors    = ['darkgreen', 'indigo']
    # use line below to set alpha by p-value rank so less "normal" providers are more faded
    # nonoutlying_alphas = [.2 + .3 * i / (num_npis - len(config.outlying_npis) - 1) for i in range(num_npis - len(config.outlying_npis))]
    nonoutlying_alphas = [.35 for _ in range(num_npis - len(config.outlying_npis))]
    metformin_color    = 'steelblue'
    other_color        = 'orange'
    
    category_titles           = ['F50 2014-05-25', 'F70 2014-05-25', 'F70 2019-04-09', 'M50 2014-05-25', 'M70 2014-05-25', 'M70 2019-04-09']
    category_sexes            = [0, 0, 0, 1, 1, 1]
    category_age_ranges       = [[45, 54], [45, 54], [65, 74], [45, 54], [45, 54], [65, 74]]
    category_trt_date_ranges  = [['2013-02-18', '2015-08-29'], ['2013-02-18', '2015-08-29'], ['2017-09-26', '2020-10-21'],
                                 ['2013-02-18', '2015-08-29'], ['2013-02-18', '2015-08-29'], ['2017-09-26', '2020-10-21']]
    
    for category_idx in range(len(category_titles)):
        if category_idx < 3:
            row_idx = 0
            col_idx = category_idx
        else:
            row_idx = 1
            col_idx = category_idx - 3
        
        sex            = category_sexes[category_idx]
        age_range      = category_age_ranges[category_idx]
        trt_date_range = category_trt_date_ranges[category_idx]
        
        # create histograms
        category_df = sample_df.loc[np.logical_and.reduce((sample_df['heart_failure'] == 0,
                                                           sample_df['male'] == sex,
                                                           sample_df['age'] >= age_range[0],
                                                           sample_df['age'] <= age_range[1],
                                                           sample_df['first_treatment_date'] >= trt_date_range[0],
                                                           sample_df['first_treatment_date'] <= trt_date_range[1]))]
        sns.histplot(data      = category_df,
                     x         = 'eGFR',
                     hue       = 'Treatment',
                     hue_order = treatment_order,
                     palette   = [metformin_color, other_color],
                     ax        = ax[2 * row_idx, col_idx],
                     legend    = False,
                     binwidth  = 15,
                     binrange  = [0, 165])
        
        # create markers for outlying providers
        for npi_idx in range(len(config.outlying_npis)):
            npi_df = category_df.loc[category_df['npi'] == config.outlying_npis[npi_idx]]
            if len(npi_df) == 0:
                continue
            npi_df[' '] = 33 # place markers above histograms
            sns.scatterplot(data        = npi_df,
                            x           = 'eGFR',
                            y           = ' ',
                            style       = 'Treatment',
                            style_order = treatment_order,
                            c           = outlying_colors[npi_idx % 2],
                            markers     = ['o', 'X'],
                            legend      = False,
                            ax          = ax[2 * row_idx, col_idx])
        
        # plot predictions with random effects for outlying providers and all other providers
        logits_with_random_effects  = pred_df_with_npi['category_' + str(category_idx) + '_npi_pred'].values
        probs_with_random_effects   = 1./(1. + np.exp(-1*logits_with_random_effects))
        plot_df_with_random_effects = pd.DataFrame(data    = {'eGFR': np.tile(egfr_vals_to_plot, num_npis),
                                                              'Metformin probability': probs_with_random_effects,
                                                              'NPI': np.repeat(npis, len(egfr_vals_to_plot))},
                                                   columns = ['eGFR', 'Metformin probability', 'NPI'])
        
        for npi_idx in range(num_npis - len(config.outlying_npis)):
            npi = npis[npi_idx + len(config.outlying_npis)]
            npi_plot_df = plot_df_with_random_effects.loc[plot_df_with_random_effects['NPI'] == npi]
            sns.lineplot(data   = npi_plot_df,
                         x      = 'eGFR',
                         y      = 'Metformin probability',
                         c      = metformin_color,
                         alpha  = nonoutlying_alphas[npi_idx],
                         legend = False,
                         ax     = ax[2 * row_idx + 1, col_idx])
            if row_idx == 0 and col_idx == 0:
                sns.lineplot(data   = npi_plot_df,
                             x      = 'eGFR',
                             y      = 'Metformin probability',
                             c      = metformin_color,
                             alpha  = nonoutlying_alphas[npi_idx],
                             legend = False,
                             ax     = indiv_ax)
        
        for npi_idx in range(len(config.outlying_npis)):
            npi_plot_df = plot_df_with_random_effects.loc[plot_df_with_random_effects['NPI'] 
                                                          == config.outlying_npis[npi_idx]]
            sns.lineplot(data   = npi_plot_df,
                         x      = 'eGFR',
                         y      = 'Metformin probability',
                         c      = outlying_colors[npi_idx % 2],
                         legend = False,
                         ax     = ax[2 * row_idx + 1, col_idx])
            if row_idx == 0 and col_idx == 0:
                sns.lineplot(data   = npi_plot_df,
                             x      = 'eGFR',
                             y      = 'Metformin probability',
                             c      = outlying_colors[npi_idx % 2],
                             legend = False,
                             ax     = indiv_ax)
        
        # plot predictions without random effects
        logits_without_random_effects  = pred_df_without_npi['category_' + str(category_idx) + '_pred'].values
        probs_without_random_effects   = 1./(1. + np.exp(-1*logits_without_random_effects))
        plot_df_without_random_effects = pd.DataFrame(data    = {'eGFR': egfr_vals_to_plot,
                                                                 'Metformin probability': probs_without_random_effects},
                                                      columns = ['eGFR', 'Metformin probability'])
        sns.lineplot(data   = plot_df_without_random_effects,
                     x      = 'eGFR',
                     y      = 'Metformin probability',
                     c      = 'black',
                     legend = False,
                     ax     = ax[2 * row_idx + 1, col_idx])
        if row_idx == 0 and col_idx == 0:
            sns.lineplot(data   = plot_df_without_random_effects,
                         x      = 'eGFR',
                         y      = 'Metformin probability',
                         c      = 'black',
                         legend = False,
                         ax     = indiv_ax)
        
        ax[2 * row_idx, col_idx].set_title(category_titles[category_idx])
        ax[2 * row_idx, col_idx].set_xlim([egfr_min, egfr_max + 1])
        ax[2 * row_idx + 1, col_idx].set_xlim([egfr_min, egfr_max + 1])
        ax[2 * row_idx + 1, col_idx].set_ylim([0, 1])

        if row_idx == 0 and col_idx == 0:
            indiv_ax.set_title(category_titles[category_idx])
            indiv_ax.set_xlim([egfr_min, egfr_max + 1])
            indiv_ax.set_ylim([0, 1])
        
    # create legends
    if len(config.outlying_npis) > 0:
        metformin_patch         = mpatches.Patch(color = 'white', label = 'Metformin')
        general_metformin_patch = mpatches.Patch(color = metformin_color, label = 'General')
        hist_legend_handles = [metformin_patch, general_metformin_patch]
        for npi_idx in range(len(config.outlying_npis)):
            npi_metformin_dot = mlines.Line2D([],
                                              [],
                                              color     = outlying_colors[npi_idx % 2],
                                              marker    = 'o',
                                              linestyle = 'None',
                                              label     = 'Small p-value NPI ' + str(npi_idx))
            hist_legend_handles.append(npi_metformin_dot)
        
        other_patch         = mpatches.Patch(color = 'white',  label = 'DPP-4i / Sulfonylurea')
        general_other_patch = mpatches.Patch(color = other_color, label = 'General')
        hist_legend_handles.extend([other_patch, general_other_patch])
        for npi_idx in range(len(config.outlying_npis)):
            npi_other_dot = mlines.Line2D([],
                                          [],
                                          color     = outlying_colors[npi_idx % 2],
                                          marker    = 'X',
                                          linestyle = 'None',
                                          label     = 'Small p-value NPI ' + str(npi_idx))
        
        ax[2, -1].legend(handles = hist_legend_handles, ncol = 1, loc = 'upper right')
        
        general_line = mlines.Line2D([],
                                     [],
                                     color = 'black',
                                     label = 'General')
        line_legend_handles = [general_line]
        for npi_idx in range(len(config.outlying_npis)):
            npi_line = mlines.Line2D([],
                                     [],
                                     color = outlying_colors[npi_idx % 2],
                                     label = 'Small p-value NPI ' + str(npi_idx))
            line_legend_handles.append(npi_line)
        
        large_pval_npi_line = mlines.Line2D([],
                                            [],
                                            color = metformin_color,
                                            alpha = nonoutlying_alphas[-1],
                                            label = 'Other NPI (larger p-value)')
        small_pval_npi_line = mlines.Line2D([],
                                            [],
                                            color = metformin_color,
                                            alpha = nonoutlying_alphas[0],
                                            label = 'Other NPI (smaller p-value)')
        line_legend_handles.extend([large_pval_npi_line, small_pval_npi_line])
        ax[3, -1].legend(handles = line_legend_handles, loc = 'upper right')
        
        ax[2, -1].axis('off')
        ax[3, -1].axis('off')
    else:
        metformin_patch = mpatches.Patch(color = metformin_color, label = 'Metformin')
        other_patch     = mpatches.Patch(color = other_color,  label = 'DPP-4i / Sulfonylurea')
        hist_legend_handles = [metformin_patch, other_patch]
        ax[0, -1].legend(handles = hist_legend_handles, ncol = 1, loc = 'upper right')
        general_line = mlines.Line2D([],
                                     [],
                                     color = 'black',
                                     label = 'General')
        npi_line = mlines.Line2D([],
                                 [],
                                 color = metformin_color,
                                 alpha = .7,
                                 label = 'Individual providers')
        line_legend_handles = [general_line, npi_line]
        ax[1, -1].legend(handles = line_legend_handles, loc = 'lower center')

    indiv_ax.legend(handles = line_legend_handles, loc = 'lower center')
    
    fig.tight_layout()
    fig.savefig(config.output_dir + 'treatment_policy_plot.pdf')

    indiv_fig.tight_layout()
    indiv_fig.savefig(config.output_dir + 'single_category_treatment_policy_plot.pdf')
    
if __name__ == '__main__':
    
    plot_treatment_policy_vs_egfr()