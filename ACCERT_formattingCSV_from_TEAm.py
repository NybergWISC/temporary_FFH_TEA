import csv
import numpy as np
import sys
import pandas as pd

# Reads data from a CSV file into a DataFrame
path=sys.argv[1]
dataLoadTxt = pd.read_csv(path)

# Prints the first 5 rows of the DataFrame
print(dataLoadTxt.head())
# print(read_csv_to_string(path))
coaNumRows, coaNumCols = dataLoadTxt.shape
# Copy of array that will be edited

formattedCopy = [['' for _ in range(12)] for _ in range(coaNumRows+1)]

# Set up headers
formattedCopy[0] = ["ind", "code_of_account", "account_description", "total_cost (M$)","total_cost ($)", "level", "prn", "supaccount", "alg_name", "fun_unit", "variables", "algno"]


### GENERAL FORMATTING VARIABLES ### 

# Account numbers


for account_iter in range(coaNumRows):
    # Adds the ind numbers in
    formattedCopy[account_iter+1][0] = account_iter+1

    # Formatting account numbers to remove . and add the c in front
    formattedTemp = f"c{dataLoadTxt['Account Number'].values[account_iter]}".replace('.','')
    if formattedTemp[-1] == '0':
        formattedTemp=formattedTemp[0:-1]
    formattedCopy[account_iter+1][1] = formattedTemp

    # use the same for alg_name 
    formattedCopy[account_iter+1][8] = f"ac{formattedTemp}"

    # Account names (descriptions in ACCERT)
    formattedTemp = f"{dataLoadTxt['Account Name'].values[account_iter]}".replace(' ', '_')
    formattedCopy[account_iter+1][2] = formattedTemp

    # Loading and formatting costs for both M$ and $ columns
    costMillionDollars = dataLoadTxt['Cost'].values[account_iter]
    formattedCopy[account_iter+1][3] = f"{costMillionDollars}"
    formattedTemp = f"${float(costMillionDollars)*10**6}"
    formattedCopy[account_iter+1][4] = formattedTemp

    # Level = level
    formattedCopy[account_iter+1][5] = f"{dataLoadTxt['Level'].values[account_iter]}"

    # prn TODO ASK
    formattedCopy[account_iter+1][6] = "TODO"

    # supaccount, take one off the original
    formattedTemp = f"{dataLoadTxt['Account Number'].values[account_iter]}".replace('.','')
    if formattedTemp[-1] == '0':
        formattedCopy[account_iter+1][7]=""
    else:
        formattedCopy[account_iter+1][7]=f"{formattedTemp[0:-1]}"

    # 9th column alg_name implemented above

    # units (all millions)
    formattedCopy[account_iter+1][9]="million"

    # variables TODO

    

print(formattedCopy)