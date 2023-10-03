import atomica as at
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to run a scenario where spending on interventions is specified.
'''

facility_code = 'mb_hosp' # specify facility code

# Atomica project definition
P = at.Project(framework='carbomica_framework.xlsx', databook='books/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2022 # simulation start year
P.settings.sim_end   = 2025 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('books/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year
# investment = [300,600] # 
# result = []
# for invest in investment:
#     # Option 1: increase investments for all interventions
#     # budget_scenario = {prog: at.TimeSeries(start_year,invest) for prog in progset.programs}    
    
#     # Option 2: increase investments for specific interventions
#     budget_scenario = {'electric_cars': at.TimeSeries(start_year,invest)}
        
#     instructions = at.ProgramInstructions(start_year=start_year, alloc=budget_scenario) # define program instructions
#     result_budget = P.run_sim(P.parsets[0],progset=P.progsets[0], progset_instructions=instructions, result_name='${}'.format(invest)) # run budget scenario
#     result_budget.export_raw('results/{}_budget_raw.xlsx'.format(invest))
#     result.append(result_budget)
investment = 1e3
results_scenario = []

for prog in progset.programs:
    budget_scenario = {prog_all: 0 for prog_all in progset.programs}
    budget_scenario[prog] = investment
    instructions = at.ProgramInstructions(start_year=start_year, alloc=budget_scenario) # define program instructions
    result_budget = P.run_sim(parset='default',progset=P.progsets[0], progset_instructions=instructions, result_name=progset.programs[prog].label) # run budget scenario
    results_scenario.append(result_budget)
    
# Calculate emissions and allocation
ut.calc_emissions(results_scenario,start_year,facility_code,file_name='emissions_budget_scen_{}'.format(facility_code),title='CO2e emissions - fixed budget ($1,000.0)')
# ut.calc_allocation(results_scenario,file_name='allocation_    budget_scen_{}'.format(facility_code)) # allocation

