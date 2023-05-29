import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

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
    parameters = ['SC1_energy_actual',
                'SC1_travel_actual',
                'SC1_refrigerants_actual',
                'SC1_waste_actual',
                'SC1_anaesthetic_actual',
                'SC2_electricity_actual',
                'SC2_heat_actual',
                'SC3_energy_actual',
                'SC3_refrigerants_actual',
                'SC3_travel_actual',
                'SC3_business_actual',
                'SC3_water_actual',
                'SC3_waste_actual',
                'SC3_logistics_actual',
                'SC3_inhalers_actual',
                'SC3_supply_actual'
                ]
    outcomes = ['SC1 Building energy',
                'SC1 Travel',
                'SC1 Refrigerants',
                'SC1 Waste',
                'SC1 Anaesthetic gases',
                'SC2 Purchased and consumed grid electricity',
                'SC2 Heat networks',
                'SC3 Building energy (building not owned)',
                'SC3 Refrigerants (building not owned)',
                'SC3 Travel (vehicles not owned)',
                'SC3 Employee business travel-road, rail, air',
                'SC3 Water',
                'SC3 Waste',
                'SC3 Contractor logistics',
                'SC3 Inhalers',
                'SC3 Supply chain'
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
    worksheet.set_row(1, None, format_emit)
    worksheet.set_row(2, None, format_emit)
    worksheet.set_row(3, None, format_emit)
    worksheet.set_row(4, None, format_emit)
    
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
    worksheet.set_row(1, None, format_cost)
    writer_optim.close()
    print('Allocation results saved: results/{}.xlsx'.format(file_name))
    print('Allocation bar plots saved: figs/{}.xlsx'.format(file_name))
    
    return df_spending_optimized