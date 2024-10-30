from ortools.sat.python import cp_model

# Các tham số bài toán
num_players = 13  # Tổng số người chơi
num_weeks = 4     # Số tuần
players_per_group = [3, 4]

# Tạo model
model = cp_model.CpModel()

# Tính toán số nhóm và các m1, m2
def find_all_valid_combinations(num_players, player_per_group):
    valid_combinations = set()

    k1 = players_per_group[0]
    k2 = players_per_group[1] if len(players_per_group) > 1 else None

    # Số lượng nhóm tối đa
    max_groups = num_players // min(players_per_group)

    for num_groups in range(2, max_groups + 1):
        for m1 in range(0, num_players // k1 + 1):
            for m2 in range(0, num_players // k2 + 1 if k2 is not None else 1):
                if k2 is not None:
                    if m1 * k1 + m2 * k2 == num_players and m1 + m2 == num_groups:
                        valid_combinations.add((k1, k2, m1, m2, num_groups))
                else:
                    if m1 * k1 == num_players and m1 == num_groups:
                        valid_combinations.add((k1, None, m1, 0, num_groups))

    return list(valid_combinations)

# Gọi hàm để tìm các kết hợp hợp lệ
valid_combinations = find_all_valid_combinations(num_players, players_per_group)
print("Valid combinations (k1, k2, m1, m2, num_groups):", valid_combinations)

# Sử dụng số nhóm tính toán được để tạo biến cho mỗi người chơi, nhóm và tuần
num_groups = valid_combinations[0][4]  # Chọn một kết hợp hợp lệ (chỉ ví dụ, có thể chọn cái khác)
m2 = valid_combinations[0][3]
variables = {}
for player in range(1, num_players + 1):
    for group in range(1, num_groups + 1):
        for week in range(1, num_weeks + 1):
            variables[(player, group, week)] = model.NewBoolVar(f'player_{player}_group_{group}_week_{week}')

def get_variable(golfer, group, week):
    return variables[(golfer, group, week)]

# Ràng buộc: Mỗi người chơi chỉ xuất hiện trong một nhóm mỗi tuần
for player in range(1, num_players + 1):
    for week in range(1, num_weeks + 1):
        model.AddExactlyOne(variables[(player, group, week)] for group in range(1, num_groups + 1))

# Ràng buộc: Mỗi nhóm phải có một số lượng người chơi nhất định mỗi tuần
for week in range(1, num_weeks + 1):
      if m2 > 0:
          for group in range(1, m2 + 1):
              model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[1])

          for group in range(m2 + 1, num_groups + 1):
              model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[0])
      else:
          for group in range(1, num_groups + 1):
              model.Add(sum(variables[(player, group, week)] for player in range(1, num_players + 1)) == players_per_group[0])

# Áp dụng các ràng buộc không cho phép golfer1 và golfer2 xuất hiện cùng nhau
for week in range(1, num_weeks + 1):
    for group in range(1, num_groups + 1):
        for golfer1 in range(1, num_players + 1):
            for golfer2 in range(golfer1 + 1, num_players + 1):
                for other_group in range(1, num_groups + 1):
                    for other_week in range(week + 1, num_weeks + 1):
                        model.AddBoolOr([
                            get_variable(golfer1, group, week).Not(),
                            get_variable(golfer2, group, week).Not(),
                            get_variable(golfer1, other_group, other_week).Not(),
                            get_variable(golfer2, other_group, other_week).Not()
                        ])

# Ràng buộc theo cấu trúc ban đầu
# for p1 in range(1, num_players):
#     for p2 in range(p1 + 1, num_players + 1):
#         M = [model.NewBoolVar(f'M_{p1}_{p2}_week_{week}') for week in range(num_weeks)]

#         # (1) M[0] = False
#         model.Add(M[0] == 0)

#         # (2) G[p1, k, l] and G[p2, k, l] -> M[l]
#         for k in range(1, num_groups + 1):
#             for l in range(1, num_weeks):
#                 model.AddBoolOr([
#                     get_variable(p1, k, l).Not(),
#                     get_variable(p2, k, l).Not(),
#                     M[l]
#                 ])

#         # (3) M[l-1] -> M[l]
#         for l in range(1, num_weeks):
#             model.AddImplication(M[l - 1], M[l])

#         # (4) M[l-1] -> not (G[p1, k, l] and G[p2, k, l])
#         for k in range(1, num_groups + 1):
#             for l in range(1, num_weeks + 1):
#                 model.AddBoolOr([
#                     M[l - 1].Not(),
#                     get_variable(p1, k, l).Not(),
#                     get_variable(p2, k, l).Not()
#                 ])

#         # (5) not M[l-1] and not (G[p1, k, l] and G[p2, k, l]) -> not M[l]
#         for k in range(1, num_groups + 1):
#             for l in range(1, num_weeks):
#                 model.AddBoolOr([
#                     M[l - 1],
#                     get_variable(p1, k, l).Not(),
#                     get_variable(p2, k, l).Not(),
#                     M[l].Not()
#                 ])

# Giải quyết vấn đề
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Hàm hiển thị giải pháp
def display_solution():
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution Found:")
        for week in range(1, num_weeks + 1):
            print(f"\nWeek {week}:")
            for group in range(1, num_groups + 1):
                group_members = []
                for player in range(1, num_players + 1):
                    if solver.Value(variables[(player, group, week)]):
                        group_members.append(str(player))
                print(f"  Group {group}: " + ", ".join(group_members))
    else:
        print("No solution found.")

# Gọi hàm hiển thị kết quả
display_solution()
