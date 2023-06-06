import atomica as at
import numpy as np
from utils import facilities, interventions
'''
Script to generate a databook and progbook.
'''
# Load Framework
F = at.ProjectFramework('files/carbomica_framework.xlsx') 

#%% Step 1: generate databook
data_years = [2022,2023] # years for input data
databook_name = 'files/carbomica_databook.xlsx' # databook name
gen_databook = False # 'True' if generating databooks, 'False' if generating progbooks

if gen_databook :
    D = at.ProjectData.new(F,np.arange(data_years[0],data_years[1]),pops=facilities,transfers=0)
    D.save(databook_name)

#%% Step 2: generate program books after filling in databook (note that progbook will not generate if data cells in databook are empty)
prog_years = [2024,2030] # program years
nb_prog = 8 # number of programs
gen_progbook = True # 'True' if generating progbooks, 'False' if generating databooks

if gen_progbook :
    P = at.Project(framework=F,databook=databook_name, do_run=False)
    for facility in facilities.keys():
        progbook_path = 'files/carbomica_progbook_{}.xlsx'.format(facility)
        P.make_progbook(progbook_path,progs=interventions,data_start=prog_years[0],data_end=prog_years[1])