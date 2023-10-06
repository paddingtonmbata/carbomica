import atomica as at
import numpy as np
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')
'''
Script to minimize emissions and optimize spending allocation for a set total budget.
'''

facility_code = 'AKHS_Mombasa' # specify facility code

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
adjustments = [at.SpendingAdjustment(prog, start_year, 'abs', 0.0, 10e6) for prog in progset.programs]

# Measurables (objective function: minimize total emissions)
measurables = [at.MinimizeMeasurable('co2e_emissions',start_year)]

# Set random seed
np.random.seed(4)

#%% Run optimization

# Initialize with PSO
budgets = [20e3, 50e3, 100e3]
result_names = ['$20,000', '$50,000', '$100,000']
results_optimized = []
for budget, name in zip(budgets, result_names):
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
    # Run optimization
    optimization = at.Optimization(name='default', method='pso', 
                                   adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions, optim_args={"maxiter": 10})
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)
    
    # Compile results
    result_optimized.name = name
    results_optimized.append(result_optimized)

# Extract spending to use as initial conditions in ASD loop
allocation_initial, _ = ut.write_alloc_excel(progset, results_optimized, start_year, print_results=False)

# Refine optimization with ASD
results_optimized = []
for budget, name in zip(budgets, result_names):
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
    adjustments = [at.SpendingAdjustment(prog, start_year, initial=allocation_initial[name][progset.programs[prog].label]) for prog in progset.programs.keys()]
    
    # Run optimization
    optimization = at.Optimization(name='default', method='asd', 
                                   adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)
    
    # Compile results
    result_optimized.name = name
    results_optimized.append(result_optimized)

# Plot and save emissions    
ut.calc_emissions(results_optimized,start_year,facility_code,file_name='optimization_Emissions_{}'.format(facility_code))

# Plot budget allocation
ut.calc_allocation(results_optimized,file_name='optimization_Budget_Allocation_{}'.format(facility_code)) # allocation

# Save budget allocation and interventions coverage
ut.write_alloc_excel(progset, results_optimized, start_year,file_name='results/optimization_Budget_Allocation_{}.xlsx'.format(facility_code))
