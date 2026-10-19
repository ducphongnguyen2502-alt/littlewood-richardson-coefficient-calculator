import copy
import itertools
import graphviz
from itertools import permutations

# ==========================================
# YOUNG TABLEAU & RSK DATA STRUCTURES
# ==========================================

class YoungTableau:
    def __init__(self):
        self.tableau = []

    def insert(self, x):
        val_to_insert = x
        for r in range(len(self.tableau)):
            inserted_in_current_row = False
            for c in range(len(self.tableau[r])):
                if self.tableau[r][c] > val_to_insert:
                    self.tableau[r][c], val_to_insert = val_to_insert, self.tableau[r][c]
                    inserted_in_current_row = True
                    break 
            if not inserted_in_current_row:
                self.tableau[r].append(val_to_insert)
                return r, len(self.tableau[r]) - 1

        self.tableau.append([val_to_insert])
        return len(self.tableau) - 1, 0

    def get_rightmost_max_cell(self):
        max_val = -float('inf')
        max_r, max_c = -1, -1
        for r in range(len(self.tableau)):
            if len(self.tableau[r]) > 0:
                c = len(self.tableau[r]) - 1
                val = self.tableau[r][c]
                if val > max_val:
                    max_val = val
                    max_r, max_c = r, c
                elif val == max_val:
                    if c > max_c:
                        max_r, max_c = r, c
        return max_r, max_c

    def reverse_insert(self, r, c):
        val = self.tableau[r].pop(c)
        if len(self.tableau[r]) == 0:
            self.tableau.pop(r)
            
        for i in range(r - 1, -1, -1):
            for j in range(len(self.tableau[i]) - 1, -1, -1):
                if self.tableau[i][j] < val:
                    self.tableau[i][j], val = val, self.tableau[i][j]
                    break
        return val

    def get_word(self):
        word = []
        for row in reversed(self.tableau):
            word.extend([val for val in row if val != 0])
        return word

    def multiply(self, other_tableau):
        result_tableau = copy.deepcopy(self)
        for val in other_tableau.get_word():
            result_tableau.insert(val)
        return result_tableau

    def __mul__(self, other):
        return self.multiply(other)

    def get_shape(self):
        return [len(row) for row in self.tableau]

    def display(self, title="Young Tableau:"):
        """Display tableau. Automatically converts 0 values to [  ]."""
        print(f"{title}")
        for row in self.tableau:
            print(" ".join(f"[{' ' if val == 0 else val:^2}]" for val in row))
        print("-" * 35)

    def slide(self, r, c):
        while True:
            val_right = float('inf')
            if r < len(self.tableau) and c + 1 < len(self.tableau[r]):
                val_right = self.tableau[r][c + 1]
                
            val_down = float('inf')
            if r + 1 < len(self.tableau) and c < len(self.tableau[r + 1]):
                val_down = self.tableau[r + 1][c]

            if val_right == float('inf') and val_down == float('inf'):
                self.tableau[r].pop(c)
                if len(self.tableau[r]) == 0:
                    self.tableau.pop(r)
                break
 
            if val_right < val_down:
                self.tableau[r][c] = self.tableau[r][c + 1]
                self.tableau[r][c + 1] = 0
                c += 1
            else:
                self.tableau[r][c] = self.tableau[r + 1][c]
                self.tableau[r + 1][c] = 0 
                r += 1

    def jeu_de_taquin(self):
        for r in range(len(self.tableau) - 1, -1, -1):
            for c in range(len(self.tableau[r]) - 1, -1, -1):
                if self.tableau[r][c] == 0:
                    self.slide(r, c)


def rsk(top_row, bottom_row):
    if len(top_row) != len(bottom_row):
        raise ValueError("Both rows of the array must have the same length!")

    P = YoungTableau()
    Q = YoungTableau()
    biwords = sorted(zip(top_row, bottom_row))
    
    for q, p in biwords:
        r, c = P.insert(p)
        if r == len(Q.tableau):
            Q.tableau.append([q])
        else:
            Q.tableau[r].append(q)
            
    return P, Q


def inverse_rsk(P_input, Q_input):
    P = copy.deepcopy(P_input)
    Q = copy.deepcopy(Q_input)
    
    top_row, bottom_row = [], []
    while len(Q.tableau) > 0:
        r, c = Q.get_rightmost_max_cell()
        q_val = Q.tableau[r].pop(c)
        if len(Q.tableau[r]) == 0:
            Q.tableau.pop(r)
            
        p_val = P.reverse_insert(r, c)
        top_row.append(q_val)
        bottom_row.append(p_val)
        
    top_row.reverse()
    bottom_row.reverse()
    return top_row, bottom_row


def F(A_input, U_input, U0_input):
    A = copy.deepcopy(A_input)
    S_tableau = copy.deepcopy(A_input).tableau

    for r in range(len(S_tableau)):
        for c in range(len(S_tableau[r])):
            S_tableau[r][c] = 0

    U0_val, U_val = inverse_rsk(U_input, U0_input)

    for u0, u in zip(U0_val, U_val):
        r, c = A.insert(u)

        while r >= len(S_tableau):
            S_tableau.append([])

        while c >= len(S_tableau[r]):
            S_tableau[r].append(0)

        S_tableau[r][c] = u0

    S_result = YoungTableau()
    S_result.tableau = S_tableau
    return S_result


def F_inverse(S_input, V0_input):
    V0_working = copy.deepcopy(V0_input)
    inserted_cells = []
    
    for r in range(len(S_input.tableau)):
        for c in range(len(S_input.tableau[r])):
            val = S_input.tableau[r][c]
            if val != 0:
                inserted_cells.append((r, c, val))
                
    inserted_cells.sort(key=lambda x: (x[2], x[1], x[0]), reverse=True)
    u_row, v_row = [], []
    
    for r, c, u_val in inserted_cells:
        v_val = V0_working.reverse_insert(r, c)
        u_row.append(u_val)
        v_row.append(v_val)
        
    u_row.reverse()
    v_row.reverse()
    
    A_restored = V0_working
    U_restored, _ = rsk(u_row, v_row)
    return A_restored, U_restored


def get_skew_cells(shape_nu, shape_lambda):
    cells = []
    for r in range(len(shape_nu)):
        lambda_len = shape_lambda[r] if r < len(shape_lambda) else 0
        for c in range(lambda_len, shape_nu[r]):
            cells.append((r, c))
    return cells


def generate_reverse_filling(shape_nu, shape_lambda):
    cells = get_skew_cells(shape_nu, shape_lambda)
    sorted_cells = sorted(cells, key=lambda x: (x[0], -x[1]))
    
    T_skew, cell_by_label = {}, {}
    for i, cell in enumerate(sorted_cells, start=1):
        T_skew[cell] = i
        cell_by_label[i] = cell
    return T_skew, cell_by_label


def check_conditions_R1_R2(T_tableau, cell_by_label, total_size):
    pos_in_T = {}
    for r in range(len(T_tableau.tableau)):
        for c in range(len(T_tableau.tableau[r])):
            pos_in_T[T_tableau.tableau[r][c]] = (r, c)
  
    for k in range(1, total_size):
        r_k, c_k = cell_by_label[k]
        if (k + 1) in cell_by_label:
            r_k1, c_k1 = cell_by_label[k + 1]
            if r_k == r_k1:
                row_k, col_k = pos_in_T[k]
                row_k1, col_k1 = pos_in_T[k + 1]
                if not (row_k1 <= row_k and col_k1 > col_k):
                    return False

    for k in range(1, total_size + 1):
        r_k, c_k = cell_by_label[k]
        below_cell = (r_k + 1, c_k)
        h = next((label for label, cell in cell_by_label.items() if cell == below_cell), None)
        
        if h is not None:
            row_k, col_k = pos_in_T[k]
            row_h, col_h = pos_in_T[h]
            if not (row_h > row_k and col_h <= col_k):
                return False

    return True


def is_standard_young_tableau(T_tableau):
    grid = T_tableau.tableau
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if c + 1 < len(grid[r]) and grid[r][c] >= grid[r][c + 1]:
                return False
            if r + 1 < len(grid) and c < len(grid[r + 1]) and grid[r][c] >= grid[r + 1][c]:
                return False
    return True


def find_set_O(shape_nu, shape_lambda):
    T_skew, cell_by_label = generate_reverse_filling(shape_nu, shape_lambda)
    total_size = len(T_skew)
    O_set = []
    
    for perm in permutations(range(1, total_size + 1)):
        T = YoungTableau()
        for x in perm:
            T.insert(x)
            
        if sum(len(r) for r in T.tableau) == total_size and is_standard_young_tableau(T):
            if any(T.tableau == existing.tableau for existing in O_set):
                continue
            if check_conditions_R1_R2(T, cell_by_label, total_size):
                O_set.append(T)

    return O_set, T_skew, cell_by_label


def find_set_O_mu(shape_nu, shape_lambda, shape_mu):
    O_set, _, _ = find_set_O(shape_nu, shape_lambda)
    O_mu_set = [T for T in O_set if T.get_shape() == list(shape_mu)]

    return O_mu_set


def find_set_S(shape_nu, shape_lambda, shape_mu):
    O_mu_set = find_set_O_mu(shape_nu, shape_lambda, shape_mu)
    _, cell_by_label = generate_reverse_filling(shape_nu, shape_lambda)
    
    S_set = []

    for T in O_mu_set:
        pos_in_T = {}
        for r, row in enumerate(T.tableau):
            for val in row:
                pos_in_T[val] = r + 1

        T_star = YoungTableau()
        for r in range(len(shape_nu)):
            row_len = shape_nu[r]
            row = [0] * row_len
            T_star.tableau.append(row)

        total_size = len(cell_by_label)
        for k in range(1, total_size + 1):
            x_k = pos_in_T[k]
            r_k, c_k = cell_by_label[k]
            T_star.tableau[r_k][c_k] = x_k

        S_set.append(T_star)

    return S_set


def is_valid_perforated(tableau_grid):
    rows = len(tableau_grid)
    for r in range(rows):
        cols = len(tableau_grid[r])
        for c in range(cols):
            val = tableau_grid[r][c]
            if val is None or val == 0:
                continue
            
            for r2 in range(r + 1):
                for c2 in range(c + 1):
                    other = tableau_grid[r2][c2]
                    if other is not None and other != 0 and other > val:
                        return False
            
            if r + 1 < rows and c < len(tableau_grid[r + 1]):
                below = tableau_grid[r + 1][c]
                if below is not None and below != 0 and below <= val:
                    return False
    return True


def can_switch(S_grid, T_grid, r1, c1, r2, c2):
    S_next = copy.deepcopy(S_grid)
    T_next = copy.deepcopy(T_grid)
    
    S_next[r1][c1], S_next[r2][c2] = S_next[r2][c2], S_next[r1][c1]
    T_next[r1][c1], T_next[r2][c2] = T_next[r2][c2], T_next[r1][c1]
    
    return is_valid_perforated(S_next) and is_valid_perforated(T_next)


def tableau_switching(S_grid, T_grid):
    S_curr = copy.deepcopy(S_grid)
    T_curr = copy.deepcopy(T_grid)
    
    rows = len(S_curr)
    
    while True:
        switched = False
        for r1 in range(rows):
            for c1 in range(len(S_curr[r1])):
                if S_curr[r1][c1] is None or S_curr[r1][c1] == 0:
                    continue
                
                neighbors = [(r1 + 1, c1), (r1, c1 + 1)]
                for r2, c2 in neighbors:
                    if r2 < rows and c2 < len(T_curr[r2]):
                        if T_curr[r2][c2] is not None and T_curr[r2][c2] != 0:
                            if can_switch(S_curr, T_curr, r1, c1, r2, c2):
                                S_curr[r1][c1], S_curr[r2][c2] = S_curr[r2][c2], S_curr[r1][c1]
                                T_curr[r1][c1], T_curr[r2][c2] = T_curr[r2][c2], T_curr[r1][c1]
                                switched = True
                                break
                if switched:
                    break
            if switched:
                break
                
        if not switched:
            break
            
    return S_curr, T_curr


def B_map(U0, A0, shape_nu):
    max_r = len(shape_nu)
    max_c = max(shape_nu) if max_r > 0 else 0
    
    A0_grid = [[0] * max_c for _ in range(max_r)]
    for r in range(len(A0.tableau)):
        for c in range(len(A0.tableau[r])):
            A0_grid[r][c] = A0.tableau[r][c]
            
    U0_grid = [[0] * max_c for _ in range(max_r)]
    for r in range(len(U0.tableau)):
        for c in range(len(U0.tableau[r])):
            val = U0.tableau[r][c]
            if val is not None and val != 0:
                U0_grid[r][c] = val

    _, A0_S_grid = tableau_switching(A0_grid, U0_grid)
    
    result_tableau = YoungTableau()
    for r in range(len(shape_nu)):
        row_len = shape_nu[r]
        row = [A0_S_grid[r][c] for c in range(row_len)]
        result_tableau.tableau.append(row)
        
    return result_tableau


# ==========================================
# TILDE LAMBDA PROCESSING & OUTPUT UTILS
# ==========================================

def get_transpose_shape(shape):
    """Compute transpose partition mu^T."""
    if not shape:
        return []
    max_cols = max(shape)
    transposed = []
    for c in range(max_cols):
        count = sum(1 for r in shape if r > c)
        if count > 0:
            transposed.append(count)
    return transposed


def construct_canonical_U0(shape):
    """Construct canonical U0 of given shape, row k contains value k."""
    U0 = YoungTableau()
    for r, length in enumerate(shape):
        U0.tableau.append([r + 1] * length)
    return U0


def compute_tilde_lambda(lam_strict, mu):
    r"""Compute tilde lambda (\widetilde{\lambda}) for yellow block mu^T x mu combined with strict lambda."""
    mu_t = get_transpose_shape(mu)
    tilde_shape = []
    max_len = max(len(lam_strict), len(mu), len(mu_t))
    
    for i in range(max_len):
        yellow_part = mu_t[i] if i < len(mu_t) else 0
        shift_offset = i
        strict_part = lam_strict[i] if i < len(lam_strict) else 0
        tilde_shape.append(yellow_part + shift_offset + strict_part)
        
    return [x for x in tilde_shape if x > 0]


def tableau_to_str(tab):
    """Format Young tableau to a single-line string representation."""
    grid = tab.tableau if hasattr(tab, 'tableau') else tab
    return " / ".join("[" + ",".join(str(x) if x != 0 else "." for x in row) + "]" for row in grid)


class ShiftedYoungTableau:
    def __init__(self, shape=None):
        self.tableau = []
        self.shape = shape if shape is not None else []

    @staticmethod
    def compare_labels(a, b):
        def parse(val):
            s = str(val)
            is_primed = s.endswith("'")
            num = int(s[:-1]) if is_primed else int(s)
            return num - 0.5 if is_primed else float(num)

        val_a, val_b = parse(a), parse(b)
        if val_a < val_b: return -1
        if val_a > val_b: return 1
        return 0

    def is_valid(self):
        grid = self.tableau
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                val = grid[r][c]
                if val is None or val == 0:
                    continue

                if c + 1 < len(grid[r]) and grid[r][c + 1] != 0:
                    right = grid[r][c + 1]
                    if self.compare_labels(val, right) > 0:
                        return False
                    if str(val).endswith("'") and val == right:
                        return False

                if r + 1 < len(grid) and c < len(grid[r + 1]) and grid[r + 1][c] != 0:
                    down = grid[r + 1][c]
                    if self.compare_labels(val, down) > 0:
                        return False
                    if not str(val).endswith("'") and val == down:
                        return False

                if c + 1 < len(grid[r]) and grid[r][c + 1] != 0:
                    if self.compare_labels(val, grid[r][c + 1]) > 0:
                        return False
                if r + 1 < len(grid) and c < len(grid[r + 1]) and grid[r + 1][c] != 0:
                    if self.compare_labels(val, grid[r + 1][c]) > 0:
                        return False

        return True

    def get_content(self):
        counts = {}
        for row in self.tableau:
            for val in row:
                if val is None or val == 0:
                    continue
                base_num = int(str(val).rstrip("'"))
                counts[base_num] = counts.get(base_num, 0) + 1

        if not counts:
            return ()
        max_idx = max(counts.keys())
        return tuple(counts.get(i, 0) for i in range(1, max_idx + 1))

    def display(self, title="Shifted Tableau:"):
        print(f"{title}")
        for r, row in enumerate(self.tableau):
            indent = " " * (r * 5)
            formatted_row = "".join(f"[{str(val):^3}]" if val != 0 else "[   ]" for val in row)
            print(indent + formatted_row)
        print("-" * 35)


def shifted_slide(tableau, r, c):
    rows = len(tableau)
    while True:
        val_right = float('inf')
        if c + 1 < len(tableau[r]) and tableau[r][c + 1] != 0:
            val_right = tableau[r][c + 1]

        val_down = float('inf')
        down_c = c - 1
        if r + 1 < rows and 0 <= down_c < len(tableau[r + 1]) and tableau[r + 1][down_c] != 0:
            val_down = tableau[r + 1][down_c]

        if val_right == float('inf') and val_down == float('inf'):
            tableau[r][c] = 0
            break

        if val_right <= val_down:
            tableau[r][c] = val_right
            tableau[r][c + 1] = 0
            c += 1
        else:
            tableau[r][c] = val_down
            tableau[r + 1][down_c] = 0
            r += 1
            c = down_c


def shifted_jeu_de_taquin(shifted_tableau):
    T_curr = copy.deepcopy(shifted_tableau.tableau)
    
    while True:
        inner_corner = None
        for r in range(len(T_curr) - 1, -1, -1):
            for c in range(len(T_curr[r]) - 1, -1, -1):
                if T_curr[r][c] == 0:
                    has_right = (c + 1 < len(T_curr[r])) and (T_curr[r][c + 1] != 0)
                    down_c = c - 1
                    has_down = (r + 1 < len(T_curr)) and (0 <= down_c < len(T_curr[r + 1])) and (T_curr[r + 1][down_c] != 0)
                    if has_right or has_down:
                        inner_corner = (r, c)
                        break
            if inner_corner:
                break
                
        if not inner_corner:
            break
            
        r, c = inner_corner
        shifted_slide(T_curr, r, c)

    cleaned_tableau = []
    for row in T_curr:
        trimmed = [val for val in row if val != 0]
        if trimmed:
            cleaned_tableau.append(trimmed)

    res = ShiftedYoungTableau()
    res.tableau = cleaned_tableau
    return res

def alphabet_order(val):
    s = str(val)
    if s.endswith("'"):
        num = int(s[:-1])
        return 2 * num - 1
    else:
        num = int(s)
        return 2 * num

def get_partitions(n, max_val=None):
    if max_val is None:
        max_val = n
    if n == 0:
        return [[]]
    partitions = []
    for i in range(min(n, max_val), 0, -1):
        for p in get_partitions(n - i, i):
            partitions.append([i] + p)
    return partitions

def get_shifted_reverse_filling(nu, mu):
    N = sum(nu) - sum(mu)
    T_tilde = {}
    curr = 1
    
    for r in range(len(nu)):
        row_len = nu[r] - (mu[r] if r < len(mu) else 0)
        c_start = (mu[r] if r < len(mu) else 0) + r
        for k in range(row_len - 1, -1, -1):
            c = c_start + k
            T_tilde[(r, c)] = curr
            curr += 1
            
    return T_tilde, N

def is_valid_tableau_order(T):
    # 1. Check weak row increase
    for row in T:
        for c in range(len(row) - 1):
            if alphabet_order(row[c]) > alphabet_order(row[c + 1]):
                return False

    # 2. Check strict column increase
    max_cols = max(len(row) for row in T)
    for c in range(max_cols):
        col_vals = [alphabet_order(T[r][c]) for r in range(len(T)) if c < len(T[r])]
        for i in range(len(col_vals) - 1):
            if col_vals[i] >= col_vals[i + 1]:
                return False

    return True

def is_valid_O_tilde(T, T_tilde, N):
    # Map string value -> (row, column) in T
    pos_map = {}
    for r in range(len(T)):
        for c in range(len(T[r])):
            val = str(T[r][c])
            pos_map[val] = (r, c)

    # 1. CHECK CONDITION (C1): k and k+1 are adjacent in the same row of T_tilde
    pos_in_tilde = {val: cell for cell, val in T_tilde.items()}
    
    for k in range(1, N):
        if k in pos_in_tilde and (k + 1) in pos_in_tilde:
            r_k, c_k = pos_in_tilde[k]
            r_k1, c_k1 = pos_in_tilde[k + 1]
            
            if r_k == r_k1:
                k_val = str(k)
                k_prime_val = f"{k}'"
                kp1_val = str(k + 1)
                kp1_prime_val = f"{k+1}'"

                kp1_pos = pos_map.get(kp1_val) or pos_map.get(kp1_prime_val)

                cond1_a = False
                if k_val in pos_map:
                    k_pos = pos_map[k_val]
                    cond1_a = (kp1_pos[0] <= k_pos[0])

                cond1_b = False
                if k_prime_val in pos_map:
                    k_prime_pos = pos_map[k_prime_val]
                    cond1_b = (kp1_pos[0] < k_prime_pos[0])

                if not (cond1_a or cond1_b):
                    return False

    # 2. CHECK CONDITION (C2): h is directly below k in the same column of T_tilde
    for (r, c), k in T_tilde.items():
        if (r + 1, c) in T_tilde:
            h = T_tilde[(r + 1, c)]
            h_val = str(h)
            h_prime_val = f"{h}'"
            k_val = str(k)
            k_prime_val = f"{k}'"

            h_pos = pos_map.get(h_val) or pos_map.get(h_prime_val)

            cond2_a = False
            if k_prime_val in pos_map:
                k_prime_pos = pos_map[k_prime_val]
                cond2_a = (h_pos[0] >= k_prime_pos[0])

            cond2_b = False
            if k_val in pos_map:
                k_pos = pos_map[k_val]
                cond2_b = (h_pos[0] > k_pos[0])

            if not (cond2_a or cond2_b):
                return False

    # 3. CHECK CONDITION (C3): Last element of each row must not contain a prime (')
    for r in range(len(T)):
        last_val = str(T[r][-1])
        if last_val.endswith("'"):
            return False

    # 4. CHECK CONDITION (C4)
    T_hat = []
    def hat_order(val):
        s = str(val)
        if s.endswith("'"):
            num = int(s[:-1])
            return N + (N - num + 1)
        else:
            return int(s)

    for row in T:
        sorted_row = sorted(row, key=hat_order)
        T_hat.append(sorted_row)

    max_cols = max(len(row) for row in T_hat)
    for c in range(max_cols):
        col_vals = []
        for r in range(len(T_hat)):
            if c < len(T_hat[r]):
                col_vals.append(hat_order(T_hat[r][c]))
        for i in range(len(col_vals) - 1):
            if col_vals[i] >= col_vals[i + 1]:
                return False

    def count_less_in_hat(row, ref_val):
        ref_rank = hat_order(ref_val)
        return sum(1 for item in row if hat_order(item) < ref_rank)

    for i in range(1, len(T_hat)):
        for j in range(1, N + 1):
            j_prime = f"{j}'"
            if j_prime in T_hat[i]:
                tau_prev = count_less_in_hat(T_hat[i - 1], j)
                tau_curr = count_less_in_hat(T_hat[i], j)
                if tau_prev <= tau_curr:
                    return False

            if j in T_hat[i - 1]:
                tau_prev = count_less_in_hat(T_hat[i - 1], j_prime)
                tau_curr = count_less_in_hat(T_hat[i], j_prime)
                if tau_prev <= tau_curr:
                    return False

    return True


def find_set_O_tilde(nu, mu):
    T_tilde, N = get_shifted_reverse_filling(nu, mu)
    if N <= 0:
        return {}

    all_partitions = get_partitions(N)
    all_results = {}

    label_choices = [[f"{i}'", i] for i in range(1, N + 1)]

    for lambda_shape in all_partitions:
        valid_tableaux = []
        for chosen_labels in itertools.product(*label_choices):
            for perm in itertools.permutations(chosen_labels):
                idx = 0
                grid = []
                for row_len in lambda_shape:
                    grid.append(list(perm[idx:idx + row_len]))
                    idx += row_len

                if not is_valid_tableau_order(grid):
                    continue

                if is_valid_O_tilde(grid, T_tilde, N):
                    yt = YoungTableau()
                    yt.tableau = grid
                    yt.shape = list(lambda_shape)
                    valid_tableaux.append(yt)

        if valid_tableaux:
            all_results[tuple(lambda_shape)] = valid_tableaux

    return all_results


# ==========================================
# DECISION TREE BUILDER FOR UNSHIFTED O SET
# ==========================================

def is_valid_young_shape(grid):
    """Check Ferrers diagram geometric shape: row lengths must be weakly decreasing."""
    for r in range(len(grid) - 1):
        if len(grid[r]) < len(grid[r + 1]):
            return False
    return True

def is_valid_young_tableau(grid):
    """Check Young tableau conditions:
    1. Valid Young shape (top row >= bottom row).
    2. Strict row increase.
    3. Strict column increase.
    """
    if not is_valid_young_shape(grid):
        return False

    for r in range(len(grid)):
        for c in range(len(grid[r])):
            val = grid[r][c]
            # Row: strict increase (val < right)
            if c + 1 < len(grid[r]) and grid[r][c + 1] != 0:
                if val >= grid[r][c + 1]:
                    return False
            # Column: strict increase (val < down)
            if r + 1 < len(grid) and c < len(grid[r + 1]) and grid[r + 1][c] != 0:
                if val >= grid[r + 1][c]:
                    return False
    return True

def get_possible_next_grids(grid, val_to_insert):
    """Insert val_to_insert only into valid corner cells of the Young diagram."""
    next_grids = []
    
    # Choice 1: Append to existing rows if preserving Young structure
    for r in range(len(grid)):
        new_grid = copy.deepcopy(grid)
        new_grid[r].append(val_to_insert)
        if is_valid_young_tableau(new_grid):
            next_grids.append(new_grid)
            
    # Choice 2: Start a new row at the bottom (valid if length <= previous row length)
    new_grid = copy.deepcopy(grid)
    new_grid.append([val_to_insert])
    if is_valid_young_tableau(new_grid):
        next_grids.append(new_grid)

    return next_grids

def check_R1_R2_partial(grid, cell_by_label, current_k):
    """Check conditions R1 and R2 for early tree pruning."""
    pos_map = {}
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            pos_map[grid[r][c]] = (r, c)

    # R1: k and k+1 in the same row of T_skew
    for k in range(1, current_k):
        if k in cell_by_label and (k + 1) in cell_by_label:
            r_k, c_k = cell_by_label[k]
            r_k1, c_k1 = cell_by_label[k + 1]
            if r_k == r_k1:
                if (k in pos_map) and ((k + 1) in pos_map):
                    row_k, col_k = pos_map[k]
                    row_k1, col_k1 = pos_map[k + 1]
                    if not (row_k1 <= row_k and col_k1 > col_k):
                        return False

    # R2: h is directly below k in the same column of T_skew
    for k in range(1, current_k + 1):
        if k in cell_by_label:
            r_k, c_k = cell_by_label[k]
            below_cell = (r_k + 1, c_k)
            h = next((label for label, cell in cell_by_label.items() if cell == below_cell), None)
            if h is not None and h <= current_k:
                if (k in pos_map) and (h in pos_map):
                    row_k, col_k = pos_map[k]
                    row_h, col_h = pos_map[h]
                    if not (row_h > row_k and col_h <= col_k):
                        return False
    return True

class TreeNode:
    def __init__(self, grid, val):
        self.grid = grid
        self.val = val
        self.children = []

def get_skew_cells(shape_nu, shape_lambda):
    cells = []
    for r in range(len(shape_nu)):
        lambda_len = shape_lambda[r] if r < len(shape_lambda) else 0
        for c in range(lambda_len, shape_nu[r]):
            cells.append((r, c))
    return cells

def build_O_tree(shape_nu, shape_lambda):
    cells = get_skew_cells(shape_nu, shape_lambda)
    sorted_cells = sorted(cells, key=lambda x: (x[0], -x[1]))
    cell_by_label = {i: cell for i, cell in enumerate(sorted_cells, start=1)}
    N = len(cell_by_label)

    root_grid = [[1]]
    root_node = TreeNode(root_grid, 1)

    _expand_tree(root_node, 2, N, cell_by_label)
    return root_node

def _expand_tree(node, k, N, cell_by_label):
    if k > N:
        return

    possible_grids = get_possible_next_grids(node.grid, k)
    for next_g in possible_grids:
        if check_R1_R2_partial(next_g, cell_by_label, k):
            child_node = TreeNode(next_g, k)
            node.children.append(child_node)
            _expand_tree(child_node, k + 1, N, cell_by_label)

def export_tree_to_graphviz(root_node, filename="O_tree_correct"):
    dot = graphviz.Digraph(comment='Corrected O Set Decision Tree', format='png')
    dot.attr('node', shape='plaintext')
    
    node_counter = [0]

    def grid_to_html(grid):
        html = '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
        for row in grid:
            html += '<TR>'
            for cell in row:
                html += f'<TD WIDTH="20" HEIGHT="20">{cell}</TD>'
            html += '</TR>'
        html += '</TABLE>'
        return f'<{html}>'

    def add_nodes(node, parent_id=None):
        node_counter[0] += 1
        curr_id = f"node_{node_counter[0]}"
        dot.node(curr_id, label=grid_to_html(node.grid))
        
        if parent_id:
            dot.edge(parent_id, curr_id)
            
        for child in node.children:
            add_nodes(child, curr_id)

    add_nodes(root_node)
    dot.render(filename, cleanup=True)
    print(f"Updated Young tree diagram exported to file: {filename}.png")

if __name__ == "__main__":
    shape_nu = [6, 5, 2, 2, 1]
    shape_lambda = [3, 2, 2, 1]

    root_tree = build_O_tree(shape_nu, shape_lambda)
    export_tree_to_graphviz(root_tree, "O_tree_correct")
