import atomica as at
import pandas as pd
import os
if not os.path.exists('books'): os.makedirs('books')
'''
Script to generate a framework, databook and progbook.
'''
#%% 
sites_list = pd.read_excel('input_data.xlsx', sheet_name='study sites', index_col='Code Name')
facilities = {}
for site in sites_list.index:
    facilities[site] = {'label': sites_list.loc[site,'Display Name'], 'type': 'facilities'}

interventions_list = pd.read_excel('input_data.xlsx', sheet_name='interventions', index_col='Code Name')
interventions = {}
for intervention in interventions_list.index:
    interventions[intervention] = interventions_list.loc[intervention,'Display Name']

#%% Step 1: read in base framework, and generate intervention-specific parameters 
# read framework base from template
df_fw = pd.read_excel(pd.ExcelFile('templates/carbomica_framework_template.xlsx'), sheet_name=None)
emissions_list = pd.read_excel('input_data.xlsx', sheet_name='emission sources', index_col='Code Name')

# define intervention-specific parameters and add to the Parameters sheet as a new row
for i, emission in enumerate(emissions_list.index):
    emission_par = {'Code Name': emission+'_baseline', 
                'Display Name': emissions_list.loc[emission,'Display Name'] + ' - baseline',
                'Targetable': 'n',
                'Databook Page': 'emission_sources'} # define coverage of intervention as a new row in framework
    emission_mult = {'Code Name': emission+'_mult', 
                'Display Name': emissions_list.loc[emission,'Display Name'] + ' - multiplier',
                'Targetable': 'y',
                'Default Value': 0,
                'Minimum Value': 0,
                'Maximum Value': 1,
                'Databook Page': 'targeted_pars'}
    emission_actual = {'Code Name': emission, 
            'Display Name': emissions_list.loc[emission,'Display Name'],
            'Targetable': 'n',
            'Population type': 'facilities',
            'Function': emission_par['Code Name']+'*(1-'+emission_mult['Code Name']+')'} # define coverage of intervention as a new row in framework
    df_fw['Parameters'] = df_fw['Parameters'].append(emission_par, ignore_index=True) # add the coverage row to the framework
    df_fw['Parameters'] = df_fw['Parameters'].append(emission_mult, ignore_index=True) # add the coverage row to the framework
    df_fw['Parameters'] = df_fw['Parameters'].append(emission_actual, ignore_index=True) # add the coverage row to the framework
    # update the function for total emissions:
    if i == 0:
        df_fw['Parameters'].loc[df_fw['Parameters']['Code Name']=='co2e_emissions','Function'] = emission_actual['Code Name']
    else:
        df_fw['Parameters'].loc[df_fw['Parameters']['Code Name']=='co2e_emissions','Function'] += '+'+emission_actual['Code Name']
    
with pd.ExcelWriter('carbomica_framework.xlsx') as writer:
    for sheet_name, df in df_fw.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

#%% Step 2: generate and populate the databook (saved in "books/")
F = at.ProjectFramework('carbomica_framework.xlsx')  # load framework
data_years = 2023 # years for input data

D = at.ProjectData.new(framework=F, tvec=data_years, pops=facilities, transfers=0)
db_data = pd.read_excel('input_data.xlsx', sheet_name='emission data', index_col='facilities')
cols_to_drop = [col for col in db_data.columns if 'Unnamed' in col]
db_data.drop(columns=cols_to_drop,inplace=True)

for facility in facilities:
    D.tdve['facilities_number'].ts[facility] = at.TimeSeries(data_years, 1, units='Number')
    D.tdve['facilities_number'].write_assumption = True
    for parameter in db_data.columns:
        D.tdve[parameter+'_baseline'].ts[facility] = at.TimeSeries(data_years, db_data.loc[facility,parameter])
        D.tdve[parameter+'_baseline'].write_assumption = True
        
D.save('books/carbomica_databook.xlsx')
    
#%% Step 3: generate empty progbooks in folder "templates/"
databook_name = 'books/carbomica_databook.xlsx'
P = at.Project(framework=F,databook=databook_name, do_run=False)
for facility in facilities:
    progbook_path = 'templates/carbomica_progbook_{}.xlsx'.format(facility)
    P.make_progbook(progbook_path,progs=interventions,data_start=data_years,data_end=data_years)
    
target_pars_overall = pd.read_excel('input_data.xlsx', sheet_name='emission targets', index_col='interventions')
cols_to_drop = [col for col in target_pars_overall.columns if 'Unnamed' in col]
target_pars_overall.drop(columns=cols_to_drop,inplace=True)

effects = pd.read_excel('input_data.xlsx', sheet_name='effect sizes', index_col='facilities')
cols_to_drop = [col for col in effects.columns if 'Unnamed' in col]
effects.drop(columns=cols_to_drop,inplace=True)

# Populate the progbooks that were just created and save the files to "books/"
D = at.ProjectData.from_spreadsheet(databook_name,framework=F) 
pb_costs = pd.read_excel('input_data.xlsx', sheet_name='unit costs', index_col='facilities') 
cols_to_drop = [col for col in pb_costs.columns if 'Unnamed' in col]
pb_costs.drop(columns=cols_to_drop,inplace=True) 
for facility in facilities:
    P = at.ProgramSet.from_spreadsheet(spreadsheet='templates/carbomica_progbook_{}.xlsx'.format(facility), framework=F, data=D, _allow_missing_data=True)
    for intervention in interventions:
        # Write in 'Program targeting' sheet
        P.programs[intervention].target_pops = [facility]
        P.programs[intervention].target_comps = ['facilities_number']
        
        # Write in 'Spending data' sheet
        P.programs[intervention].unit_cost = at.TimeSeries(assumption=pb_costs.loc[facility,intervention+'_cost'], units='$/person/year')
        P.programs[intervention].spend_data = at.TimeSeries(data_years,0, units='$/year') # make initial spending a small, negligible but non-zero number for optimisation initialisation
        P.programs[intervention].capacity_constraint = at.TimeSeries(units='people')
        P.programs[intervention].coverage = at.TimeSeries(units='people')
        
        # Write in 'Program effects' sheet
        target_pars = target_pars_overall.columns[target_pars_overall.loc[intervention]=='y'].tolist()
        for par in target_pars:
            effect = effects.loc[facility,intervention+'_effect']
            P.covouts[(par+'_mult', facility)] = at.programs.Covout(par=par+'_mult',pop=facility,cov_interaction='random',baseline=0,progs={intervention:effect})
    P.programs[intervention].spend_data = at.TimeSeries(data_years,0, units='$/year') # make initial spending a small, negligible but non-zero number for optimisation initialisation
    P.save('books/carbomica_progbook_{}.xlsx'.format(facility))  
