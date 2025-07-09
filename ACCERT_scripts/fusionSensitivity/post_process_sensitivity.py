import numpy as np
import os
import matplotlib.pyplot as plt

### Variables ###

variable_outputs = []
all_vars = []
high_worth_vars = []

# making a combined array for the superconductor unit cost rows
sc_rows = []
# Some error tracking
errors = []
successfulRuns = []
numFails = 0
numSuccess = 0

# The runs from the original
runs = {
    "half" : 0.5,
    "original" : 1.0,    
    "zero" : 0.0,
    "double": 2.0,
    "tenX" : 10.0
}

runs_output =  {
    "half" : [],
    "original" : [],    
    "zero" : [],
    "double": [],
    "tenX" : []
}

runs_highCost_output =  {
    "half" : [],
    "original" : [],    
    "zero" : [],
    "double": [],
    "tenX" : []
}

# Function to get account outputs and direct costs from .out ACCERT outputs
def stripOutput(run_key, variable_name, model="_stell"):
    updatedAccounts = []
    inResults = False
    with open(f"sensitivity_outs{model}/{variable_name}/output_{variable_name}_{run_key}.out", 'r') as sense_output_file:
        lines = sense_output_file.readlines()
        for line in lines:
            if "Generating results table for review" in line:
                inResults = True
            if inResults:
                if "Updated" in line:
                    formLine = [x.strip().replace(",","") for x in line.split("|")]
                    updatedAccounts.append(formLine)
                if "direct" in line:
                    direct_cost = float(formLine[3])
                    # print(f"Account {formLine[1]} ({formLine[2]}) updated to M${formLine[3]}")
    return direct_cost, updatedAccounts

# Strip values and apply outputs to arrays for any one variable and set of runs 
def generalVariable(runs,variable,model="_stell"):
    global all_vars
    global numFails, numSuccess
    global runs_output, runs_highCost_output
    global successfulRuns, errors
    try:
        for run_key in runs.keys():
            all_vars.append(variable)
            direct_cost, account_info = stripOutput(run_key, variable, model=model)
            runs_output[run_key].append(direct_cost)
            if direct_cost > 6200:
                high_worth_vars.append(variable)
                runs_highCost_output[run_key].append(direct_cost)
            variable_outputs.append(account_info)
    except Exception as e:
        errors.append(str(e))
        numFails=numFails+1
    else:
        numSuccess=numSuccess+1
        successfulRuns.append(variable)

fusion_data = np.loadtxt(fname='reducedFusionSheet_unitCosts.csv', delimiter="|", dtype=str)

# Nested loops of doom. Do all runs for all lines
for rows in fusion_data[1:]:
    if "ucsc_" in rows[1]:
            sc_rows.append(rows)
    generalVariable(runs=runs, variable=rows[1], model="_tok")

generalVariable(runs=runs, variable="combinedSC")


print(f"Number of successes: {numSuccess}")
print(f"Number of failures: {numFails}")

# print(high_worth_vars)
# print(runs_output["tenX"])
# print(all_vars)

plt.bar(high_worth_vars, runs_highCost_output["tenX"])
plt.show()

plt.bar(successfulRuns, runs_output["tenX"])
plt.show()