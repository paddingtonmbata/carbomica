import atomica as at
import pandas as pd
from utils import facilities, interventions
'''
Script to generate a databook and progbook.
'''
# Load Framework
F = at.ProjectFramework('carbomica_framework.xlsx') 

#%% Step 1: generate databook
data_years = 2023 # years for input data
databook_name = 'books/carbomica_databook.xlsx' # databook name

# Option to generate empty databook, or generate and populate databook

gen_databook = False # 'True' if generating databooks, 'False' if generating progbooks

if gen_databook :
    D = at.ProjectData.new(F,data_years,pops=facilities,transfers=0)
    D.save(databook_name)

pop_databook = False # True if populating databook

if pop_databook : 
    D = at.ProjectData.new(framework=F, tvec=data_years, pops=facilities, transfers=0)
    db_data = pd.read_excel('input_data.xlsx', sheet_name='data', index_col='facilities')
    for facility in facilities.keys():
        for parameter in db_data.columns:
            D.tdve[parameter].ts[facility] = at.TimeSeries(data_years, db_data.loc[facility,parameter], units='Number')
            D.tdve[parameter].write_assumption = True
    D.save(databook_name)
    
#%% Step 2: generate program books after filling in databook (note that progbook will not generate if data cells in databook are empty)
gen_progbook = False # 'True' if generating progbooks, 'False' if generating databooks

if gen_progbook :
    P = at.Project(framework=F,databook=databook_name, do_run=False)
    for facility in facilities.keys():
        progbook_path = 'files/carbomica_progbook_{}.xlsx'.format(facility)
        P.make_progbook(progbook_path,progs=interventions,data_start=data_years,data_end=data_years)
        
# In order to populate the progbook, the empty progbooks that were just created (in files) are read in first
pop_progbook = True

if pop_progbook:
    D = at.ProjectData.from_spreadsheet(databook_name,framework=F) 
    pb_costs = pd.read_excel('input_data.xlsx', sheet_name='unit_costs', index_col='facilities')  
    for facility in facilities.keys():
        P = at.ProgramSet.from_spreadsheet(spreadsheet='files/carbomica_progbook_{}.xlsx'.format(facility), framework=F, data=D, _allow_missing_data=True)
        for intervention in interventions.keys():
            P.programs[intervention].unit_cost = at.TimeSeries(assumption=pb_costs.loc[facility,intervention], units='$/person/year')
            P.programs[intervention].spend_data = at.TimeSeries(data_years,0, units='$/year') # make it a small, negligible but non-zero number for optimisation
            P.programs[intervention].capacity_constraint = at.TimeSeries(units='people')
            P.programs[intervention].coverage = at.TimeSeries(units='people')
        P.programs[intervention].spend_data = at.TimeSeries(data_years,1e-16, units='$/year') # make it a small, negligible but non-zero number for optimisation
        P.save('books/carbomica_progbook_{}.xlsx'.format(facility))  