# x = [
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FL090",
#     "STM|BW010",
#     "STM|BW010",
#     "STM|BL010",
#     "STM|FW010",
#     "STM|FW010",
#     "STM|FW010",
#     "RPI|TOCAM",
#     "RPI_END|0"
# ]

# # for i, v in enumerate(x):
# #     if i==0:
# #         print(v)
# #     elif v!=x[i-1]:
# #         print(v)
# #     elif v==x[ii ]
# # print([v for i, v in enumerate(x) if i == 0 or v != x[i-1]])

# # list1 = [-1, -1, 1, 1, 1, -1, 1]
# grouped_L = [(k, sum(1 for i in g)) for k,g in groupby(x)]
# print(grouped_L)
# new_cmds=[]
# for i in grouped_L:
#     cmd = i[0].split("|",1)[1]
#     if cmd=="FW010":
#         newCmd = "STM|FW0"+str(i[1])+"0"
#         new_cmds.append(newCmd)
#     elif cmd=="BW010":
#         newCmd = "STM|BW0"+str(i[1])+"0"
#         new_cmds.append(newCmd)
#     else:
#         new_cmds.append(i[0])
# print(new_cmds)