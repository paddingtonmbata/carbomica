import atomica as at
import pandas as pd
from utils import facilities, interventions
'''
Script to generate a framework, databook and progbook.
'''

#%% Step 1: generate parameters for framework

# read framework from templates
dfs = pd.read_excel(pd.ExcelFile('templates/carbomica_framework_base.xlsx'), sheet_name=None)

# add intervention variables
for key in interventions:
    coverage = {'Code Name': key + '_cov', 
                'Display Name': interventions[key] + ' - coverage',
                'Default Value': 0,
                'Minimum Value': 0,
                'Maximum Value': 1,
                'Targetable': 'y',
                'Databook Page': 'coverage',
                'Population type': 'facilities',
                'Timed': 'n', 'Is derivative': 'n'} # define coverage of intervention as a new row in framework
    effect = {'Code Name': key, 
              'Display Name': interventions[key],
              'Format': 'number',
              'Minimum Value': 0,
              'Maximum Value': 1,
              'Targetable': 'n',
              'Databook Page': 'intervention',
              'Guidance': 'Input as X% reduction in emissions',
              'Population type': 'facilities',
              'Timed': 'n', 'Is derivative': 'n'} # define effect of intervention as a new row in framework
    dfs['Parameters'] = dfs['Parameters'].append(coverage, ignore_index=True) # add the coverage row to the framework
    dfs['Parameters'] = dfs['Parameters'].append(effect, ignore_index=True) # add the effect row to the framework
    # update the function for overall_multiplier:
    function = dfs['Parameters'].loc[dfs['Parameters']['Code Name']=='overall_multiplier', 'Function']
    dfs['Parameters'].loc[dfs['Parameters']['Code Name']=='overall_multiplier', 'Function'] = function+'*(1-'+coverage['Code Name']+'*'+effect['Code Name']+')'
    
with pd.ExcelWriter('carbomica_framework.xlsx') as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    

#%% Step 2: generate databook
F = at.ProjectFramework('carbomica_framework.xlsx')  # load framework
data_years = 2023 # years for input data

# Option to generate empty databook, or generate and populate databook

gen_databook = False # 'True' if generating databooks (without populating)

if gen_databook :
    D = at.ProjectData.new(F,data_years,pops=facilities,transfers=0)
    D.save('templates/carbomica_databook.xlsx')

pop_databook = False # True if generating and populating databook

if pop_databook : 
    D = at.ProjectData.new(framework=F, tvec=data_years, pops=facilities, transfers=0)
    db_data = pd.read_excel('input_data.xlsx', sheet_name='data', index_col='facilities')

    for facility in facilities.keys():
        for parameter in db_data.columns:
            D.tdve[parameter].ts[facility] = at.TimeSeries(data_years, db_data.loc[facility,parameter], units='Number')
            D.tdve[parameter].write_assumption = True
        
    D.save('books/carbomica_databook.xlsx')
    
#%% Step 3: generate program books after filling in databook (note that progbook will not generate if data cells in databook are empty)
gen_progbook = False # 'True' if generating progbooks, 'False' if generating databooks
databook_name = 'books/carbomica_databook.xlsx'
if gen_progbook :
    P = at.Project(framework=F,databook=databook_name, do_run=False)
    for facility in facilities.keys():
        progbook_path = 'templates/carbomica_progbook_{}.xlsx'.format(facility)
        P.make_progbook(progbook_path,progs=interventions,data_start=data_years,data_end=data_years)
        
# In order to populate the progbook, the empty progbooks that were just created (in files) are read in first
pop_progbook = True

if pop_progbook:
    D = at.ProjectData.from_spreadsheet(databook_name,framework=F) 
    pb_costs = pd.read_excel('input_data.xlsx', sheet_name='unit_costs', index_col='facilities')  
    for facility in facilities.keys():
        P = at.ProgramSet.from_spreadsheet(spreadsheet='templates/carbomica_progbook_{}.xlsx'.format(facility), framework=F, data=D, _allow_missing_data=True)
        for intervention in interventions.keys():
            P.programs[intervention].unit_cost = at.TimeSeries(assumption=pb_costs.loc[facility,intervention], units='$/person/year')
            P.programs[intervention].spend_data = at.TimeSeries(data_years,1e-16, units='$/year') # make it a small, negligible but non-zero number for optimisation
            P.programs[intervention].capacity_constraint = at.TimeSeries(units='people')
            P.programs[intervention].coverage = at.TimeSeries(units='people')
        P.save('books/carbomica_progbook_{}.xlsx'.format(facility))  