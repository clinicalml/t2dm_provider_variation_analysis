import sys
from os.path import dirname, abspath

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def make_plot():
    '''
    Plot eGFR values colored by treatment decisions for different providers
    Order providers by metformin prescription rate
    For graphical abstract, only plot 10 providers
    '''
    patient_df = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    metformin_prescription_rate_df = patient_df.groupby(by = 'npi')['metformin'].mean().reset_index().sort_values(by='metformin')
    npis_sorted = metformin_prescription_rate_df['npi'].values
    keep_idxs = np.array([0, 2, 8, 22, 52, 82, 111, 141, 161, 171])
    npis_sorted = npis_sorted[keep_idxs]
    patient_df = patient_df.loc[patient_df['npi'].isin(npis_sorted)]
    npi_yvals = {npis_sorted[idx]: len(npis_sorted) - idx
                 for idx in range(len(npis_sorted))}
    plot_egfrs = patient_df.egfr.values
    plot_yvals = [npi_yvals[npi] for npi in patient_df.npi.values]
    plot_metformins = ['Metformin' if metformin == 1 else 'DPP-4i / Sulfonylurea'
                       for metformin in patient_df.metformin.values]
    plot_df = pd.DataFrame(data    = {'eGFR (mL/min/1.73m^2)': plot_egfrs,
                                      'Provider'             : plot_yvals,
                                      'Treatment'            : plot_metformins},
                           columns = ['eGFR (mL/min/1.73m^2)', 'Provider', 'Treatment'])
    
    fig, ax = plt.subplots(figsize = (5.6, 3.6))
    sns.scatterplot(data        = plot_df,
                    x           = 'eGFR (mL/min/1.73m^2)',
                    y           = 'Provider',
                    hue         = 'Treatment',
                    style       = 'Treatment',
                    hue_order   = ['Metformin', 'DPP-4i / Sulfonylurea'],
                    style_order = ['Metformin', 'DPP-4i / Sulfonylurea'],
                    ax          = ax)
    for i in range(len(npis_sorted)):
        color = 'grey'
        label = None
        ax.axhline(len(npis_sorted) - i, alpha = .25, c = color, label = label)
    ax.set_ylim([0, len(npis_sorted) + 1])
    h, l = ax.get_legend_handles_labels()
    ax.legend_.remove()
    ax.legend(h, l, ncol=2, loc = 'upper center', bbox_to_anchor = (0.35, 1.15))
    plt.tick_params(axis       = 'y',
                    which      = 'both',
                    left       = False,
                    right      = False,
                    labelleft  = False,
                    labelright = False)
    fig.tight_layout()
    fig.savefig(config.output_dir + 'provider_vs_egfr_plot_graphical_abstract.pdf')
    
if __name__ == '__main__':
    
    make_plot()