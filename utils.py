import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np

#%%
facilities = {
    'aga-khan_hosp_KE': {'label': 'Aga Khan Hospital, Kenya', 'type': 'facilities'},
    'aga-khan_medi_KE': {'label': 'Aga Khan Medical Centre, Kenya', 'type': 'facilities'},
    'laudium_chc_SA': {'label': 'Laudium Community Health Centre, South Africa', 'type': 'facilities'},
    'stanza-bopape_chc_SA': {'label': 'Stanza Bopape Community Health Centre, South Africa', 'type': 'facilities'},
    'mamelodi_hosp_SA': {'label': 'Mamelodi Regional Hospital, South Africa', 'type': 'facilities'},
    'mt-darwin_hosp_ZW': {'label': 'Mt Darwin District Hospital, Zimbabwe', 'type': 'facilities'},
    'dotito_rhcc_ZW': {'label': 'Dotito Rural Health Care Clinic, Zimbabwe', 'type': 'facilities'},
    'chitse_rhcc_ZW': {'label': 'Chitse Rural Health Care Clinic, Zimbabwe', 'type': 'facilities'}
    }

# Mitigation interventions (modify as needed)
interventions = {
    'energy_led': 'Energy saving LED',
    'low_emit_mat': 'Low emitting materials',
    'electric_cars': 'Electric cars',
    'low_emit_gas': 'Low emitting anesthetic gases',
    'borehole_water': 'Borehole water',
    'recycle': 'Recycling',
    'low_emit_inhale': 'Low emitting inhalers',
    'local_procure': 'Local procurements'
    }

#%% Calculation functions
def calc_emissions(results,start_year,facility_code,file_name):
    '''
    Calculate emissions before and after programs implementation, export results to excel and generate bar plots
    :param results: list of atomica result objects
    :param start_year: start year of programs 
    :param facility: facility code
    :param file_name: (optional) specify excel file name for saving
    :return: df_emissions: dataFrame of results
    '''
    parameters = ['co2e_emissions_actual'
                ]
    outcomes = ['Total CO2e emissions'
                ]
    writer_emissions = pd.ExcelWriter('results/{}.xlsx'.format(file_name), engine='xlsxwriter')    
    
    rows = ['Status-quo'] + [res.name for res in results]
    df_emissions = pd.DataFrame(index=rows, columns=outcomes)
    start_i = list(results[0].t).index(start_year)
    for par, out in zip(parameters,outcomes):
        df_emissions.loc['Status-quo', out] = results[0].get_variable(par, facility_code)[0].vals[start_i-1]
    for res in results:
        # Create DataFrame of emissions
        for par, out in zip(parameters,outcomes):
            df_emissions.loc[res.name, out] = res.get_variable(par, facility_code)[0].vals[start_i]
        
    # Print to excel
    df_emissions.to_excel(writer_emissions, sheet_name=facility_code, index=True)
    workbook  = writer_emissions.book
    worksheet = writer_emissions.sheets[facility_code]
    format_emit = workbook.add_format({'num_format': '#,##0.00'})
    for i in np.arange(len(rows)):
        worksheet.set_row(i+1, None, format_emit) 
    
    # Generate bar plots of emissions
    plt.figure()
    ax = df_emissions.plot.bar(stacked=True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.05,1), prop={'size':7})
    plt.title('Total CO2e emissions (metric tonnes)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('figs/{}.png'.format(file_name))
    plt.show()
    plt.close()
        
    writer_emissions.close()
    print('Emissions results saved: results/{}.xlsx'.format(file_name))
    print('Emissions bar plots saved: figs/{}.xlsx'.format(file_name))
    
    return df_emissions
    
def calc_allocation(results,file_name):
    '''
    Prints allocation to excel
    :param results: list of atomica result objects
    :param file_name: (optional) specify excel file name for saving
    '''
    prog_codes = results[0].model.progset.programs.keys()
    prog_labels = [results[0].model.progset.programs[prog].label for prog in prog_codes]
    res_names = [res.name for res in results]
    df_spending_optimized = pd.DataFrame(index=res_names, columns=prog_labels)
    
    for res in results:
        for prog_code, prog_name in zip(prog_codes,prog_labels):
            df_spending_optimized.loc[res.name,prog_name] = res.get_alloc()[prog_code][0]
        
    plt.figure()
    ax = df_spending_optimized.plot.bar(stacked=True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.05,1), prop={'size':7})
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('${x:,.0f}'))
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('figs/{}.png'.format(file_name))
    plt.show()
    plt.close()
        
    writer_optim = pd.ExcelWriter('results/{}.xlsx'.format(file_name), engine='xlsxwriter')    
    df_spending_optimized.to_excel(writer_optim, sheet_name='Optimized allocation', index=True)
    
    workbook  = writer_optim.book
    worksheet = writer_optim.sheets['Optimized allocation']
    format_cost = workbook.add_format({'num_format': '$#,##0.0'})
    for i in np.arange(len(res_names)):
        worksheet.set_row(i+1, None, format_cost) 
    writer_optim.close()
    print('Allocation results saved: results/{}.xlsx'.format(file_name))
    print('Allocation bar plots saved: figs/{}.xlsx'.format(file_name))
    
    return df_spending_optimized