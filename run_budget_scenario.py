import atomica as at
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to run a scenario where spending on interventions is specified.
'''

facility_code = 'mt-darwin_hosp_ZW' # specify facility code
facility_name = 'Mt Darwin District Hospital, Zimbabwe' # specify facility name

# Atomica project definition
P = at.Project(framework='files/carbomica_framework.xlsx', databook='files/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2010 # simulation start year
P.settings.sim_end   = 2030 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('files/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year
investment = 1e5 # initial investment (can be a list)

# Option 1: increase investments for all interventions
budget_scenario = {prog: at.TimeSeries(start_year,investment) for prog in progset.programs.keys()}    

# Option 2: increase investments for specific interventions
# budget_scenario = {'energy_led': at.TimeSeries(start_year,investment),
#                      'electric_cars': at.TimeSeries(start_year,investment)
#                      }
    
instructions = at.ProgramInstructions(start_year=start_year, alloc=budget_scenario) # define program instructions
result_budget = P.run_sim(P.parsets[0],progset=P.progsets[0], progset_instructions=instructions, result_name=facility_name) # run budget scenario

# Calculate emissions and allocation
ut.calc_emissions([result_budget],start_year,facility_code,file_name='emissions_budget_scen_{}'.format(facility_code))
ut.calc_allocation([result_budget],file_name='allocation_budget_scen_{}'.format(facility_code)) # allocation

