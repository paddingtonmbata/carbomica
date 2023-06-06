import atomica as at
import pandas as pd
import numpy as np
from utils import facilities, interventions
import os
if not os.path.exists('books'): os.makedirs('books')

'''
The script to create fresh databooks and progbooks. Will overwrite existing 
files in Databooks and Progbooks folders.
'''

data_years = [2023]
prog_years = np.arange(2024,2031)

F = at.ProjectFramework('files/carbomica_framework.xlsx')
D = at.ProjectData.new(framework=F, tvec=data_years, pops=facilities, transfers=0)

db_data = pd.read_excel('input_data.xlsx', sheet_name='data', index_col='facilities')
pb_costs = pd.read_excel('input_data.xlsx', sheet_name='unit_costs', index_col='facilities')  

for facility in facilities.keys():
    for parameter in db_data.columns:
        D.tdve[parameter].ts[facility] = at.TimeSeries(data_years, db_data.loc[facility,parameter], units='Number')
        D.tdve[parameter].write_assumption = True
    P = at.ProgramSet.from_spreadsheet(spreadsheet='files/carbomica_progbook_{}.xlsx'.format(facility), framework=F, data=D, _allow_missing_data=True)
    for intervention in interventions.keys():
        P.programs[intervention].unit_cost = at.TimeSeries(assumption=pb_costs.loc[facility,intervention], units='$/person/year')
        P.programs[intervention].spend_data = at.TimeSeries(prog_years[0],1e-16, units='$/year') # make it a small, negligible but non-zero number for optimisation
        P.programs[intervention].capacity_constraint = at.TimeSeries(assumption=1, units='people')
        P.programs[intervention].coverage = at.TimeSeries(assumption=1, units='people/year')
    P.save('books/carbomica_progbook_{}.xlsx'.format(facility))    

D.save('books/carbomica_databook.xlsx')