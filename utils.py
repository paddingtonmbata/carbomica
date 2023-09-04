import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import atomica as at


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
    pop = results[0].pop_names[0]
    pars = results[0].par_names(pop)
    parameters = []
    for par in pars:
        if 'actual' in par:
            parameters.append(par)
    
    rows = ['Status-\nquo'] + [res.name for res in results]
    df_emissions = pd.DataFrame(index=rows, columns=parameters)
    start_i = list(results[0].t).index(start_year)
    for par in parameters:
        df_emissions.loc['Status-\nquo', par] = results[0].get_variable(par, facility_code)[0].vals[start_i-1]
    for res in results:
        # Create DataFrame of emissions
        for par in parameters:
            df_emissions.loc[res.name, par] = res.get_variable(par, facility_code)[0].vals[start_i]
        
    # Print to excel
    writer_emissions = pd.ExcelWriter('results/{}.xlsx'.format(file_name), engine='xlsxwriter')    
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
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.title('Total CO2e emissions')
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
    prog_codes = results[0].model.progset.programs
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
    plt.title('Budget optimization')
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

def write_alloc_excel(progset, results, year, print_results=True,file_name=None):
    """Write optimized budget alloations onto an excel file
        :param: P: atomica project
        :param: results: results from optimization runs
        :param: save_dir: path for saving the plot
        :param: name to be given to excel file (string)"""
        
    progname = []
    prog_labels = []
    for prog in progset.programs:
        progname += [prog]
        prog_labels += [progset.programs[prog].label]
        
    bars = []
    for i in range(0, len(results)):
         bar_name = results[i].name
         bars.append(bar_name)
         
    d1 = at.PlotData.programs(results, quantity='spending')
    d1.interpolate(year)
    spending_raw_data = {(x.result, x.output): x.vals[0] for x in d1.series}
    spending_data = {res: {prog:0 for prog in progname} for res in bars}
    
    d2 = at.PlotData.programs(results, quantity='coverage_fraction')
    d2.interpolate(year)
    cov_raw_data = {(x.result, x.output): x.vals[0] for x in d2.series}
    cov_data = {res: {prog:0 for prog in progname} for res in bars}
    for br in bars:
        for prog in progname:
            spending_data[br][prog] = spending_raw_data[(br, prog)]
            cov_data[br][prog] = cov_raw_data[(br, prog)]
    df1 = pd.DataFrame(spending_data)
    df2 = pd.DataFrame(cov_data)
    df1.index = prog_labels
    df2.index = prog_labels
    
    if print_results:
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name="Budgets")
        df2.to_excel(writer, sheet_name="Coverages")
        writer.save()
        print('Excel file saved: {}'.format(file_name))
    
    return df1, df2