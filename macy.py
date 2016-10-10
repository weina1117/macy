#!/usr/bin/python

from gurobipy import Model, GRB, GurobiError
import pandas as pd

#
# There are 9 categories:c1,c2,c3,c4,c5,c6,c7,c42,c64. We map the category number to our variable index.
# The record number is 2096, which is the 1st dimension of our variables.
# Since the conversion rate is independent with the click rate of emails, we have to make some
# assumptions here. To analyze the usefulness of the emails, we will have to suppose to conditions
# here, one is that all the conversions are not related to the email, and the other is its opposite condition.
# If the conversion is fully related to the emails at all the obj function of the problem will be:
# maximize \sum_{i=1}^{2096}sizes_i\sum_{j=1}^{24}cs_j*aov_j
ncategory = 9
nrecords = 2096
def loadData(filename):
    df = pd.read_csv(filename)
    sizes = list(df.iloc[:, 1])
    cs = [list(df.iloc[:, i]) for i in range(2, 26)]
    aovs = [list(df.iloc[:, i]) for i in range(26, 50)]
    ems = [list(df.iloc[:, i]) for i in range(50, 60)]
    return (sizes, cs, aovs, ems)

# We have em1,em2,em3,em4,em5,em6,em7,em42,em43,em64, and we will remove em43, since it does not exist in other
# parameters, then we will have
#         em0,em1,em2,em3,em4,em5,em6,em12,em18
def fixEms(ems):
    avg = [sum([ems[i][j] for i in range(len(ems))])/len(ems) for j in range(len(ems[0]))]
    ret = [[] for _ in range(ncategory)]
    for i in range(len(ret)):
        if i >= 0 and i <= 6:
            ret[i] = ems[i]
            continue
        if i == 7:
            ret[12] = ems[i]
            ret[7] = list(avg)
            continue
        if i == 8:
            ret[18] = ems[i]
            ret[8] = list(avg)
            continue
        ret[i] = list(avg)
    return ret



def createVariables(m):
    vars = [[] for _ in range(ncategory)]
    for i in range(ncategory):
        vars[i] = [0 for _ in range(nrecords)]
        for j in range(nrecords):
            vars[i][j] = m.addVar(lb=0, vtype=GRB.INTEGER, name="v["+str(i)+"]["+str(j)+"]")
    return vars


def main():
    try:
        (sizes, cs, aovs, ems) = loadData('./data.csv')
        cs = cs[:7] + cs[12:13] + cs[18:19]
        aovs = aovs[:7] + aovs[12:13] + aovs[18:19]
        # ems = fixEms(ems)

        # Create a new model
        m = Model("mip1")

        # Create variables
        vars = createVariables(m)

        # Integrate new variables
        m.update()

        # maximize \sum_{i=1}^{2096}sizes_i\sum_{j=1}^{24}cs_j*aov_j
        # Set objective
        m.setObjective(sum([sum([cs[i][j]*aovs[i][j]*vars[i][j] for i in range(ncategory)])*sizes[j] for j in range(nrecords)]),
                       GRB.MAXIMIZE)

        # c1,c2,c3,c4,c5,c6,c7,c42,c64
        # v0,v1,v2,v3,v4,v6,v6,v7, v8
        # Add constraints: sum([vars[7][j]+vars[8][j]+vars[9][j] for j in range(nrecords)]) == sum([vars[0][j] for j in range(nrecords)])
        m.addConstr(sum([vars[7][j] for j in range(nrecords)]) <= sum([vars[3][j] for j in range(nrecords)]))
        m.addConstr(sum([vars[8][j] for j in range(nrecords)]) <= sum([vars[5][j] for j in range(nrecords)]))

        m.addConstr(sum([vars[7][j] for j in range(nrecords)]) <= 18000)
        m.addConstr(sum([vars[7][j] for j in range(nrecords)]) >= 8000)
        m.addConstr(sum([vars[8][j] for j in range(nrecords)]) <= 6000)
        m.addConstr(sum([vars[8][j] for j in range(nrecords)]) >= 3000)
        m.addConstr(sum([vars[0][j] for j in range(nrecords)]) <= 25000)
        m.addConstr(sum([vars[0][j] for j in range(nrecords)]) >= 10000)
        m.addConstr(sum([vars[1][j] for j in range(nrecords)]) <= 8500)
        m.addConstr(sum([vars[1][j] for j in range(nrecords)]) >= 5000)
        m.addConstr(sum([vars[2][j] for j in range(nrecords)]) <= 8000)
        m.addConstr(sum([vars[2][j] for j in range(nrecords)]) >= 1500)
        m.addConstr(sum([vars[3][j] for j in range(nrecords)]) <= 10000)
        m.addConstr(sum([vars[3][j] for j in range(nrecords)]) >= 4000)
        m.addConstr(sum([vars[4][j] for j in range(nrecords)]) <= 8000)
        m.addConstr(sum([vars[4][j] for j in range(nrecords)]) >= 1500)
        m.addConstr(sum([vars[5][j] for j in range(nrecords)]) <= 20000)
        m.addConstr(sum([vars[5][j] for j in range(nrecords)]) >= 9000)
        m.addConstr(sum([vars[6][j] for j in range(nrecords)]) <= 15000)
        m.addConstr(sum([vars[6][j] for j in range(nrecords)]) >= 8000)
        for j in range(nrecords):
            m.addConstr(sum([vars[i][j] for i in range(0, 9)]) <= 3*sizes[j])
        m.update()
        m.optimize()
        m.write("./macy.lp")

        for v in m.getVars():
            print v.varName, v.x

        print 'Obj:', m.objVal

    except GurobiError:
        print 'Error reported: {}'.format(GurobiError)

if __name__ == '__main__':
    main()
