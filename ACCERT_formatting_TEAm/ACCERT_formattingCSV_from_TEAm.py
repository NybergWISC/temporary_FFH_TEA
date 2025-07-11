import csv
import numpy as np
import sys
import pandas as pd
# For the Variables and Functions
import ast
import csv
from typing import Optional
import re

# Class for applying AST to a python script and getting variable/function data
class CodeAnalyzer(ast.NodeVisitor):

    ind_iter=0
    func_iter=0

    def __init__(self):
        self.records = []

    def visit_FunctionDef(self, node):
        global ind_var_iter
        args = node.args
        arg_defaults = [None] * (len(args.args) - len(args.defaults)) + args.defaults
        for arg, default in zip(args.args, arg_defaults):
            self.ind_iter=self.ind_iter+1
            self.records.append({
                "Type": "function argument",
                "ind":self.ind_iter,
                "var_name": arg.arg,
                "var_description": "",
                "var_value": self._safe_eval(default),          
                "var_unit": "TODO",
                "var_alg": "TODO",
                "var_need": "TODO",
                "algs_using_var": node.name,
                "v_linked":""
            })
        
        ["ind", "alg_name", "alg_description", "alg_python", "alg_formulation", "alg_units", "variables", "constants"]
        self.func_iter=self.func_iter+1
        if "Account" in node.name or "account" in node.name:
            description_text = re.sub("(?i)account", "", node.name).replace("_","")
            self.records.append({
                "Type": "function",
                "ind":self.func_iter,
                "alg_name": node.name,
                "alg_for":"", # v or c based on variable vs overall code
                "alg_description": f"Account {description_text} Rollup",
                "alg_python": node.name,
                "alg_formulation": "TODO",
                "alg_units": "TODO",
                "variables": ", ".join(ast.unparse(node.args).split(",")), # TODO should also include variables within the function
                "constants": "TODO", # Needs to have the constants defined in that 
                "Dependencies": ", ".join(sorted({a.arg for a in args.args}))
            })
        else:
            self.records.append({
                "Type": "function",
                "ind":self.func_iter,
                "alg_name": node.name,
                "alg_for":"", # v or c based on variable vs overall code
                "alg_description": "".join(str(ast.get_docstring(node)).strip().split("\n")[0:1]) or "",
                "alg_python": node.name,
                "alg_formulation": "TODO",
                "alg_units": "TODO",
                "variables": ", ".join(ast.unparse(node.args).split(",")), # TODO should also include variables within the function
                "constants": "TODO", # Needs to have the constants defined in that 
                "Dependencies": ", ".join(sorted({a.arg for a in args.args}))
            })
        self.generic_visit(node)

    def visit_Assign(self, node):
        value_repr = self._safe_eval(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.ind_iter=self.ind_iter+1
                self.records.append({
                    "Type": type(value_repr).__name__,
                    "ind":self.ind_iter,
                    "var_name": target.id,
                    "var_description": type(value_repr).__name__,
                    "var_value": value_repr,
                    "var_unit": "TODO",
                    "var_alg": self._get_dependencies(node.value),
                    "var_need": "TODO",
                    "algs_using_var": "TODO",
                    "v_linked":""
                })

    def _safe_eval(self, node: Optional[ast.AST]):
        try:
            if node is not None:
                return ast.literal_eval(node)
        except Exception:
            return ""
        return ""

    def _get_dependencies(self, node: ast.AST):
        # Traverse nodes and collect variable names
        return ", ".join(sorted({n.id for n in ast.walk(node) if isinstance(n, ast.Name)}))

# Run the ast and the analyzer to parse a python script, then write the variables and 
# Algorithms to a csv in an ACCERT format
def extract_metadata_to_csv(filepath: str, output_var_csv: str, output_func_csv:str):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=filepath)

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    # print(analyzer.records)

    fieldnames = ["ind", "var_name", "var_description", "var_value", "var_unit", "var_alg", "var_need", "algs_using_var", "v_linked"]
    with open(output_var_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in analyzer.records:
            if record["Type"] is not ("function"):
                writer.writerow(record)

    fieldnames = ["ind", "alg_name", "alg_description", "alg_python", "alg_formulation", "alg_units", "variables", "constants"]
    with open(output_func_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in analyzer.records:
            if record["Type"] is ("function"):
                # print(record)
                writer.writerow(record)


# Takes in the txt output from TEAm and creates the formatted 
# ACCERT first page (accounts) 
# TODO implement the variables column (use AST?)
def formatAccounts(TEAm_outputs_path):

    # Reads data from a CSV file into a DataFrame
    path=TEAm_outputs_path
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
        # variables in all of the subaccounts

    # print(formattedCopy)
    return formattedCopy


# Takes in the core python script and outputs the variables
def formatVariables(core_python_path):

    # TODO implement
    print("not implemented")


# Takes in the core python script and outputs the functions
def formatFunctions(core_python_path):
    # TODO implement
    print("not implemented")


### MAIN ###

formattedAccountsInit = formatAccounts(TEAm_outputs_path=sys.argv[1])
extract_metadata_to_csv(filepath="core_editedForNeeds.py", output_var_csv="vars.csv", output_func_csv="func.csv")

print(formattedAccountsInit)