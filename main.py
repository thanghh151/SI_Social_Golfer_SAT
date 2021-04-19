from pysat.solvers import Glucose3

w = 3
p = 2
g = 2

x = p * g

sat_solver = Glucose3()

def genAllClauses():
    genClause1()
    genClause2()

def genClause1():
    for i in range(1, x+1):
        for l in range(1, w+1):
            loo = []
            for j in range(1, p+1):
                for k in range(1, g+1):
                    loo.append(getVariable(i, j, k, l))
            sat_solver.add_clause(loo)


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

def getVariable(i, j, k, l):
    i -= 1
    j -= 1
    k -= 1
    l -= 1
    return i + (x * j) + (k * x * p) + (l * x * p * g) + 1


def resolveVariable(v):
    for i in range(1, x+1):
        for l in range(1, w+1):
            for j in range(1, p+1):
                for k in range(1, g+1):
                    if abs(v) == getVariable(i, j, k, l):
                        return i, j, k, l
    return -2137


if __name__ == "__main__":
    genAllClauses()
    print(sat_solver.solve())
    jakas_zmienna = sat_solver.get_model()
    wynik = []
    for v in jakas_zmienna:
        i, j, k, l = resolveVariable(v)
        if v < 0:
            wynik.append({"v": False, "i":i, "j":j, "k":k, "l":l})
        else:
            wynik.append({"v": True, "i":i, "j":j, "k":k, "l":l})
    for row in wynik:
        print(row)
