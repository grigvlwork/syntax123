with open("17.txt") as f:
    l = [el.strip() for el in f.readlines()]
    print(l[:10])

# def check(a, b, c, d):
#     arr = [int(a), int(b), int(c), int(d)]
#     h, l = 0, 0
#     for x in arr:
#         if x > 1000:
#             h += 1
#         else:
#             l += 1
#     if h == 2 and l == 2:
#         return True
#     else:
#         return False
# def max47(arr):
#     res = []
#     for el in arr:
#         if str(el)[-2:] == "47":
#             res.append(el)
#     return max(res)
# res = []
# for i in range(len(l)-4):

#     if check(l[i], l[i+1], l[i+2], l[i+3]):
#         if summ := sum((int(l[i]), int(l[i+1]), int(l[i+2]), int(l[i+3]))) <= max47(l):
#             res.append(summ)
# print(len(res), max(res))