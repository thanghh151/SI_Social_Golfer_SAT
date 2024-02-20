from pycsp3 import *
from itertools import combinations
import time
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from zipfile import BadZipFile
from openpyxl import Workbook
import os

def solve_social_golfers(data):
    clear()
    nWeeks, size, nGroups = data
    nPlayers = nGroups * size

    print(f"Social Golfer Problem with {nPlayers} players, {nGroups} groups of size {size} and {nWeeks} weeks")

    # x[w][p] is the group admitting on week w the player p
    x = VarArray(size=[nWeeks, nPlayers], dom=range(nGroups))
    
    start_time = time.time()

    satisfy(
        # ensuring that two players don't meet more than one time
        [
            If(
                x[w1][p1] == x[w1][p2],
                Then=x[w2][p1] != x[w2][p2]
            ) for w1, w2 in combinations(range(nWeeks), 2) for p1, p2 in combinations(range(nPlayers), 2)
        ],
        # respecting the size of the groups
        [Cardinality(x[w], occurrences={i: size for i in range(nGroups)}) for w in range(nWeeks)],
        # tag(symmetry-breaking)
        LexIncreasing(x, matrix=True)
    )
    
    solve_time = time.time() - start_time

    result_dict = {
        "Problem": f"{nWeeks}-{size}-{nGroups}",
        "Type": "PyCSP",
        "Time": "",
        "Result": "",
        "Variables": 0,
    }
    if solve() is SAT:
        results = []
        for w in range(nWeeks):
            print("Groups of week ", w , [[p for p in range(nPlayers) if x[w][p].value == g] for g in range(nGroups)])
            for g in range(nGroups):
                results.append({"week": w, "group": g, "players": [p for p in range(nPlayers) if x[w][p].value == g]})
        print(f"Constraints: {nGroups * (nWeeks-1) * size}; Variables: {nWeeks * nPlayers}; Time: {solve_time:.4f} seconds")
        result_dict["Result"] = "sat"
        result_dict["Time"] = '{0:.3f}'.format(solve_time)
        result_dict["Variables"] = nWeeks * nPlayers
    else:
        result_dict["Result"] = "unsat"
        result_dict["Time"] = '{0:.3f}'.format(solve_time)
        result_dict["Variables"] = nWeeks * nPlayers

    # Append the result to a list
    excel_results = []
    excel_results.append(result_dict)

    # Write the results to an Excel file
    df = pd.DataFrame(excel_results)
    excel_file_path = f"out/results.xlsx"
        
    # Check if the file already exists
    if os.path.exists(excel_file_path):
        try:
            book = load_workbook(excel_file_path)
        except BadZipFile:
            book = Workbook()  # Create a new workbook if the file is not a valid Excel file

        # Check if the 'Results' sheet exists
        if 'Results' not in book.sheetnames:
            book.create_sheet('Results')  # Create 'Results' sheet if it doesn't exist

        sheet = book['Results']

        for row in dataframe_to_rows(df, index=False, header=False):
            sheet.append(row)

        book.save(excel_file_path)

    else:
        df.to_excel(excel_file_path, index=False, sheet_name='Results', header=False)

    print("Result written to Excel file:", os.path.abspath(excel_file_path))  # Print full path
    print("Result added to Excel file.")

# Read data from file
data_list = []
with open("data.txt") as file:
    for line in file:
        if line[0] != "#":
            data_list.append([int(x) for x in line.split()])

# Solve for each set of data
for data in data_list:
    solve_social_golfers(data)
