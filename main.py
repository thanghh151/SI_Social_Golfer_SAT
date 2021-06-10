from pysat.solvers import Glucose3
from prettytable import PrettyTable

w = 3 #liczba tygodni
p = 3 #gracze na grupe
g = 5 #liczba grup

x = p * g

sat_solver = Glucose3()


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


#co najmniej raz w tygodniu każdy golfista gra
def genClause1():
    for i in range(1, x+1):
        for l in range(1, w+1):
            loo = []
            for j in range(1, p+1):
                for k in range(1, g+1):
                    loo.append(getVariable(i, j, k, l))
            sat_solver.add_clause(loo)


#co najwyżej raz w tygodniu każdy golfista gra
def genClause2():
    for i in range(1, x+1):
        for l in range(1, w+1):
            for j in range(1, p+1):
                for k in range(1, g+1):
                    for m in range(j+1, p+1):
                        loo = []
                        loo.append(-1*getVariable(i, j, k, l))
                        loo.append(-1*getVariable(i, m, k, l))
                        sat_solver.add_clause(loo)


def genClause3():
    for i in range(1, x+1):
        for l in range(1, w+1):
            for j in range(1, p+1):
                for k in range(1, g+1):
                    for m in range(k+1, g+1):
                        for n in range(1, p+1):
                            loo = []
                            loo.append(-1*getVariable(i, j, k, l))
                            loo.append(-1*getVariable(i, n, m, l))
                            sat_solver.add_clause(loo)


def genClause4():
    for l in range(1, w+1):
        for k in range(1, g+1):
            for j in range(1, p+1):
                loo = []
                for i in range(1, x+1):
                    loo.append(getVariable(i, j, k, l))
                sat_solver.add_clause(loo)


def genClause5():
    for l in range(1, w + 1):
        for k in range(1, g + 1):
            for j in range(1, p + 1):
                for i in range(1, x + 1):
                    for m in range(i + 1, p + 1):
                        loo = []
                        loo.append(-1 * getVariable(i, j, k, l))
                        loo.append(-1 * getVariable(m, j, k, l))
                        sat_solver.add_clause(loo)


def genClause6():
    for i in range(1, x + 1):
        for k in range(1, g + 1):
            for l in range(1, w + 1):
                tab = []
                tab.append(-1 * getVariable2(i, k, l))
                for j in range(1, p + 1):
                    tab.append(getVariable(i, j, k, l))
                    tab2 = []
                    tab2.append(getVariable2(i, k, l))
                    tab2.append(-1 * getVariable(i, j, k, l))
                    sat_solver.add_clause(tab2)
                sat_solver.add_clause(tab)


def genClause7():
    for l in range(1, w+1):
        for k in range(1, g+1):
            for m in range(1, x+1):
                for n in range(m+1, x+1):
                    for k2 in range(1, g+1):
                        for l2 in range(l+1, w+1):
                            loo = []
                            loo.append(-1 * getVariable2(m, k, l))
                            loo.append(-1 * getVariable2(n, k, l))
                            loo.append(-1 * getVariable2(m, k2, l2))
                            loo.append(-1 * getVariable2(n, k2, l2))
                            sat_solver.add_clause(loo)


def genSymmetryBreakingClause1():
    for i in range(1, x+1):
        for j in range(1, p):
            for k in range(1, g+1):
                for l in range(1, w+1):
                    for m in range(1, i+1):
                        loo = []
                        loo.append(-1 * getVariable(i, j, k, l))
                        loo.append(-1 * getVariable(m, j+1, k, l))
                        sat_solver.add_clause(loo)


def genSymmetryBreakingClause2():
    for i in range(1, x+1):
        for k in range(1, g):
            for l in range(1, w+1):
                for m in range(1, i):
                    loo = []
                    loo.append(-1 * getVariable(i, 1, k, l))
                    loo.append(-1 * getVariable(m, 1, k+1, l))
                    sat_solver.add_clause(loo)


def genSymmetryBreakingClause3():
    for i in range(1, x+1):
        for l in range(1, w):
            for m in range(1, i+1):
                loo = []
                loo.append(-1 * getVariable(i, 2, 1, l))
                loo.append(-1 * getVariable(m, 2, 1, l+1))
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
    for i in range(1, x+1):
        for l in range(1, w+1):
            for j in range(1, p+1):
                for k in range(1, g+1):
                    if abs(v) == getVariable(i, j, k, l):
                        return i, j, k, l
    for i in range(1, x+1):
        for l in range(1, w+1):
            for k in range(1, g+1):
                if abs(v) == getVariable2(i, k, l):
                    return i, k, l
    return


def showResults(wyn):
    tab=[]
    for row in wyn:
        if row["v"] == True:
            tab.append(row)
    ntab={}
    for tyg in range(1,w+1):
        ntab[tyg] = {}
        for grp in range(1, g+1):
            ntab[tyg][grp]=[]
    for row in tab:
        ntab[row["l"]][row["k"]].append(row["i"])
    return ntab


def showResults2(wyn):
    x = PrettyTable()
    field_names = []
    field_names.append("Tydzien")
    for grupa in range(1, g+1):
        field_names.append("Grupa " + str(grupa))
    x.field_names = field_names
    for tyg in range(1, w+1):
        row = [str(tyg)]
        for grupa in range(1, g+1):
            row.append(str(",".join(list(map(str, wyn[tyg][grupa])))))
        x.add_row(row)
    print(x)


def menu():
    global w, p, g
    while True:
        try:
            w = int(input("Podaj liczbę tygodni\n"))
            if w <= 0:
                print("Podaj poprawną wartość\n")
                continue
            p = int(input("Podaj liczbę graczy w grupie\n"))
            if p <= 0:
                print("Podaj poprawną wartość\n")
                continue
            g = int(input("Podaj liczbę grup\n"))
            if g <= 0:
                print("Podaj poprawną wartość\n")
                continue
        except ValueError:
            print("Podaj poprawną wartość\n")
            continue
        else:
            break
    solveSatProblem()


def solveSatProblem():
    global x
    x = p * g
    genAllClauses()
    #sat_solver.conf_budget(1000000)
    satsolvd = sat_solver.solve_limited()
    if satsolvd == False:
        print("Nie znaleziono.")
    else:
        jakas_zmienna = sat_solver.get_model()
        wynik = []
        wynik2 = []
        for v in jakas_zmienna:
            ijkl = resolveVariable(v)
            if len(ijkl) == 4:
                i, j, k, l = ijkl
                if v < 0:
                    wynik.append({"v": False, "i": i, "j": j, "k": k, "l": l})
                else:
                    wynik.append({"v": True, "i": i, "j": j, "k": k, "l": l})
            else:
                i, k, l = ijkl
                if v < 0:
                    wynik2.append({"v": False, "i": i, "k": k, "l": l})
                else:
                    wynik2.append({"v": True, "i": i, "k": k, "l": l})
        ostatecznyWynik = showResults(wynik)
        print("Klauzule: " + str(sat_solver.nof_clauses()))
        print("Zmienne: " + str(sat_solver.nof_vars()))
        showResults2(ostatecznyWynik)


if __name__ == "__main__":
    menu()