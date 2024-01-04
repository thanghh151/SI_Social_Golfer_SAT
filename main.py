from pysat.solvers import Glucose3, Solver
from prettytable import PrettyTable
from threading import Timer

num_weeks: int  # number of weeks
players_per_group: int  # players per group
num_groups: int  # number of groups
num_players: int  # players per group * number of groups
time_budget = 10
show_additional_info = True
show_additional_info_str = "Yes"

sat_solver: Solver


def generate_all_clauses():
    ALO_a_week_every_golfer_plays()
    AMO_each_golfer_plays_in_each_group_each_week()
    AMO_group_each_golfer_plays_each_week()
    ALO_each_player_plays_in_a_group_in_a_week()
    ALO_()
    generate_clause6()
    two_players_do_not_meet_more_than_one()
    generate_symmetry_breaking_clause1()
    generate_symmetry_breaking_clause2()
    generate_symmetry_breaking_clause3()


# Every golfer plays at least once a week
def ALO_a_week_every_golfer_plays():
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks + 1):
            loo = []
            for j in range(1, players_per_group + 1):
                for k in range(1, num_groups + 1):
                    loo.append(get_variable(i, j, k, l))
                    # print(get_variable(i, j, k, l))
            # print(loo)
            sat_solver.add_clause(loo)


# Each golfer plays at most once in each group each week
def AMO_each_golfer_plays_in_each_group_each_week():
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks + 1):
            for j in range(1, players_per_group + 1):
                for k in range(1, num_groups + 1):
                    for m in range(j + 1, players_per_group + 1):
                        loo = [-1 * get_variable(i, j, k, l),
                               -1 * get_variable(i, m, k, l)]
                        print(loo)
                        sat_solver.add_clause(loo)


# No golfer plays in more than one group each week
def AMO_group_each_golfer_plays_each_week():
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks + 1):
            for j in range(1, players_per_group + 1):
                for k in range(1, num_groups + 1):
                    for m in range(k + 1, num_groups + 1):
                        for n in range(1, players_per_group + 1):
                            loo = [-1 * get_variable(i, j, k, l),
                                   -1 * get_variable(i, n, m, l)]
                            sat_solver.add_clause(loo)

# ensure each player appears only once in a group in a week
def ALO_each_player_plays_in_a_group_in_a_week():
    for l in range(1, num_weeks + 1):
        for k in range(1, num_groups + 1):
            for j in range(1, players_per_group + 1):
                loo = []
                for i in range(1, num_players + 1):
                    loo.append(get_variable(i, j, k, l))
                sat_solver.add_clause(loo)

# ensure no two players occupy the same position in the same group in the same week
def ALO_():
    for l in range(1, num_weeks + 1):
        for k in range(1, num_groups + 1):
            for j in range(1, players_per_group + 1):
                for i in range(1, num_players + 1):
                    for m in range(i + 1, players_per_group + 1):
                        loo = [-1 * get_variable(i, j, k, l),
                               -1 * get_variable(m, j, k, l)]
                        sat_solver.add_clause(loo)


# This is a clause combining two sets of variables, ijkl and ikl
def generate_clause6():
    for i in range(1, num_players + 1):
        for k in range(1, num_groups + 1):
            for l in range(1, num_weeks + 1):
                tab = [-1 * get_variable2(i, k, l)]
                for j in range(1, players_per_group + 1):
                    tab.append(get_variable(i, j, k, l))
                    tab2 = [get_variable2(i, k, l),
                            -1 * get_variable(i, j, k, l)]
                    sat_solver.add_clause(tab2)
                sat_solver.add_clause(tab)


# If two players m and n play in the same group k in week l, they cannot play together in any group together in future weeks
def two_players_do_not_meet_more_than_one():
    for l in range(1, num_weeks + 1):
        for k in range(1, num_groups + 1):
            for m in range(1, num_players + 1):
                for n in range(m + 1, num_players + 1):
                    for k2 in range(1, num_groups + 1):
                        for l2 in range(l + 1, num_weeks + 1):
                            loo = [-1 * get_variable2(m, k, l),
                                   -1 * get_variable2(n, k, l),
                                   -1 * get_variable2(m, k2, l2),
                                   -1 * get_variable2(n, k2, l2)]
                            sat_solver.add_clause(loo)


def generate_symmetry_breaking_clause1():
    for i in range(1, num_players + 1):
        for j in range(1, players_per_group):
            for k in range(1, num_groups + 1):
                for l in range(1, num_weeks + 1):
                    for m in range(1, i + 1):
                        loo = [-1 * get_variable(i, j, k, l),
                               -1 * get_variable(m, j + 1, k, l)]
                        sat_solver.add_clause(loo)


def generate_symmetry_breaking_clause2():
    for i in range(1, num_players + 1):
        for k in range(1, num_groups):
            for l in range(1, num_weeks + 1):
                for m in range(1, i):
                    loo = [-1 * get_variable(i, 1, k, l),
                           -1 * get_variable(m, 1, k + 1, l)]
                    sat_solver.add_clause(loo)


def generate_symmetry_breaking_clause3():
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks):
            for m in range(1, i + 1):
                loo = [-1 * get_variable(i, 2, 1, l),
                       -1 * get_variable(m, 2, 1, l + 1)]
                sat_solver.add_clause(loo)


def get_variable(i, j, k, l):
    i -= 1
    j -= 1
    k -= 1
    l -= 1
    return i + (num_players * j) + (k * num_players * players_per_group) + (l * num_players * players_per_group * num_groups) + 1


def get_variable2(i, k, l):
    i -= 1
    k -= 1
    l -= 1
    return i + (num_players * k) + (l * num_players * num_groups) + 1 + (num_players * players_per_group * num_groups * num_weeks)


def resolve_variable(v):
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks + 1):
            for j in range(1, players_per_group + 1):
                for k in range(1, num_groups + 1):
                    if abs(v) == get_variable(i, j, k, l):
                        return i, j, k, l
    for i in range(1, num_players + 1):
        for l in range(1, num_weeks + 1):
            for k in range(1, num_groups + 1):
                if abs(v) == get_variable2(i, k, l):
                    return i, k, l
    return


def process_results(results):
    new_table = {}
    for week in range(1, num_weeks + 1):
        new_table[week] = {}
        for group in range(1, num_groups + 1):
            new_table[week][group] = []
    for row in results:
        new_table[row["l"]][row["k"]].append(row["i"])
    return new_table


def show_results(results):
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
    print(print_table)


def change_time_budget():
    global time_budget
    while True:
        try:
            time_bud = int(input("\nEnter new time limit in seconds (current: " + str(time_budget) + "s): "))
            if time_bud < 0:
                time_bud = 0
            elif time_bud > 999999:
                time_bud = 999999
            time_budget = time_bud
        except ValueError:
            print("Enter a valid value\n")
            continue
        else:
            break


def change_showing_additional_info():
    global show_additional_info, show_additional_info_str
    while True:
        try:
            print(
                "\nShould additional information about solving the problem in the SAT Solver be displayed (i.e.: number of variables, number of clauses, propagations, conflicts, decisions and restarts)")
            print("1 - Yes")
            print("2 - No")
            choice = int(input("Choose an option: "))
            if choice == 1:
                show_additional_info = True
                show_additional_info_str = "Yes"
            elif choice == 2:
                show_additional_info = False
                show_additional_info_str = "No"
            else:
                print("Enter a valid value\n")
                continue
        except ValueError:
            print("Enter a valid value\n")
            continue
        else:
            break


def main_menu():
    while True:
        try:
            print("\n/------------------------------\\")
            print("| Social Golfer Problem Solver |")
            print("\\------------------------------/")
            print("1 - Solve the Social Golfer problem")
            print("2 - Change timeout (currently: " + str(time_budget) + "s)")
            print("3 - Change showing additional information (currently: " + show_additional_info_str + ")")
            print("0 - Finish")
            selection = int(input("Select options: "))
            if selection == 1:
                menu()
            elif selection == 2:
                change_time_budget()
            elif selection == 3:
                change_showing_additional_info()
            elif selection == 0:
                return

        except ValueError:
            print("Enter a valid value\n")
            continue
        else:
            pass


def menu():
    global num_weeks, players_per_group, num_groups
    while True:
        try:
            num_weeks = int(input("Enter the number of weeks: "))
            if num_weeks <= 0:
                print("Enter a valid value\n")
                continue
            players_per_group = int(input("Enter the number of players per group: "))
            if players_per_group <= 0:
                print("Enter a valid value\n")
                continue
            num_groups = int(input("Enter the number of groups: "))
            if num_groups <= 0:
                print("Enter a valid value\n")
                continue
        except ValueError:
            print("Enter a valid value\n")
            continue
        else:
            break
    solve_sat_problem()


def interrupt(s):
    s.interrupt()


def solve_sat_problem():
    global num_players, sat_solver
    num_players = players_per_group * num_groups

    print("\nGenerating a problem.")

    sat_solver = Glucose3(use_timer=True)
    generate_all_clauses()

    if show_additional_info:
        print("Clauses: " + str(sat_solver.nof_clauses()))
        print("Variables: " + str(sat_solver.nof_vars()))

    print("\nSearching for a solution.")

    timer = Timer(time_budget, interrupt, [sat_solver])
    timer.start()

    sat_status = sat_solver.solve_limited(expect_interrupt=True)

    if sat_status is False:
        print("\nNot found. There is no solution.")
    else:
        solution = sat_solver.get_model()
    if solution is None:
        print("Not found. Time exceeded (" + '{0:.2f}s'.format(sat_solver.time()) + ").\n")
    else:
        print(
            "A solution was found in time " + '{0:.2f}s'.format(sat_solver.time()) + ". Generating it now.\n")
        result = []
        for v in solution:
            if v > 0:
                ijkl = resolve_variable(v)
                if len(ijkl) == 3:
                    i, k, l = ijkl
                    result.append({"i": i, "k": k, "l": l})

        final_result = process_results(result)
        show_results(final_result)

        if show_additional_info:
            sat_accum_stats = sat_solver.accum_stats()
            print("Restarts: " +
                  str(sat_accum_stats['restarts']) +
                  ", conflicts: " +
                  ", decisions: " +
                  str(sat_accum_stats['decisions']) +
                  ", propagations: " +
                  str(sat_accum_stats["propagations"]))

        input("Press Enter to continue...")

    sat_solver.delete()


if __name__ == "__main__":
    main_menu()
