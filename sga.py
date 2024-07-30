def check_sga(v, k, r):
    def ks_exists(v, k):
        return v % k == 0 and (v - 1) % (k - 1) == 0

    def kts_exists(v):
        return v % 6 == 3 and v >= 9

    def nkts_exists(v):
        return v % 6 == 0 and v >= 18

    def find_design(v, k):
        if isinstance(k, list):
            for ki in k:
                result = find_design(v, ki)
                if result != "Unknown":
                    return result
            return "Unknown"
        else:
            if ks_exists(v, k):
                return f"KS({v}, {k})"
            elif kts_exists(v):
                return f"KTS({v}, {k})"
            elif nkts_exists(v):
                return f"NKTS({v})"
            elif v == 16 and k == 4:
                return "RTD(4, 5)"
            else:
                return "Unknown"

    def find_alternative_design(v, k):
        k_min = min(k) if isinstance(k, list) else k
        for delta_v in range(-k_min, k_min + 2):
            for delta_k in [0, 1]:
                new_v = v + delta_v
                new_k = [k_ + delta_k for k_ in (k if isinstance(k, list) else [k])]
                design = find_design(new_v, new_k)
                if design != "Unknown":
                    return design
        return "Unknown"

    # Check for invalid inputs
    if v < 12:
        return False, "v phải lớn hơn hoặc bằng 12"
    
    # Normalize k to a list if it's a single value
    if isinstance(k, int):
        k = [k]
    elif len(k) > 2 or (len(k) == 2 and abs(k[0] - k[1]) > 1):
        return False, "k không hợp lệ"
    
    # Additional constraints for v >= 20
    if v >= 20 and (min(k) < 4 or max(k) > 6):
        return False, "Với v >= 20, kích thước nhóm phải từ 4 đến 6"
    
    # Attempt to find valid (m1, m2) pairs
    valid_pairs = []
    if len(k) == 1:
        if v % k[0] == 0:
            valid_pairs.append((v // k[0], 0))
    else:
        k1, k2 = k[0], k[1]
        for m1 in range(v // k1 + 1):
            m2 = (v - m1 * k1) // k2
            if m1 * k1 + m2 * k2 == v and m2 >= 0:
                valid_pairs.append((m1, m2))
    
    if not valid_pairs:
        return False, "Không tìm thấy cặp (m1, m2) thỏa mãn"
    
    # Check for solutions
    solutions = []
    for m1, m2 in valid_pairs:
        k_min = min(k)
        denominator = k_min * (m1 * (k_min - 1) + m2 * (k_min + 1))
        if denominator == 0:
            continue
        R = v * (v - 1) // denominator
        
        if r > R:
            continue
        
        # Specific cases to exclude
        if v == 20 and k == [4] and r == R:
            continue
        if v == 36 and k == [6] and r > 3:
            continue
        
        # Find the design for the current values
        design = find_design(v, k_min)
        if design == "Unknown":
            design = find_alternative_design(v, k)
        if len(k) == 2:
            design += f" - {m2}"
        
        solutions.append((m1, m2, R, design))
    
    # Format the result
    if solutions:
        result = f"Có thể có giải pháp cho SGA({v},{k},{r}) với các cặp (m1, m2) sau:\n"
        for m1, m2, R, design in solutions:
            result += f"v={v} k={k} m1={m1}, m2={m2} R={R} Design: {design}\n"
        return True, result.strip()
    else:
        return False, "Không tìm thấy giải pháp thỏa mãn tất cả điều kiện"

# Ví dụ sử dụng
print(check_sga(12, 3, 4))
print(check_sga(12, [3, 4], 4))
print(check_sga(13, [3, 4], 5))
print(check_sga(15, 3, 7))
print(check_sga(16, 4, 5))
print(check_sga(18, 3, 8))
