from pysat.solvers import Glucose3
from prettytable import PrettyTable
from threading import Timer
import datetime
import pandas as pd
import os
import sys
from openpyxl import load_workbook, Workbook
from zipfile import BadZipFile
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime

# Initialization1 
num_weeks = 2  # number of weeks
num_groups = 3  # number of groups
players_per_group = [2, 3]  # k1 and k2
num_players = 6  # number of players
time_budget = 600
show_additional_info = True
online_path = ''

sat_solver = Glucose3(use_timer=True)

# Function to generate all clauses (for completeness, you can add more constraints as needed)
def generate_all_clauses(m1, m2):
    ensure_golfer_plays_exactly_once_per_week()
    ensure_group_contains_exactly_p_players(m1, m2)
    ensure_no_repeated_players_in_groups()
    symmetry_breaking_1(m1, m2)
    symmetry_breaking_2(m1, m2)
    
def exactly_k(var: list[int], k):
    n = len(var) - 1
    map_register = [[0 for _ in range(k + 1)] for _ in range(n)]
    id_variable = 0
    for i in range(1, n):
        for j in range(1, min(i, k) + 1):
            id_variable += 1
            map_register[i][j] = id_variable

    for i in range(1, n):
        sat_solver.add_clause([-var[i], map_register[i][1]])
    for i in range(2, n):
        for j in range(1, min(i - 1, k) + 1):
            sat_solver.add_clause([-map_register[i - 1][j], map_register[i][j]])
    for i in range(2, n):
        for j in range(2, min(i, k) + 1):
            sat_solver.add_clause([-var[i], -map_register[i - 1][j - 1], map_register[i][j]])
    for i in range(2, n):
        for j in range(1, min(i - 1, k) + 1):
            sat_solver.add_clause([var[i], map_register[i - 1][j], -map_register[i][j]])
    for i in range(1, k + 1):
        sat_solver.add_clause([var[i], -map_register[i][i]])
    for i in range(2, n):
        for j in range(2, min(i, k) + 1):
            sat_solver.add_clause([map_register[i - 1][j - 1], -map_register[i][j]])
    sat_solver.add_clause([map_register[n - 1][k], var[n]])
    sat_solver.add_clause([map_register[n - 1][k], map_register[n - 1][k - 1]])

def exactly_one(var: list[int]):
    n = len(var)
    clause = [v for v in var]
    sat_solver.add_clause(clause)
    for i in range(n):
        for j in range(i + 1, n):
            sat_solver.add_clause([-var[i], -var[j]])

def ensure_golfer_plays_exactly_once_per_week():
    for player in range(1, num_players + 1):
        for week in range(1, num_weeks + 1):
            list_vars = [get_variable(player, group, week) for group in range(1, num_groups + 1)]
            exactly_one(list_vars)

def ensure_group_contains_exactly_p_players(m1, m2):
    for week in range(1, num_weeks + 1):
        # Ensure m1 groups with k1 players
        if m1 > 0:
            for group in range(1, m1 + 1):
                list_vars = [-1]
                for player in range(1, num_players + 1):
                    list_vars.append(get_variable(player, group, week))
                exactly_k(list_vars, players_per_group[0])
        # Ensure m2 groups with k2 players
        if m2 > 0:
            for group in range(m1 + 1, m1 + m2 + 1):
                list_vars = [-1]
                for player in range(1, num_players + 1):
                    list_vars.append(get_variable(player, group, week))
                exactly_k(list_vars, players_per_group[1])

def ensure_no_repeated_players_in_groups():
    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            for golfer1 in range(1, num_players + 1):
                for golfer2 in range(golfer1 + 1, num_players + 1):
                    for other_group in range(1, num_groups + 1):
                        for other_week in range(week + 1, num_weeks + 1):
                            clause = [-get_variable(golfer1, group, week),
                                      -get_variable(golfer2, group, week),
                                      -get_variable(golfer1, other_group, other_week),
                                      -get_variable(golfer2, other_group, other_week)]
                            sat_solver.add_clause(clause)
# SB1: The first week order is [1, 2, 3, ... x]
def symmetry_breaking_1(m1, m2):
    for player in range(1, num_players + 1):
        if player <= m1 * players_per_group[0]:
            right_group = (player - 1) // players_per_group[0] + 1
        else:
            right_group = m1 + (player - m1 * players_per_group[0] - 1) // players_per_group[1] + 1
        for group in range(1, num_groups + 1):
            if group == right_group:
                sat_solver.add_clause([get_variable(player, group, 1)])
            else:
                sat_solver.add_clause([-1 * get_variable(player, group, 1)])

# SB2: From week 2, first p players belong to p groups
def symmetry_breaking_2(m1, m2):
    for week in range(2, num_weeks + 1):
        for player in range(1, num_players + 1):
            if player <= m1 * players_per_group[0]:
                right_group = (player - 1) // players_per_group[0] + 1
            else:
                right_group = m1 + (player - m1 * players_per_group[0] - 1) // players_per_group[1] + 1
            for group in range(1, num_groups + 1):
                if group == right_group:
                    sat_solver.add_clause([get_variable(player, group, week)])
                else:
                    sat_solver.add_clause([-1 * get_variable(player, group, week)])
                    
def get_variable(player, group, week):
    return 1 + player + (group - 1) * num_players + (week - 1) * num_players * num_groups

def resolve_variable(v):
    tmp = abs(v) - 1
    player = tmp % num_players + 1
    tmp //= num_players
    group = tmp % num_groups + 1
    tmp //= num_groups
    week = tmp + 1
    return player, group, week

def validate_result(solution):
    table = {week: {group: [] for group in range(1, num_groups + 1)} for week in range(1, num_weeks + 1)}

    for v in solution:
        if abs(v) > num_players * num_groups * num_weeks: break
        if v > 0:
            player, group, week = resolve_variable(v)
            table[week][group].append(player)

    for week in table:
        has_played = [0] * (num_players + 1)
        for player in range(1, num_players + 1):
            has_played[player] = 0
        for group in table[week]:
            for player in table[week][group]:
                if has_played[player] == 1: return False
                has_played[player] = 1

    for week in table:
        for group in table[week]:
            if len(table[week][group]) != players_per_group[0]: return False

    play_together = [[0 for _ in range(num_players + 1)] for _ in range(num_players + 1)]
    for week in table:
        for group in table[week]:
            for id1 in range(players_per_group[0]):
                x = table[week][group][id1]
                for id2 in range(id1 + 1, players_per_group[0]):
                    y = table[week][group][id2]
                    if play_together[x][y] == 1:
                        return False
                    play_together[x][y] = 1
    return True

def find_valid_m1_m2():
    k1 = players_per_group[0]
    k2 = players_per_group[1] if len(players_per_group) > 1 else None

    valid_combinations = []
    for m1 in range(num_groups + 1):
        remaining_players = num_players - m1 * k1
        if k2 and remaining_players % k2 == 0:
            m2 = remaining_players // k2
            if m1 + m2 == num_groups:
                valid_combinations.append((m1, m2))
        elif not k2 and remaining_players == 0 and m1 == num_groups:
            valid_combinations.append((m1, 0))
    
    return valid_combinations

def run_sat_solver():
    valid_combinations = find_valid_m1_m2()
    for m1, m2 in valid_combinations:
        print(f"Trying m1 = {m1}, m2 = {m2}...")
        sat_solver = Glucose3(use_timer=True)
        generate_all_clauses(m1, m2)
        sat_status = sat_solver.solve_limited(expect_interrupt=True)
        print("SAT Status:", sat_status)
        if sat_status:
            solution = sat_solver.get_model()
            if solution is not None:
                print("Model:", solution)
                print("Number of Clauses:", sat_solver.nof_clauses())
                print("Number of Variables:", sat_solver.nof_vars())
                print("Solution found!")
                if validate_result(solution):
                    print("Valid solution.")
                    return solution
                else:
                    print("Invalid solution.")
            else:
                print("Model is None. No solution found.")
        else:
            print("SAT solver did not find a solution.")
    return None

def process_results(results):
    new_table = {week: {group: [] for group in range(1, num_groups + 1)} for week in range(1, num_weeks + 1)}

    for v in results:
        if abs(v) > num_players * num_groups * num_weeks: break
        if v > 0:
            player, group, week = resolve_variable(v)
            new_table[week][group].append(player)
    return new_table

def show_results(results):
    table = PrettyTable()
    table.field_names = ["Week", "Group", "Players"]
    processed_results = process_results(results)
    for week, groups in processed_results.items():
        for group, players in groups.items():
            table.add_row([week, group, ", ".join(map(str, players))])
    print(table)

def show_results2(results):
    processed_results = process_results(results)
    df_list = []
    for week, groups in processed_results.items():
        week_df = pd.DataFrame.from_dict(groups, orient='index').fillna('')
        week_df.index = [f"Group {i}" for i in week_df.index]
        week_df.index.name = f"Week {week}"
        df_list.append(week_df)

    writer = pd.ExcelWriter('output.xlsx', engine='openpyxl')
    for idx, df in enumerate(df_list):
        df.to_excel(writer, sheet_name=f'Week {idx + 1}')
    writer.save()

def main():
    start_time = datetime.now()
    results = run_sat_solver()
    if results:
        print("Results found.")
        show_results(results)
        show_results2(results)
    else:
        print("No results found.")
    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    print(f"Execution time: {elapsed_time} seconds")

if __name__ == "__main__":
    main()
