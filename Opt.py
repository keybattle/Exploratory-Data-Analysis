__author__ = 'Yaji'

from pulp import *
import pandas as pd
import numpy as np

file1=pd.read_csv("Decision.txt")
file2=pd.read_csv("distance.csv")
file3=pd.read_csv("inventory_single.csv")
file4=pd.read_csv("Order.txt")

distance=file2.pivot("dc_id","zip","zone_id").fillna(2).sort_index()
single_upc=file1.loc[file1['Categories']=='Single UPC - Single Unit']
index=single_upc["order_no"]
order=file4.loc[file4['order_no'].isin(index)]
inventory=file3.pivot("item_id","dc_id","ats").fillna(0).sort_index(axis=1)
demand=pd.pivot_table(order,index= 'item_id', columns='zip',values='quantity',aggfunc=np.sum).fillna(0)

current_zone=order['ship_to_zone'].mean()

FC=list(distance.index.values)
common_zip=list(set(distance.columns.values)&set(demand.columns.values))
common_upc=list(set(demand.index.values)&set(inventory.index.values))
I=[i for i in range(len(FC))]
J=[j for j in range(len(common_zip))]
K=[k for k in range(len(common_upc))]

zip_drop1=[n for n in distance.columns.values if n not in common_zip]
zip_drop2=[n for n in demand.columns.values if n not in common_zip]
upc_drop1=[n for n in inventory.index.values if n not in common_upc]
upc_drop2=[n for n in demand.index.values if n not in common_upc]
distance=distance.drop(zip_drop1,axis=1)
demand=demand.drop(zip_drop2,axis=1)
inventory=inventory.drop(upc_drop1,axis=0)
demand=demand.drop(upc_drop2,axis=0)
order2=order.loc[order['item_id'].isin(common_upc)]
current_zone2=order2['ship_to_zone'].mean()
number_of_order=len(order2.index)
total_zone_byupc=order2.groupby('item_id').sum().ship_to_zone

"""
print distance[:10]
print demand[:10]
print inventory[:10]
"""
"""
print demand.shape
print inventory.shape
print len(common_upc)
print distance[:10]
print demand[:10]
print len(upc_drop1)
print len(upc_drop2)
"""

def LP(UPC):
    D=list(demand.loc[UPC])
    S=list(inventory.loc[UPC])
    prob = LpProblem("Shipping", LpMinimize)
    assign_vars=LpVariable.dicts("X",[(i,j) for i in I
                                           for j in J],
                             0,1,LpBinary)
    prob += lpSum(distance.iloc[i,j]*assign_vars[(i,j)] for i in I for j in J)
    for i in I:
        prob +=lpSum(assign_vars[(i,j)] for j in J)<=S[i]
    for j in J:
        prob +=lpSum(assign_vars[(i,j)] for i in I)>=D[j]
    prob.solve()
    """
    var_list=[]
    for v in prob.variables():
        if v.varValue==1:
            var_list.append(v.name)
    """
    return value(prob.objective) #,var_list

zone=0
bad_upc=[]

for UPC in common_upc:
    zone_temp=LP(UPC)
    zone+=zone_temp
    if zone_temp<total_zone_byupc.loc[UPC]:
        bad_upc.append(UPC)

optimal_zone=float(zone)/number_of_order
print optimal_zone
print current_zone2
print bad_upc
#print len(LP(15522243)[1])
#print total_zone_byupc.loc[15522243]

