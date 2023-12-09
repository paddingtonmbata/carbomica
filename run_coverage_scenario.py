import atomica as at
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to run a scenario where coverage on interventions is specified.
'''

facility_code = 'AKHS_Mombasa' # specify facility code

# Atomica project definition
P = at.Project(framework='carbomica_framework.xlsx', databook='books/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2023 # simulation start year
P.settings.sim_end   = 2024+5 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('books/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year
coverage = [1] # 
result = []
# Option 1: increase coverage for all interventions
# for cov in coverage:
#     # coverage_scenario = {prog: at.TimeSeries(start_year,cov) for prog in progset.programs}
        
#     # Option 2: increase coverage for specific interventions
#     coverage_scenario = {'electric_cars': at.TimeSeries(start_year,cov),
#                           }
        
#     instructions = at.ProgramInstructions(start_year=start_year, coverage=coverage_scenario) # define program instructions
#     result_coverage = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=instructions, result_name='{:.0f}%'.format(cov*100)) # run budget scenario
#     result_coverage.export_raw('results/{}_coverage_raw.xlsx'.format(cov*100))
#     result.append(result_coverage)
results_scenario = []

for prog in progset.programs:
    coverage_scenario = {prog_all: 0 for prog_all in progset.programs}
    coverage_scenario[prog] = 1
    instructions = at.ProgramInstructions(start_year=start_year, coverage=coverage_scenario) # define program instructions
    result_budget = P.run_sim(parset='default',progset=P.progsets[0], progset_instructions=instructions, result_name=progset.programs[prog].label) # run budget scenario
    results_scenario.append(result_budget)
    
# Calculate emissions and allocation
df=ut.calc_emissions(results_scenario,start_year,facility_code,file_name='coverage_scenario_Emissions_{}'.format(facility_code),title='CO2e emissions - full coverage')
