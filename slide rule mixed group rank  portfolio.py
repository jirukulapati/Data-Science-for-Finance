import pandas as pd
import numpy as np
import itertools
import scipy.stats as ss
from sklearn.linear_model import LogisticRegression
from scipy import sparse
import matplotlib.pyplot as plt
#load data into data frame, may have to change file path.  Also make sure the excel file is saved as a CSV file
stockdata = pd.read_csv("C:\Users\Jason\Desktop\Computational finance\CompFinResearch\Data\Hsu Stock Data(CSV).csv",
                        header=None)

#assigns specific feature info to specific dataframe
t = ['Date', 'IS_EPS', 'EBITDA', 'PROF_MARGIN', 'PE_RATIO', 'CASH_FLOW_PER_SH', 'PX_TO_BOOK_RATIO', 'CURR_ENTP_VAL',
     'PX_VOLUME', 'RETURN_COM_EQY']
x = stockdata.loc[~stockdata[0].isin(t)]
x = x.dropna(how='all')
y = stockdata.loc[stockdata[0] == 'Date']
y = y.iloc[0, :].tolist()[1:len(y)-1]
a = stockdata.loc[stockdata[0] == 'IS_EPS']
b = stockdata.loc[stockdata[0] == 'EBITDA']
c = stockdata.loc[stockdata[0] == 'PROF_MARGIN']
d = stockdata.loc[stockdata[0] == 'PE_RATIO']
e = stockdata.loc[stockdata[0] == 'CASH_FLOW_PER_SH']
f = stockdata.loc[stockdata[0] == 'PX_TO_BOOK_RATIO']
g = stockdata.loc[stockdata[0] == 'CURR_ENTP_VAL']
h = stockdata.loc[stockdata[0] == 'PX_VOLUME']
i = stockdata.loc[stockdata[0] == 'RETURN_COM_EQY']

attributes = [a, b, c, d, e, f, g, h, i]
avg_att = []

for n in attributes:
    j = n.drop(n.columns[0], axis=1)
    l = j.apply(pd.to_numeric, errors='coerce')
    h = l.mean(axis=1)
    avg_att.append(h)

data_arrays = []
for k in avg_att:
    j = map(float, k.as_matrix())
    l = np.asarray(j).T
    data_arrays.append(l)

names = x[0].as_matrix().T
data_matrix = np.column_stack(data_arrays)

clean_data_matrix = data_matrix[~np.any(np.isnan(data_matrix), axis=1)]
clean_data_matrix = clean_data_matrix * np.array([1, 1, 1, -1, -1, 1, 1, -1, 1])
clean_names = names[~np.any(np.isnan(data_matrix), axis=1)]

data_vectors = []
for i in range(0, 9):
    j = clean_data_matrix[:, i]
    data_vectors.append(j)


scores = []
for i in data_vectors:
    z = (1/(max(i)-min(i)))*(i-(min(i) * (np.ones(np.shape(i)))))
    scores.append(z)

ranks = []
for i in scores[0:9]:
    j = ss.rankdata(i, method="min")
    j = (j.shape[0])*(np.ones(np.shape(j))) - j + 1
    ranks.append(j)


top_scores = [scores[0], scores[2], scores[3], scores[4], scores[6], scores[7]]
#Features: ACDFG
top_ranks = [ranks[0], ranks[2], ranks[3], ranks[4], ranks[6], ranks[7]]
top_ranks_int = []
for i in top_ranks:
    a = i.astype(int)
    top_ranks_int.append(a)


rank_matrix = np.column_stack(top_ranks_int)

model = LogisticRegression()
model.fit(rank_matrix, ranks[8])

weights = model.coef_

weights = np.split(weights, len(top_ranks), axis=1)

rank_comb = []
weight_comb = []

for i in range(1, len(top_ranks) + 1):
    a = list(itertools.combinations(top_ranks, i))
    b = list(itertools.combinations(weights, i))
    rank_comb = rank_comb + a
    weight_comb = weight_comb + b

mgr = []

for i in range(0, len(rank_comb)):
    j = []
    k = []

    for count in range(0, len(rank_comb[i])+1):
        g = list(itertools.combinations(rank_comb[i], count))
        h = list(itertools.combinations(weight_comb[i], count))
        j = j + g
        k = k + h

    j = [x for x in j if x != ()]
    k = [x for x in k if x != ()]
    k2 = []
    j2 = []

    for m in range(0, len(k)):
        v = reduce(lambda x, y: np.multiply(x, y), k[m])
        k2.append(v)

    for n in range(0, len(j)):
        x = np.column_stack(j[n])
        j2.append(x)

    rowlist = []

    for o in range(0, np.shape(j2[0])[0]):
        l = []
        for p in range(0, len(j2)):
            d = -1 * k2[p][o] * min(j2[p][o])
            l.append(d)
        t = sum(l)
        rowlist.append(t)
    rowMatrix = np.stack(rowlist)

    mgr.append(rowMatrix)

rank_mat = []


newScore = np.reshape(scores[8], (1903, 1))

for i in range(0, len(mgr)):
    j = np.concatenate([mgr[i], newScore], axis=1)
    rank_mat.append(j)

rank_sorts = []
for i in rank_mat:
    j = i[i[:, 0].argsort()]
    rank_sorts.append(j)

rank_perf = []

#since MGR is a score function
for i in rank_sorts:
    j = np.mean(i[:, 1][0:100])
    rank_perf.append(j)

comb_labels = []
for i in range(1, len(top_ranks)+1):
    a = list(itertools.combinations('ACDFGH', i))
    comb_labels = comb_labels + a


labels = []
for i in comb_labels:
    a = ''.join(i)
    labels.append(a)

l = zip(labels, rank_perf)

one_feat = sorted(l[0:6], key=lambda x: x[1])
two_feat = sorted(l[6:21], key=lambda x: x[1])
three_feat = sorted(l[21:41], key=lambda x: x[1])
four_feat = sorted(l[41:56], key=lambda x: x[1])
five_feat = sorted(l[56:62], key=lambda x: x[1])
six_feat = l[62]
k = one_feat + two_feat + three_feat + four_feat + five_feat
k.append(six_feat)

[combinations, rank_y] = zip(*k)
combinations = list(combinations)


AG = np.c_[clean_names, rank_mat[9]]
ACG = np.c_[clean_names, rank_mat[23]]
AFGH = np.c_[clean_names, rank_mat[50]]

pred1sort = AG[AG[:, 1].argsort()]
pred2sort = ACG[ACG[:, 1].argsort()]
pred3sort = AFGH[AFGH[:, 1].argsort()]

portfolio = []
for i in pred1sort[0:300]:
    if i in pred2sort[0:300]:
        if i in pred3sort[0:300]:
            portfolio.append(i[0])

AG_rank = AG[:,1]
ACG_rank = ACG[:, 1]
AFGH_rank = AFGH[:, 1]

agg_rank = np.mean((AG_rank, ACG_rank, AFGH_rank), axis=0)
agg_mat = np.c_[clean_names, agg_rank]

final_portfolio = []

for i in agg_mat:
    if i[0] in portfolio:
        final_portfolio.append(i)

[final_names, final_rank] = zip(*final_portfolio)

##normalized_scores = []
#for i in final_scores:
 #   j = (i - min(final_scores)) * (1/(max(final_scores)-min(final_scores)))
 #   normalized_scores.append(j)

portfolio_score = zip(final_names, final_rank)


portfolio_score.sort(key=lambda tup: tup[1])

best_portfolio = portfolio_score[0:99]

[stocknames, normal_scores] = zip(*best_portfolio)

final_weights = []
for i in normal_scores:
    j = i * (1/sum(normal_scores))
    final_weights.append(j)

investment = zip(stocknames, final_weights)
print stocknames
print list(reversed(final_weights))
print len(stocknames)


