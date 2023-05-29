# prison-nsp
## Name
CARBOMICA

## Description
CARBOn MItigation Tool for HealthCAre FAcilities​

## Requirements
Atomica

## Usage
### `generate_books.py`
Script to generate a databook and progbook.

### `run_program_checks.py`
Script to check output of programs under certain coverage and budget conditions.
E.g.: It can be useful to set intervention effects to 0 (perfect effect), the same unit_cost for all interventions, and check that spending (0.5 x unit_cost) or (1 x unit_cost) produces the correct outputs (a program effect of 0.5 or 0, respectively).

### `run_coverage_scenario.py`
Script to run a scenario where coverage of interventions is specified.

### `run_budget_scenario.py`
Script to run a scenario where spending on interventions is specified.

### `run_optimisation.py`
Script to optimize the allocation of funds.

### `utils.py`
Module containing utility functions.