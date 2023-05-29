import atomica as at
import numpy as np
'''
Script to generate a databook and progbook.
'''
# Load Framework
F = at.ProjectFramework('files/carbomica_framework.xlsx') 

# Facilities (modify as needed)
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