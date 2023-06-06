import atomica as at
from utils import facilities, interventions
'''
Script to generate a databook and progbook.
'''
# Load Framework
F = at.ProjectFramework('files/carbomica_framework.xlsx') 

#%% Step 1: generate databook
data_years = 2023 # years for input data
databook_name = 'files/carbomica_databook.xlsx' # databook name
gen_databook = False # 'True' if generating databooks, 'False' if generating progbooks

if gen_databook :
    D = at.ProjectData.new(F,data_years,pops=facilities,transfers=0)
    D.save(databook_name)

#%% Step 2: generate program books after filling in databook (note that progbook will not generate if data cells in databook are empty)
nb_prog = 8 # number of programs
gen_progbook = True # 'True' if generating progbooks, 'False' if generating databooks

if gen_progbook :
    P = at.Project(framework=F,databook=databook_name, do_run=False)
    for facility in facilities.keys():
        progbook_path = 'files/carbomica_progbook_{}.xlsx'.format(facility)
        P.make_progbook(progbook_path,progs=interventions,data_start=data_years,data_end=data_years)