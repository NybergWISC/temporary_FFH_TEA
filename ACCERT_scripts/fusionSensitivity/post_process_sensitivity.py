import numpy as np
import os
import matplotlib.pyplot as plt

def stripOutput(run_key, rows, model="_tok"):
    updatedAccounts = []
    inResults = False
    with open(f"sensitivity_outs{model}/{rows[1]}/output_{rows[1]}_{run_key}.out", 'r') as sense_output_file:
        lines = sense_output_file.readlines()
        for line in lines:
            if "Generating results table for review" in line:
                inResults = True
            # if rows[1] in line and "|" in line:
                # print(line)
            if inResults:
                if "Updated" in line:
                    formLine = [x.strip() for x in line.split("|")]
                    updatedAccounts.append(formLine)
                if "direct" in line:
                    direct_cost = formLine[3]
                    # print(f"Account {formLine[1]} ({formLine[2]}) updated to M${formLine[3]}")
    return direct_cost, updatedAccounts


fusion_data = np.loadtxt(fname='reducedFusionSheet_unitCosts.csv', delimiter="|", dtype=str)

run_dir = os.getcwd()

indices = fusion_data[1:,0]
var_names = fusion_data[1:,1]
values = fusion_data[1:,2]
units = fusion_data[1:,3]

variable_outputs = []
plotting_by_var = []

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

# Nested loops of doom. Do all runs for all lines
for rows in fusion_data[1:]:
    runs_output = {}
    print(f"{rows[1]}")
    if "ucsc_" in rows[1]:
        sc_rows.append(rows)
    try:
        for run_key in runs.keys():
            direct_cost, account_info = stripOutput(run_key, rows)
            runs_output.update({run_key, direct_cost})
            variable_outputs.append(account_info)  
        plotting_by_var.append(runs_output)
    except Exception as e:
        errors.append(str(e))
        print(e)
        numFails=numFails+1
    else:
        numSuccess=numSuccess+1
        successfulRuns.append(rows[1])

print(f"Number of successes: {numSuccess}")
print(f"Number of failures: {numFails}")

print(f"{len(successfulRuns)} successful runs. Variables: {successfulRuns}")

plt.bar(fusion_data[1:][1], (plotting_by_var[:])["half"])