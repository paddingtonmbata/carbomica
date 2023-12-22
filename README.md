# carbomica
## Name
CARBOMICA (CARBOn MItigation Tool for HealthCAre FAcilities​)

## Description
CARBOMICA is a resource allocation tool for carbon mitigation in healthcare facilities, developed by the Burnet Institute and HIGH Horizons Consortium.

## Requirements
Atomica

## Modifiable scripts
### `project.py`
Script that define the Atomica project based on the `input_data.xlsx` spreadsheet.

### `run_main.py`
Script to run the three main scenarios:
- `coverage_scenario`: Run a scenario where interventions are individually fully covered.
- `budget_scenario`: Run a scenario where spending on interventions are individually specified.
- `optimization`: Optimize spending allocation on interventions by minizing emissions for a set total budget.

### `run_program_checks.py`
Script to check output of programs under certain coverage and budget conditions.

## Non-Modifiable scripts
### `utils.py`
Module containing utility functions (plotting and results functions).

### `books.py`
Function to generate the framework, databook and progbook for the study site.

### `scenarios.py`
Function to run the scenarios.

### `templates/carbomica_framework_template.xlsx`
Framework template used to generate site-specific framework.

### `templates/input_data_template.xlsx`
`input_data.xlsx` spreadsheet template to be copied and modified locally.