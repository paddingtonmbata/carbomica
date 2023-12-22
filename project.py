import atomica as at
from books import generate_books

## Time frame of simulation
start_year = 2024 # MODIFY AS NEEDED
end_year = start_year + 5 # MODIFY AS NEEDED

# Input data sheet file name (and path if applicable)
input_data_sheet = 'input_data_example.xlsx' # MODIFY AS NEEDED

# Generate framework, databook and progbook and return facility code name
facility_code = generate_books(input_data_sheet, start_year, end_year)

# Atomica project definition
P = at.Project(framework = 'books/carbomica_framework_{}.xlsx'.format(facility_code), 
               databook = 'books/carbomica_databook_{}.xlsx'.format(facility_code), 
               do_run = False)

# Projection settings
P.settings.sim_dt    = 1 # simulation timestep
P.settings.sim_start = start_year # simulation start year
P.settings.sim_end   = end_year # simulation end year

# Load program and define variables for program runs
progset = P.load_progbook('books/carbomica_progbook_{}.xlsx'.format(facility_code))
