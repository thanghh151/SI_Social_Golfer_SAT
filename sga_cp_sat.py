from ortools.sat.python import cp_model
from prettytable import PrettyTable
from threading import Timer
import datetime
import pandas as pd
import os
import sys
import ast
import math
from openpyxl import load_workbook
from openpyxl import Workbook
from zipfile import BadZipFile
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime

num_weeks: int  # number of weeks
players_per_group: list[int]  # players per group
num_groups: int  # number of groups
num_players: int
id_variable: int
time_budget = 60
show_additional_info = True
online_path = ''
id_counter = 0

model = cp_model.CpModel()
solver = cp_model.CpSolver()

def generate_all_constraints(model, m1, m2, num_groups):
    ensure_golfer_plays_exactly_once_per_week(model, num_groups)
    ensure_group_contains_exactly_p_players(model, m1, m2, num_groups)
    ensure_no_repeated_players_in_groups(model, num_groups)
    # symmetry_breaking_1(model, m1, m2, num_groups)
    # symmetry_breaking_2(model, m1, m2, num_groups)

# Tạo biến cho mỗi người chơi, nhóm và tuần
variables = {}
for player in range(1, num_players + 1):
    for group in range(1, num_groups + 1):
        for week in range(1, num_weeks + 1):
            variables[(player, group, week)] = get_variable(model, player, group, week, num_groups)

def ensure_golfer_plays_exactly_once_per_week(model, num_groups):
    for player in range(1, num_players + 1):
        for week in range(1, num_weeks + 1):
            model.AddExactlyOne(variables[(player, group, week)] for group in range(1, num_groups + 1))

def ensure_group_contains_exactly_p_players(model, m1, m2, num_groups):
    for week in range(1, num_weeks + 1):
        if m2 > 0:
            for group in range(1, m2 + 1):
                model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[1])

            for group in range(m2 + 1, num_groups + 1):
                model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[0])
        else:
            for group in range(1, num_groups + 1):
                model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[0])

def ensure_no_repeated_players_in_groups(model, num_groups):
    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            for golfer1 in range(1, num_players + 1):
                for golfer2 in range(golfer1 + 1, num_players + 1):
                    for other_group in range(1, num_groups + 1):
                        for other_week in range(week + 1, num_weeks + 1):
                            model.AddBoolOr([
                                get_variable(model, golfer1, group, week, num_groups).Not(),
                                get_variable(model, golfer2, group, week, num_groups).Not(),
                                get_variable(model, golfer1, other_group, other_week, num_groups).Not(),
                                get_variable(model, golfer2, other_group, other_week, num_groups).Not()
                            ])

def symmetry_breaking_1(model, m1, m2, num_groups):
    for player in range(1, num_players + 1):
        if m2 is None:
            if player <= m1 * players_per_group[0]:
                right_group = (player - 1) // players_per_group[0] + 1
            else:
                right_group = m1 + (player - m1 * players_per_group[0] - 1) // players_per_group[1] + 1
        else:
            if player <= m2 * players_per_group[1]:
                right_group = (player - 1) // players_per_group[1] + 1
            else:
                right_group = m2 + (player - m2 * players_per_group[1] - 1) // players_per_group[0] + 1

        for group in range(1, num_groups + 1):
            if group == right_group:
                model.Add(get_variable(model, player, group, 1, num_groups) == 1)
            else:
                model.Add(get_variable(model, player, group, 1, num_groups) == 0)

def symmetry_breaking_2(m1, m2, num_groups):
    if m2 is not None:
        max_week = math.floor((num_players - players_per_group[1]) / players_per_group[0]) - 1
        for week in range(2, max_week + 1):
            for player in range(1, min(num_groups, players_per_group[1]) + 1):
                for group in range(1, num_groups + 1):
                    model.Add(get_variable(player, group, week, num_groups) == 1)
    else:
        for week in range(2, max_week + 1):
            for player in range(1, min(num_groups, players_per_group[0]) + 1):
                for group in range(1, num_groups + 1):
                    model.Add(get_variable(player, group, week, num_groups) == 1)

def find_all_valid_combinations():
    valid_combinations = set()

    k1 = players_per_group[0]
    k2 = players_per_group[1] if len(players_per_group) > 1 else None

    for num_groups in range(2, num_players + 1):
        for m1 in range(0, num_players + 1):
            for m2 in range(0, num_players + 1):
                if k2 is not None:
                    if m1 * k1 + m2 * k2 == num_players and m1 + m2 == num_groups:
                        valid_combinations.add((k1, k2, m1, m2, num_groups))
                else:
                    if m1 * k1 == num_players and m1 == num_groups:
                        valid_combinations.add((k1, None, m1, 0, num_groups))

    return list(valid_combinations)

def get_variable(model, player, group, week, num_groups):
    return model.NewBoolVar(f"player_{player}_group_{group}_week_{week}")


def resolve_variable(v, num_groups):
    week = (v - 1) // (num_players * num_groups) + 1
    remainder = (v - 1) % (num_players * num_groups)
    group = remainder // num_players + 1
    player = remainder % num_players + 1
    return player, group, week

def validate_result(solution):
    table = {}
    for week in range(1, num_weeks + 1):
        table[week] = {}
        for group in range(1, num_groups + 1): table[week][group] = []

    for v in solution:
        if abs(v) > num_players * num_groups * num_weeks: break
        if v > 0:
            player, group, week = resolve_variable(v, num_groups)
            table[week][group].append(player)

    # Check part 1
    has_played = [0 for i in range(num_players + 1)]
    for week in range(1, num_weeks + 1):
        for player in range(1, num_players + 1):
            has_played[player] = 0
        for group in range(1, num_groups + 1):
            for player in table[week][group]:
                if (has_played[player] == 1): return False
                has_played[player] = 1

    # Check part 2
    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            if (len(table[week][group]) != players_per_group): return False

    # Check part 3
    play_together = [[0 for j in range(num_players + 1)] for i in range(num_players + 1)]
    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            for id1 in range(0, players_per_group):
                x = table[week][group][id1]
                for id2 in range(id1 + 1, players_per_group):
                    y = table[week][group][id2]
                    if (play_together[x][y] == 1):
                        return False
                    play_together[x][y] = 1
    return True

def process_results(results, num_groups):
    new_table = {}
    for week in range(1, num_weeks + 1):
        new_table[week] = {}
        for group in range(1, num_groups + 1):
            new_table[week][group] = []
    for row in results:
        new_table[row["week"]][row["group"]].append(row["player"])
    return new_table

def show_results(results, num_groups):
    print_table = PrettyTable()
    field_names = ["Week"]
    for group in range(1, num_groups + 1):
        field_names.append("Group " + str(group))
    print_table.field_names = field_names
    for week in range(1, num_weeks + 1):
        row = [str(week)]
        for group in range(1, num_groups + 1):
            row.append(str(",".join(list(map(str, results[week][group])))))
        print_table.add_row(row)
    print_to_console_and_log(print_table)

def process_results2(results, num_groups):
    new_table = {}
    for week in range(1, num_weeks + 1):
        new_table[week] = {}
        for player in range(1, num_players + 1):
            new_table[week][player] = []
    for row in results:
        new_table[row["week"]][row["player"]] = row["group"]
    return new_table

def show_results2(results, num_groups):
    print_table = PrettyTable()
    field_names = ["W\P"]
    for player in range(1, num_players + 1):
        field_names.append(str(player))
    print_table.field_names = field_names
    for week in range(1, num_weeks + 1):
        row = [str(week)]
        for player in range(1, num_players + 1):
            row.append(str(results[week][player]))
        print_table.add_row(row)
    print_to_console_and_log(print_table)

def interrupt(s): s.interrupt()

def write_to_cnf(num_vars, num_clauses, problem_name):
    # Create the directory if it doesn't exist
    input_path = online_path + "input_cnf"
    if not os.path.exists(input_path): os.makedirs(input_path)

    # Create the full path to the file "{problem}.cnf" in the directory "input_cnf"
    file_name = problem_name + ".cnf"
    file_path = os.path.join(input_path, file_name)

    # Write data to the file
    with open(file_path, 'w') as writer:
        # Write a line of information about the number of variables and constraints
        writer.write("p cnf " + str(num_vars) + " " + str(num_clauses) + "\n")

        # Write each clause to the file
        for clause in all_clauses:
            for literal in clause: writer.write(str(literal) + " ")
            writer.write("0\n")

    print_to_console_and_log("CNF written to " + file_path + ".\n")

def write_to_xlsx(result_dict):
    # Append the result to a list
    excel_results = []
    excel_results.append(result_dict)

    output_path = online_path + 'out'

    # Write the results to an Excel file
    if not os.path.exists(output_path): os.makedirs(output_path)

    df = pd.DataFrame(excel_results)
    current_date = datetime.now().strftime('%Y-%m-%d')
    excel_file_path = f"{output_path}/results_{current_date}.xlsx"

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
        for row in dataframe_to_rows(df, index=False, header=False): sheet.append(row)
        book.save(excel_file_path)

    else: df.to_excel(excel_file_path, index=False, sheet_name='Results', header=False)

    print_to_console_and_log(f"Result added to Excel file: {os.path.abspath(excel_file_path)}\n")

def check_legit(solution, num_groups):
    results = []
    for v in solution:
        if abs(v) > num_players * num_groups * num_weeks: break
        if v > 0 and v <= num_players * num_groups * num_weeks:
            player, group, week = resolve_variable(v, num_groups)
            results.append({"player": player, "group": group, "week": week})

    final_result = process_results(results, num_groups)
    show_results(final_result, num_groups)

    board = process_results2(results, num_groups)
    show_results2(board, num_groups)

    # print_to_console_and_log("Checking validation of the solution...")
    # if (not validate_result(solution)):
    #     print_to_console_and_log("Invalid solution. TERMINATE right now.\n")
    #     return False
    # else: print_to_console_and_log("Valid solution.\n")
    return True

def run_kissat(problem_name):
    # Create the directory if it doesn't exist
    input_path = online_path + "output_kissat"
    if not os.path.exists(input_path): os.makedirs(input_path)

    # Create the full path to the file "{problem}.txt"
    file_name = problem_name + ".txt"
    file_path = os.path.join(input_path, file_name)

    print_to_console_and_log("Running KiSSAT...")
    bashCommand = f"ls input_cnf/{problem_name}.cnf | xargs -n 1 ./kissat --time={time_budget} --relaxed > output_kissat/{problem_name}.txt"
    os.system(bashCommand)
    print_to_console_and_log("KiSSAT finished.")

# solve the problem using the SAT Solver and write the results to xlsx file
def solve_sat_problem():
    global num_players, id_variable, id_counter

    valid_combinations = find_all_valid_combinations()
    for k1, k2, m1, m2, num_groups in valid_combinations:
        id_variable = num_players * num_groups * num_weeks
        id_counter += 1
        result_dict = {
            "ID": id_counter,
            "Problem": f"{num_players}-{num_groups}-{players_per_group}-{num_weeks}",
            "Type": "sga_nsc",
            "Time": "",
            "Result": "",
            "Variables": 0,
            "Clauses": 0
        }

        print_to_console_and_log(
            f"Problem no. {id_counter}:\n" +
            f"Number of players: {num_players}.\n" +
            f"Number of groups: {num_groups}.\n" +
            f"Players per group: {players_per_group}.\n" +
            f"k1: {k1}.\n" +
            f"k2: {k2}.\n" +
            f"m1: {m1}.\n" +
            f"m2: {m2}.\n" +
            f"Number of weeks: {num_weeks}.\n")

        assert num_groups > 1 and players_per_group[0] > 1

        model = cp_model.CpModel()
        generate_all_constraints(model, m1, m2, num_groups)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_budget

        num_vars = len(model.Proto().variables)
        num_clauses = len(model.Proto().constraints)

        result_dict["Variables"] = num_vars
        result_dict["Clauses"] = num_clauses
        if show_additional_info:
            print_to_console_and_log("Variables: " + str(num_vars))
            print_to_console_and_log("Clauses: " + str(num_clauses))

        # Check if the model has been populated with variables and constraints
        if num_vars == 0 or num_clauses == 0:
            print_to_console_and_log("Error: Model has no variables or constraints.")
            continue

        print_to_console_and_log("Searching for a solution...")
        timer = Timer(time_budget, interrupt, [solver])
        timer.start()

        try:
            status = solver.Solve(model)
            elapsed_time = format(solver.WallTime(), ".3f")
            print_to_console_and_log(f"Solver status: {status}")
            if status == cp_model.INFEASIBLE:
                print_to_console_and_log(f"UNSAT. Time run: {elapsed_time}s.\n")
                result_dict["Result"] = "unsat"
                result_dict["Time"] = elapsed_time
            elif status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                print_to_console_and_log(f"SAT. Time run: {elapsed_time}s.\n")
                result_dict["Result"] = "sat"
                result_dict["Time"] = elapsed_time
                solution = [solver.Value(var) for var in model.Proto().variables]
                print_to_console_and_log("Checking solution legitimacy...")
                check_legit(solution, num_groups)
            else:
                print_to_console_and_log(f"Unknown status: {status}")
        except Exception as e:
            print_to_console_and_log(f"Exception during solving: {e}")
        finally:
            timer.cancel()

        write_to_xlsx(result_dict)

        print_to_console_and_log('-' * 120)

log_file = open(online_path + 'console.log', 'a')


# Define a custom print function that writes to both console and log file
def print_to_console_and_log(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, file = log_file, **kwargs)
    log_file.flush()

# read input data from file data.txt (many lines, each line is number of weeks, number of players per group, number of groups)
# solve the problem
def run_from_input_file():
    global num_players, players_per_group, num_weeks
    with open('data_new.txt') as f:
        for line in f:
            parts = line.split()
            try:
                num_players = int(parts[0])

                # Clean and validate the list part
                list_part = parts[1].strip()
                if not (list_part.startswith('[') and list_part.endswith(']')):
                    raise SyntaxError("List part is not properly formatted")

                players_per_group = ast.literal_eval(list_part)
                num_weeks = int(parts[2])
                solve_sat_problem()
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing line: {line.strip()}")
                print(f"Exception: {e}")
                continue

    log_file.close()


if __name__ == "__main__": run_from_input_file()
