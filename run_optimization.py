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
P = at.Project(framework='files/carbomica_framework.xlsx', databook='files/carbomica_databook.xlsx',do_run=False)

P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = 2010 # simulation start year
P.settings.sim_end   = 2030 # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('files/carbomica_progbook_{}.xlsx'.format(facility_code))

start_year = 2024 # programs start year

# Baseline spending
instructions = at.ProgramInstructions(alloc=P.progsets[0], start_year=start_year)

# Adjustments (spending constraint for each program)
adjustments = [at.SpendingAdjustment(prog, start_year, 'abs', 0.0, np.inf) for prog in progset.programs.keys()]

# Measurables (objective function: minimize total emissions)
measurables = [at.MinimizeMeasurable('total_emissions',start_year)]

# Loop over budgets
budgets = [2e6, 5e6, 10e6]
results_optimized = []

for budget in budgets:
    constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending

    # Run optimization
    optimization = at.Optimization(name='default', maxiters=100,
                                   adjustments=adjustments, measurables=measurables, constraints=constraints)
    optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
    result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)

    # Compile results
    opt_name = '${}M'.format(budget/1e6)
    result_optimized.name = opt_name
    results_optimized.append(result_optimized)

ut.calc_emissions(results_optimized,start_year,facility_code,file_name='emissions_optimized_{}'.format(facility_code))
ut.calc_allocation(results_optimized,file_name='allocation_optimized_{}'.format(facility_code)) # allocation


