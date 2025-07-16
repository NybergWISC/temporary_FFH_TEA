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
    arg_iter=0
    func_iter=0
    account_iter=0
    account_variables={}
    used_vars=[]

    def __init__(self):
        self.records = []

    def visit_FunctionDef(self, node):
        global ind_var_iter
        args = node.args
        arg_defaults = [None] * (len(args.args) - len(args.defaults)) + args.defaults
        for arg, default in zip(args.args, arg_defaults):
            self.arg_iter=self.arg_iter+1
            self.records.append({
                "Type": "function argument",
                "ind":self.arg_iter,
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
        ['ind', 'code_of_account', 'account_description', 'total_cost (M$)', 'total_cost ($)', 'level', 'prn', 'supaccount', 'alg_name', 'fun_unit', 'variables', 'algno']
        self.func_iter=self.func_iter+1
        # Special handling for account rollup functions
        if "Account" in node.name: #  or "account" in node.name:
            self.account_iter=self.account_iter+1
            description_text = re.sub("(?i)account", "", node.name).replace("_","")
            # Account rollup function
            self.records.append({
                "Type": "function",
                "ind":self.func_iter,
                "alg_name": node.name,
                "alg_for":"c", # v or c based on variable vs overall code
                "alg_description": f"Account {description_text} Rollup",
                "alg_python": node.name,
                "alg_formulation": "TODO",
                "alg_units": "million",
                "variables": ", ".join(ast.unparse(node.args).split(",")), # TODO should also include variables within the function
                "constants": "TODO", # Needs to have the constants defined in that 
                "Dependencies": ", ".join(sorted({a.arg for a in args.args}))
            })
            # Adds account variables to a dictionary for the TEAm-specific output parser to use
            self.account_variables.update({self.account_iter:", ".join(ast.unparse(node.args).split(","))})
            # Sorts out some strange non-numeric named accounts, may adjust to include later
            if "2" in node.name:
                # Account entry TODO WIP
                self.records.append({
                    "Type": "account",
                    "ind":self.account_iter,
                    "code_of_account":description_text.replace("C",""),
                    "account_description": f"TODO",
                    "total_cost (M$)": "TODO",
                    "total_cost": "TODO",
                    "level": len(description_text.replace("C","")),
                    "prn": "TODO",
                    "supaccount":description_text[:-1],
                    "alg_name": node.name,
                    "fun_unit": "million",
                    "variables": ", ".join(ast.unparse(node.args).split(",")), # TODO should also include variables within the function
                    "Dependencies": ", ".join(sorted({a.arg for a in args.args}))
                })
                
        else:
            # TODO add check to make sure functions aren't repeated
            self.records.append({
                "Type": "function",
                "ind":self.func_iter,
                "alg_name": node.name,
                "alg_for":"v", # v or c based on variable vs overall code
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
                if target.id not in self.used_vars:
                    self.used_vars.append(target.id)
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
def extract_metadata_to_csv(filepath: str, output_var_csv="vars.csv", output_func_csv="func.csv", output_acc_csv="accounts.csv", output_arg_csv="args.csv"):
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
            if record["Type"] != ("function") and record["Type"] != "account" and record["Type"] != "function argument":
                writer.writerow(record)

    fieldnames = ["ind", "alg_name", "alg_description", "alg_python", "alg_formulation", "alg_units", "variables", "constants"]
    with open(output_func_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in analyzer.records:
            if record["Type"] == ("function"):
                # print(record)
                writer.writerow(record)

    fieldnames = ['ind', 'code_of_account', 'account_description', 'total_cost (M$)', 'total_cost ($)', 'level', 'prn', 'supaccount', 'alg_name', 'fun_unit', 'variables', 'algno']
    with open(output_acc_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in analyzer.records:
            if record["Type"] == ("account"):
                # print(record)
                writer.writerow(record)

    fieldnames = ["ind", "var_name", "var_description", "var_value", "var_unit", "var_alg", "var_need", "algs_using_var", "v_linked"]
    with open(output_arg_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in analyzer.records:
            if record["Type"] == "function argument":
                writer.writerow(record)

# Takes in the txt output from TEAm and creates the formatted ACCERT first page (accounts) 
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

    # Useful variables for internal math
    account2_iter=0
    totalCost=0

    # Account numbers
    
    for account_iter in range(coaNumRows):
        # Adds the ind numbers in
        formattedCopy[account_iter+1][0] = account_iter+1

        # Formatting account numbers to remove . and add the c in front
        formattedTemp = f"{dataLoadTxt['Account Number'].values[account_iter]}"#.replace('.','')
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
        if formattedCopy[account_iter+1][5] == "0":
            totalCost=totalCost+float(formattedCopy[account_iter+1][3])

        # PRN handled separately

        # supaccount, take one off the original
        formattedTemp = f"{dataLoadTxt['Account Number'].values[account_iter]}".replace('.','')
        if formattedTemp[-1] == '0':
            formattedCopy[account_iter+1][7]=""
        else:
            formattedCopy[account_iter+1][7]=f"{formattedTemp[0:-1]}"

        # 9th column alg_name implemented above

        # units (all millions)
        formattedCopy[account_iter+1][9]="million"

        # variables TODO WIP
        # variables in all of the subaccounts
        if dataLoadTxt['Account Number'].values[account_iter][0] == 2:
            if CodeAnalyzer.account_variables:
                # This currently relies on simple string check to make sure it is part of the direct cost super account
                formattedCopy[account_iter+1][10]=CodeAnalyzer.account_variables[account2_iter+1]
            account2_iter=account2_iter+1
    
    # Special loop for prn
    for account_iter in range(coaNumRows):
        formattedCopy[account_iter+1][6] = str(float(formattedCopy[account_iter+1][3])/totalCost)

    # print(formattedCopy)
    with open('accounts_fromTEAm.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(formattedCopy)

    with open("accounts_by_level.csv", "w", newline="") as f:
        # print(np.shape(np.array(formattedCopy)))
        # print(np.array(formattedCopy))
        a=np.array(formattedCopy)
        formattedCopy_levelSort = a[a[:, 5].argsort()]
        writer = csv.writer(f)
        writer.writerows(formattedCopy_levelSort)
    return formattedCopy


### MAIN ###

# Creates general variables, functions, and TODO accounts csvs based on a python script
extract_metadata_to_csv(filepath="core_editedForNeeds.py", output_var_csv="vars.csv", output_func_csv="func.csv")

# Creates the accounts based on the outputs of the TEAm code
formattedAccountsInit = formatAccounts(TEAm_outputs_path=sys.argv[1])

for account in formattedAccountsInit:
    print(f"({account})")

# print(formattedAccountsInit)