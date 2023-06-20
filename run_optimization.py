import atomica as at
import numpy as np
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to optimize spending given a budget.
'''

facility_code = 'mt-darwin_hosp_ZW' # specify facility code
facility_name = 'Mt Darwin District Hospital, Zimbabwe' # specify facility name

# Atomica project definition
P = at.Project(framework='carbomica_framework.xlsx', databook='books/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2010 # simulation start year
P.settings.sim_end   = 2030 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('books/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year

# Baseline spending
instructions = at.ProgramInstructions(alloc=P.progsets[0], start_year=start_year)

# Adjustments (spending constraint for each program)
adjustments = [at.SpendingAdjustment(prog, start_year, 'abs', 0.0, 1e6) for prog in progset.programs.keys()]

# Measurables (objective function: minimize total emissions)
measurables = [at.MinimizeMeasurable('co2e_emissions_actual',[start_year,np.inf])]

# Loop over budgets
budgets = [2e3, 4e3, 8e3]
results_optimized = []
np.random.seed(4)

#%% Initialize solution with pso
for budget in budgets:
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending

    # Run optimization
    optimization = at.Optimization(name='default', method='pso', 
                                   adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions, optim_args={"maxiter": 10})
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)

    # Compile results
    opt_name = '${}k'.format(budget/1e3)
    result_optimized.name = opt_name
    results_optimized.append(result_optimized)

ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation
allocation_initial, _ = ut.write_alloc_excel(P, results_optimized, 'results/optimized_allocation_coverage.xlsx')

#%% Refine optimization with ASD
results_optimized = []
for budget in budgets:
    opt_name = '${}k'.format(budget/1e3)
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
    adjustments = [at.SpendingAdjustment(prog, start_year, initial=allocation_initial[opt_name][progset.programs[prog].label]) for prog in progset.programs.keys()]
    
    # Run optimization
    optimization = at.Optimization(name='default', method='asd', 
                                   adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)

    # Compile results
    result_optimized.name = opt_name
    results_optimized.append(result_optimized)
    
ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation
ut.write_alloc_excel(P, results_optimized, 'results/optimized_allocation_coverage.xlsx')
