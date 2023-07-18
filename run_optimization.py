import atomica as at
import numpy as np
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to minimize emissions and optimize spending allocation for a set total budget.
'''

facility_code = 'mt-darwin_hosp_ZW' # specify facility code

# Atomica project definition
P = at.Project(framework='carbomica_framework.xlsx', databook='books/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2022 # simulation start year
P.settings.sim_end   = 2025 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('books/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year

# Baseline spending
instructions = at.ProgramInstructions(alloc=P.progsets[0], start_year=start_year)

# Adjustments (no spending constraint on any intervention)
adjustments = [at.SpendingAdjustment(prog, start_year, 'abs', 0.0, 1e6) for prog in progset.programs]

# Measurables (objective function: minimize total emissions)
measurables = [at.MinimizeMeasurable('co2e_emissions',start_year)]

# Set random seed
np.random.seed(4)

#%% Initialize solution with pso
# Loop over budgets
budgets = [0.5e6, 1e6, 5e6]
results_optimized = []
for budget in budgets:
    result_name = '${}m'.format(budget/1e6)
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending

    # Run optimization
    optimization = at.Optimization(name='default', method='pso', 
                                    adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions, optim_args={"maxiter": 5})
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions,result_name=result_name)

    # Compile results
    results_optimized.append(result_optimized)

ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation
allocation_initial, _ = ut.write_alloc_excel(progset, results_optimized, start_year, 'results/optimized_allocation_coverage.xlsx')

#%% Refine optimization with ASD
results_optimized = []
for budget in budgets:
    result_name = '${}m'.format(budget/1e6)
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
    adjustments = [at.SpendingAdjustment(prog, start_year, initial=allocation_initial[result_name][progset.programs[prog].label]) for prog in progset.programs]
    
    # Run optimization
    optimization = at.Optimization(name='default', method='asd', 
                                    adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions,result_name=result_name)

    # Compile results
    results_optimized.append(result_optimized)
    
ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
ut.calc_emissions_all(results_optimized,start_year,facility_code,file_name='emissions_optimized_all_{}'.format(facility_code))
ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation
ut.write_alloc_excel(progset, results_optimized, start_year, 'results/optimized_allocation_coverage.xlsx')


#%% ASD only

# # Loop over budgets
# budgets = [0.5e5, 1e5, 5e5]
# results_optimized = []
# for budget in budgets:
#     result_name = '${}m'.format(budget/1e6)
#     constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending

#     # Run optimization
#     optimization = at.Optimization(name='default', adjustments=adjustments, measurables=measurables, constraints=constraints)
#     optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
#     result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions,result_name=result_name)

#     # Compile results
#     results_optimized.append(result_optimized)

# ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
# ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation
# allocation_initial, _ = ut.write_alloc_excel(progset, results_optimized, start_year, 'results/optimized_allocation_coverage.xlsx')
