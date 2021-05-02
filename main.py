from pysat.solvers import Glucose3

w = 3
p = 2
g = 2

x = p * g

sat_solver = Glucose3()


def genAllClauses():
    genClause1()
    genClause2()
    genClause3()
    genClause4()
    genClause5()



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
                        #print("j " + str(getVariable(i, j, k, l)))
                        #print("m " + str(getVariable(i, m, k, l)))


def genClause3():
    for i in range(1, x+1):
        for l in range(1, w+1):
            for j in range(1, p+1):
                for k in range(1, g+1):
                    for m in range(k+1, g+1):
                        for n in range(j+1, p+1):
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


#nie zrobiobione według pdf'a, gdyż mamy wątpliwości wobec tego co się tam znajduje
def genClause5():
    for l in range(1, w + 1):
        for k in range(1, g + 1):
            for j in range(1, p + 1):
                for i in range(1, x + 1):
                #i = 1
                    for m in range(i + 1, p + 1):
                        #print(x)
                        #print("ijkl: " + str(i) + " " + str(j) + " " + str(k) + " " + str(l))
                        #print("imkl: " + str(i) + " " + str(m) + " " + str(k) + " " + str(l))
                        loo = []
                        loo.append(-1 * getVariable(i, j, k, l))
                        loo.append(-1 * getVariable(i, m, k, l))
                        sat_solver.add_clause(loo)
                        #print("j " + str(getVariable(i, j, k, l)))
                        print("m " + str(m) + " j " + str(j) + " imkl: " + str(getVariable(m, j, k, l)))


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
    return


if __name__ == "__main__":
    genAllClauses()
    print(sat_solver.solve())
    jakas_zmienna = sat_solver.get_model()
    wynik = []
    for v in jakas_zmienna:
        print(v)
        i, j, k, l = resolveVariable(v)
        if v < 0:
            wynik.append({"v": False, "i":i, "j":j, "k":k, "l":l})
        else:
            wynik.append({"v": True, "i":i, "j":j, "k":k, "l":l})
    for row in wynik:
        print(row)
