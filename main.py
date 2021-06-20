from pysat.solvers import Glucose3, Solver
from prettytable import PrettyTable
from threading import Timer

w: int  # liczba tygodni
p: int  # gracze na grupe
g: int  # liczba grup
x: int  # p * g

time_budget = 10
show_additional_info = True
show_additional_info_str = "Tak"

sat_solver: Solver


def genAllClauses():
    genClause1()
    genClause2()
    genClause3()
    genClause4()
    genClause5()
    genClause6()
    genClause7()
    genSymmetryBreakingClause1()
    genSymmetryBreakingClause2()
    genSymmetryBreakingClause3()


# Każdy golfista gra co najmniej raz w tygodniu
def genClause1():
    for i in range(1, x + 1):
        for l in range(1, w + 1):
            loo = []
            for j in range(1, p + 1):
                for k in range(1, g + 1):
                    loo.append(getVariable(i, j, k, l))
            sat_solver.add_clause(loo)


# Każdy golfista gra co najwyżej raz w każdej grupie w każdym tygodniu
def genClause2():
    for i in range(1, x + 1):
        for l in range(1, w + 1):
            for j in range(1, p + 1):
                for k in range(1, g + 1):
                    for m in range(j + 1, p + 1):
                        loo = [-1 * getVariable(i, j, k, l),
                               -1 * getVariable(i, m, k, l)]
                        sat_solver.add_clause(loo)


# Żaden golfista nie gra w więcej niż jednej grupie w każdym tygodniu
def genClause3():
    for i in range(1, x + 1):
        for l in range(1, w + 1):
            for j in range(1, p + 1):
                for k in range(1, g + 1):
                    for m in range(k + 1, g + 1):
                        for n in range(1, p + 1):
                            loo = [-1 * getVariable(i, j, k, l),
                                   -1 * getVariable(i, n, m, l)]
                            sat_solver.add_clause(loo)


def genClause4():
    for l in range(1, w + 1):
        for k in range(1, g + 1):
            for j in range(1, p + 1):
                loo = []
                for i in range(1, x + 1):
                    loo.append(getVariable(i, j, k, l))
                sat_solver.add_clause(loo)


def genClause5():
    for l in range(1, w + 1):
        for k in range(1, g + 1):
            for j in range(1, p + 1):
                for i in range(1, x + 1):
                    for m in range(i + 1, p + 1):
                        loo = [-1 * getVariable(i, j, k, l),
                               -1 * getVariable(m, j, k, l)]
                        sat_solver.add_clause(loo)


# Jest to klauzula łącząca dwa zestawy zmiennych, ijkl oraz ikl
def genClause6():
    for i in range(1, x + 1):
        for k in range(1, g + 1):
            for l in range(1, w + 1):
                tab = [-1 * getVariable2(i, k, l)]
                for j in range(1, p + 1):
                    tab.append(getVariable(i, j, k, l))
                    tab2 = [getVariable2(i, k, l),
                            -1 * getVariable(i, j, k, l)]
                    sat_solver.add_clause(tab2)
                sat_solver.add_clause(tab)


# Jeśli dwaj gracze m oraz n grają w tej samej grupie k w tygodniu l to nie mogą grać razem w żadnej grupie razem w przyszłych tygodniach
def genClause7():
    for l in range(1, w + 1):
        for k in range(1, g + 1):
            for m in range(1, x + 1):
                for n in range(m + 1, x + 1):
                    for k2 in range(1, g + 1):
                        for l2 in range(l + 1, w + 1):
                            loo = [-1 * getVariable2(m, k, l),
                                   -1 * getVariable2(n, k, l),
                                   -1 * getVariable2(m, k2, l2),
                                   -1 * getVariable2(n, k2, l2)]
                            sat_solver.add_clause(loo)


def genSymmetryBreakingClause1():
    for i in range(1, x + 1):
        for j in range(1, p):
            for k in range(1, g + 1):
                for l in range(1, w + 1):
                    for m in range(1, i + 1):
                        loo = [-1 * getVariable(i, j, k, l),
                               -1 * getVariable(m, j + 1, k, l)]
                        sat_solver.add_clause(loo)


def genSymmetryBreakingClause2():
    for i in range(1, x + 1):
        for k in range(1, g):
            for l in range(1, w + 1):
                for m in range(1, i):
                    loo = [-1 * getVariable(i, 1, k, l),
                           -1 * getVariable(m, 1, k + 1, l)]
                    sat_solver.add_clause(loo)


def genSymmetryBreakingClause3():
    for i in range(1, x + 1):
        for l in range(1, w):
            for m in range(1, i + 1):
                loo = [-1 * getVariable(i, 2, 1, l),
                       -1 * getVariable(m, 2, 1, l + 1)]
                sat_solver.add_clause(loo)


def getVariable(i, j, k, l):
    i -= 1
    j -= 1
    k -= 1
    l -= 1
    return i + (x * j) + (k * x * p) + (l * x * p * g) + 1


def getVariable2(i, k, l):
    i -= 1
    k -= 1
    l -= 1
    return i + (x * k) + (l * x * g) + 1 + (x * p * g * w)


def resolveVariable(v):
    for i in range(1, x + 1):
        for l in range(1, w + 1):
            for j in range(1, p + 1):
                for k in range(1, g + 1):
                    if abs(v) == getVariable(i, j, k, l):
                        return i, j, k, l
    for i in range(1, x + 1):
        for l in range(1, w + 1):
            for k in range(1, g + 1):
                if abs(v) == getVariable2(i, k, l):
                    return i, k, l
    return


def processResults(wyn):
    ntab = {}
    for tyg in range(1, w + 1):
        ntab[tyg] = {}
        for grp in range(1, g + 1):
            ntab[tyg][grp] = []
    for row in wyn:
        ntab[row["l"]][row["k"]].append(row["i"])
    return ntab


def showResults(wyn):
    prt_table = PrettyTable()
    field_names = ["Tydzien"]
    for grupa in range(1, g + 1):
        field_names.append("Grupa " + str(grupa))
    prt_table.field_names = field_names
    for tyg in range(1, w + 1):
        row = [str(tyg)]
        for grupa in range(1, g + 1):
            row.append(str(",".join(list(map(str, wyn[tyg][grupa])))))
        prt_table.add_row(row)
    print(prt_table)


def changeTimeBudget():
    global time_budget
    while True:
        try:
            time_bud = int(input("\nPodaj nowy limit czasu w sekundach (aktualny: " + str(time_budget) + "s): "))
            if time_bud < 0:
                time_bud = 0
            elif time_bud > 999999:
                time_bud = 999999
            time_budget = time_bud
        except ValueError:
            print("Podaj poprawną wartość\n")
            continue
        else:
            break


def changeShowingAdditionalInfo():
    global show_additional_info, show_additional_info_str
    while True:
        try:
            print(
                "\nCzy mają być wyświetlane dodatkowe informacje odnośnie rozwiązywania problemu w SAT Solverze (tzn.: liczba zmiennych, liczba klauzul, propagacje, konflikty, decyzje oraz restarty)")
            print("1 - Tak")
            print("2 - Nie")
            wybor = int(input("Wybierz opcje: "))
            if wybor == 1:
                show_additional_info = True
                show_additional_info_str = "Tak"
            elif wybor == 2:
                show_additional_info = False
                show_additional_info_str = "Nie"
            else:
                print("Podaj poprawną wartość\n")
                continue
        except ValueError:
            print("Podaj poprawną wartość\n")
            continue
        else:
            break


def mainMenu():
    while True:
        try:
            print("\n/------------------------------\\")
            print("| Social Golfer Problem Solver |")
            print("\\------------------------------/")
            print("1 - Rozwiąż problem Social Golfer")
            print("2 - Zmień limit czasu (aktualnie: " + str(time_budget) + "s)")
            print("3 - Zmień pokazywanie dodatkowych informacji (aktualnie: " + show_additional_info_str + ")")
            print("0 - Zakończ")
            wybor = int(input("Wybierz opcje: "))
            if wybor == 1:
                menu()
            elif wybor == 2:
                changeTimeBudget()
            elif wybor == 3:
                changeShowingAdditionalInfo()
            elif wybor == 0:
                return

        except ValueError:
            print("Podaj poprawną wartość\n")
            continue
        else:
            pass


def menu():
    global w, p, g
    while True:
        try:
            w = int(input("Podaj liczbę tygodni: "))
            if w <= 0:
                print("Podaj poprawną wartość\n")
                continue
            p = int(input("Podaj liczbę graczy w grupie: "))
            if p <= 0:
                print("Podaj poprawną wartość\n")
                continue
            g = int(input("Podaj liczbę grup: "))
            if g <= 0:
                print("Podaj poprawną wartość\n")
                continue
        except ValueError:
            print("Podaj poprawną wartość\n")
            continue
        else:
            break
    solveSatProblem()


def interrupt(s):
    s.interrupt()


def solveSatProblem():
    global x, sat_solver
    x = p * g

    print("\nGenerowanie problemu.")

    sat_solver = Glucose3(use_timer=True)
    genAllClauses()

    if show_additional_info:
        print("Klauzule: " + str(sat_solver.nof_clauses()))
        print("Zmienne: " + str(sat_solver.nof_vars()))

    print("\nSzukanie rozwiązania.")

    timer = Timer(time_budget, interrupt, [sat_solver])
    timer.start()

    sat_status = sat_solver.solve_limited(expect_interrupt=True)

    if sat_status is False:
        print("\nNie znaleziono. Rozwiązanie nie istnieje.")
    else:
        solution = sat_solver.get_model()
        if solution is None:
            print("Nie znaleziono. Przekroczono czas (" + '{0:.2f}s'.format(sat_solver.time()) + ").\n")
        else:
            print(
                "Znaleziono rozwiązanie w czasie " + '{0:.2f}s'.format(sat_solver.time()) + ". Trwa generowanie go.\n")
            wynik = []
            for v in solution:
                if v > 0:
                    ijkl = resolveVariable(v)
                    if len(ijkl) == 3:
                        i, k, l = ijkl
                        wynik.append({"i": i, "k": k, "l": l})

            ostateczny_wynik = processResults(wynik)
            showResults(ostateczny_wynik)

            if show_additional_info:
                sat_accum_stats = sat_solver.accum_stats()
                print("Restarty: " +
                      str(sat_accum_stats['restarts']) +
                      ", konflikty: " +
                      str(sat_accum_stats['conflicts']) +
                      ", decyzje: " +
                      str(sat_accum_stats['decisions']) +
                      ", propagacje: " +
                      str(sat_accum_stats["propagations"]))

        input("Naciśnij Enter aby kontynuować...")

    sat_solver.delete()


if __name__ == "__main__":
    mainMenu()