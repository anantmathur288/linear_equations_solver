import numpy as np

class ColumnSpaceError(Exception):
    pass

class LinearEquationSolver:
    def __init__(self, A, B = None, print_bool = False):
        self.A = np.array(A, dtype = float)
        if B is not None:
            self.B = np.array(B, dtype = float)
        else:
            self.B = B
        self.print_bool = print_bool

        self._check_colspace()

    def _check_colspace(self, eps=1e-10):
        m = len(self.A)

        if self.B is not None:
            if np.shape(self.B) != (m, 1):
                raise ColumnSpaceError(f"No valid solution - B does not exist in C(A)")

        R = self._rref()
        n_vars = R.shape[1] - 1

        for row in R:
            if all(abs(row[j]) < eps for j in range(n_vars)) and abs(row[-1]) > eps:
                raise ColumnSpaceError(f"No valid solution - B does not exist in C(A)")

        return None

    def _find_nullspace(self, eps=1e-10):
        R = self._rref()
        if self.B is not None:
            n_vars = R.shape[1] - 1
        else:
            n_vars = R.shape[1]

        pivot_cols = []
        for row in R:
            for j in range(n_vars):
                if abs(row[j] - 1) < eps:
                    pivot_cols.append(j)
                    break

        free_vars = [j for j in range(n_vars) if j not in pivot_cols]

        basis = []

        for free in free_vars:
            vec = np.zeros(n_vars)
            vec[free] = 1

            for i, row in enumerate(R):
                for j in pivot_cols:
                    if abs(row[j] - 1) < eps:
                        vec[j] = -row[free]

            basis.append(vec)

        return basis

    def _augment_matrix(self):
        if self.B is not None:
            aug_matrix = self.A.tolist()

            for i in range(len(self.A)):
                aug_matrix[i].append(self.B[i][0])

            aug_matrix = np.array(aug_matrix)

            return aug_matrix

        return self.A

    def _rref(self):
        temp = self._augment_matrix()

        for n in range(min(len(temp), len(temp[0]))):

            col = n
            while col < len(temp[0]) and abs(temp[n][col]) < 1e-10:
                col += 1

            if col >= len(temp[0]):
                if self.print_bool:
                    print("No pivot possible in this row")
                continue

            p = temp[n][col]

            if self.print_bool:
                print(f"Pivot is {p}")

            c = n
            while abs(p) < 1e-10:
                c += 1
                if c >= len(temp):
                    break

                temp[n], temp[c] = temp[c].copy(), temp[n].copy()
                if self.print_bool:
                    print("Swapping Rows")

                p = temp[n][col]
                if self.print_bool:
                    print(f"New pivot is {p}")

            if abs(p) < 1e-10:
                if self.print_bool:
                    print("No valid pivot in this column, continuing")
                continue

            temp[n] = temp[n] / p
            if self.print_bool:
                print(f"R after p = 1 is \n{temp}")

            for m in range(len(temp)):
                if m == n:
                    continue

                k = temp[m][col]
                temp[m] = temp[m] - k * temp[n]

                if self.print_bool:
                    print(f"R is \n{temp}")

        R = np.array(temp, dtype = float)

        if self.print_bool:
            print(f"R is:\n{R}")

        return R

    def _soln_extract(self, eps=1e-10):
        R = self._rref()

        rows, cols = R.shape
        n_vars = cols - 1

        pivot_cols = []
        pivot_row = {}

        for i in range(rows):
            if self.print_bool:
                print(f"Row no. {i + 1}: \n{R[i]}\n")

            for j in range(n_vars):
                if self.print_bool:
                    print(f"Column no. {j + 1}: \n{R[:, j]}\n")
                    print(f"Element is {R[i, j]}")

                    print(f"Checking: abs(R[i, j] - 1) < eps --> {abs(R[i, j] - 1) < eps}")
                    print(f"Checking: all(abs(R[i, k]) < eps for k in range(rows) if k != j --> "
                          f"{all(abs(R[k, j]) < eps for k in range(rows) if k != i)}\n")

                if abs(R[i, j] - 1) < eps and all(abs(R[k, j]) < eps for k in range(rows) if k != i):
                    if self.print_bool:
                        print(f"Column no. {j + 1} is a pivot column\n")
                    pivot_cols.append(j)
                    pivot_row[j] = i
                    break

                if self.print_bool:
                    print(f"Column no. {j + 1} is not a pivot column\n")

                    print(f"Pivot column numbers are {np.array(pivot_cols) + 1}\n")

        free_vars = [j for j in range(n_vars) if j not in pivot_cols]

        if self.print_bool:
            print(f"Free Variables are {np.array(free_vars) + 1}\n")

        x_p = np.zeros((n_vars, 1))
        for j in pivot_cols:
            x_p[j, 0] = R[pivot_row[j], -1]
            if self.print_bool:
                print(f"Extracting particular solution:\n {x_p}")

        if self.print_bool:
            print(f"Particular solution is: \n {x_p}")

        if len(free_vars) == 0:
            return x_p, 0

        nullspace = self._find_nullspace()

        return x_p, nullspace

    def solve(self):
        x = self._soln_extract()
        return x



if __name__ == '__main__':
    # A = [[1, 2, 3, 7, 12, 18],
    #      [4, 8, 6, 5, 7 ,10],
    #      [7, 8, 10, 6, 3, 1],
    #      [15, 5, 3, 2, 4, 7],
    #      [16, 7, 4, 6, 1, 1],
    #      [3, 56, 7, 8, 1, 3]]

    # B = [[1], [7], [6], [9], [2], [1]]
    A = np.array([[1, 2, 3, 4],
                  [2, 4, 7, 11],
                  [3, 7, 14, 25],
                  [4, 11, 25, 50]])

    # A = [[4, 3, 7],
    #      [12, 4, 5],
    #      [7, 8, 2]]
    #
    # B = [[1], [5], [6]]

    # o = LinearEquationSolver(A, B, True)
    # s = o.solve()

    r = LinearEquationSolver(A, print_bool = True)._rref()

    print(r)