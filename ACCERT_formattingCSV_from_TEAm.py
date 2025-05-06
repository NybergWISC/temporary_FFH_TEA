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

## Account numbers

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

## Variables 

import importlib
import inspect
import ast

# Export all variables to CSV
def export_variables_to_csv(filename="variables.csv"):
    """Exports all variables in the current scope to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(["Variable Name", "Variable Value", "Variable Type"])
        # Get variables from current scope
        variables = globals().copy()
        # Remove built-in variables and the function itself from the dictionary
        to_remove = [name for name in variables if name.startswith('__') or name == export_variables_to_csv.__name__]
        for name in to_remove:
            del variables[name]
        # Write data rows
        for name, value in variables.items():
            writer.writerow([name, value, type(value).__name__])


# Find all variables and arguments in a certain function
def analyze_function(func):
    print(f"Function: {func.__name__}")

    # Arguments
    sig = inspect.signature(func)
    print("  Arguments:")
    for param in sig.parameters.values():
        print(f"    {param.name} (default={param.default})")

    # Local variables via AST
    print("  Local Variables:")
    source = inspect.getsource(func)
    tree = ast.parse(source)

    class LocalVarVisitor(ast.NodeVisitor):
        def __init__(self):
            self.local_vars = set()

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.local_vars.add(target.id)
            self.generic_visit(node)

        def visit_AnnAssign(
            self, node
        ):  # for annotated assignments (e.g. x: int = 1)
            if isinstance(node.target, ast.Name):
                self.local_vars.add(node.target.id)
            self.generic_visit(node)

    visitor = LocalVarVisitor()
    visitor.visit(tree)
    for var in sorted(visitor.local_vars):
        print(f"    {var}")

# Analyze each function for every object in the module
def analyze_module(module_name):
    mod = importlib.import_module(module_name)
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if obj.__module__ == module_name:
            analyze_function(obj)


# Example use
# analyze_module("your_module_name_here")
analyze_module("matthew_ex")

# Example Usage:
x = 10
y = "hello"
z = [1, 2, 3]
export_variables_to_csv()

print(formattedCopy)