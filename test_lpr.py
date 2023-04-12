#!/usr/bin/python3
from pulp import *
import sys
import network_gen as ng
from prg import *

#print("========== Generate topology ==========")
nov = 50    # the number of vertices of the QKD network
prob = 0.3  # the probability of generating edges in the QKD network
UG = ng.gen(nov,prob)   # generate the undirected topology
DG = ng.ug2dg(UG)       # generate the directed topology

nodes = list(UG.nodes)  # the list of nodes
edges = list(UG.edges)  # the list of undirected edges
#for e in edges:
#    channels = UG.edges[e]["channel"]
#    cap = UG.edges[e]["cap"]
    #print(f"edges: {e}, channels: {channels}, capacity: {cap}")
d_edges = list(DG.edges)    # the list of directed edges

# the set of demands
# the format of a demand: D_i = (s_i,d_i,k_i,r_i)
# s_i: the source
# d_i: the destination
# k_i: the number of the remaining keys
# r_i: the consumption rate (keys/time slot)
#print("========== The set of demands ==========")
#l_argv = sys.argv
#l_argv.pop(0)
#l_demand = list()
#for i in l_argv:
#    j = i.strip()
#    j = j.replace('(','').replace(')','')
#    j = j.split(',')
#    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
#demands = l_demand
#demands = [(1,2,6,4),(10,20,8,5),(3,7,10,3)]

demands = [(18,35,12,1),(40,12,20,1),(31,27,7,1),(11,18,13,1),(37,28,13,1),(40,49,14,1)]
demands_total_flow = dict()
for d in demands:
    demands_total_flow[d] = 0

(obj,f_i_uv,f_i) = relaxed_program(UG,DG,demands)

#print(f"Objective: {obj}")

#for var in f_i_uv:
#    print(var,"=",f_i_uv[var],"=",int(f_i_uv[var].varValue))

#for var in f_i:
#    print(var,"=",f_i[var],"=",int(f_i[var].varValue))

demand_edge = dict()
for d in demands:
    demand_edge[d] = dict()

for var in f_i_uv:
    if f_i_uv[var].varValue > 0:
        demand_edge[var[0]][var[1]] = f_i_uv[var].varValue

flow_list = dict()
for d in demands:
    if demand_edge[d] == {}: continue   # if a demand doesn't have flow because its remaining time slots exceeds the objective. In other words, it has not been served
                                        # therefore, some demands is not in the flow_list
    temp_total_flow = 0
    flow_list[d] = ng.det_flow(d,demand_edge[d])
    for e in flow_list[d]:
        if e[0] == d[0]: temp_total_flow = temp_total_flow + flow_list[d][e]
    demands_total_flow[d] = demands_total_flow[d] + temp_total_flow

# update the network and demands
cap_used = dict()
for d in demands:
    if d in flow_list:
        for e in flow_list[d]:
            if e[0] > e[1]: temp_e = (e[1],e[0])
            else: temp_e = e
            if temp_e not in cap_used: cap_used[temp_e] = flow_list[d][e]
            else: cap_used[temp_e] = cap_used[temp_e] + flow_list[d][e]
        #print(demand_edge[d])
        #print("=================================================================================")
        #print(flow_list[d])
        #print("=================================================================================")

print(cap_used)

node_cap_used = dict()
for (u,v) in cap_used:
    if u not in node_cap_used: node_cap_used[u] = cap_used[(u,v)]
    else: node_cap_used[u] = node_cap_used[u] + cap_used[(u,v)]

    if v not in node_cap_used: node_cap_used[v] = cap_used[(u,v)]
    else: node_cap_used[v] = node_cap_used[v] + cap_used[(u,v)]

fptr = open("log.txt","w")

fptr.write("The status of the network before updating\n")
#for e in edges:
#    total_cap_e = UG.edges[e]["tot_cap"]
#    fptr.write(f"edge: {e}, total capacity: {total_cap_e}\n")
for v in nodes:
    node_cap = UG.nodes[v]["cap"]
    fptr.write(f"node: {v}, total capacity: {node_cap}\n")
fptr.write("==================================================================\n")
UG = ng.network_update(node_cap_used,cap_used,UG)
fptr.write("The status of the network after updating\n")
#for e in list(UG.edges):
#    total_cap_e = UG.edges[e]["tot_cap"]
#    fptr.write(f"edge: {e}, total capacity: {total_cap_e}\n")
for v in list(UG.nodes):
    node_cap = UG.nodes[v]["cap"]
    fptr.write(f"node: {v}, total capacity: {node_cap}\n")

print(demands_total_flow)