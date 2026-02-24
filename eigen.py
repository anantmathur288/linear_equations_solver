import numpy as np
from linear_equations_solver import LinearEquationSolver as LES
from sympy import symbols, Eq, Matrix, eye, prod, solve

class Eigen():
    def __init__(self, M):
        self.M = Matrix(M)
        self.l = symbols("l")
        self.C = Matrix.zeros(self.M.shape[0])
        self.eigenvalues = []
        self.eigenvectors = []

    def values(self):

        self.C = self.M - self.l * eye(self.M.shape[0])
        char_eqn = Eigen.det(self.C)

        self.eigenvalues = solve(char_eqn, self.l)

        return self.eigenvalues
    
    def vectors(self):
        for ev in self.eigenvalues:
            ev_matrix = self.C.subs(self.l, ev)

            basis = LES(np.array(ev_matrix.tolist(), dtype = float))._find_nullspace()

            self.eigenvectors.append(basis)

        return self.eigenvectors

    @staticmethod
    def det(A):
        pivot_list = []
        sign = 1
        temp = Matrix(A)

        for n in range(temp.shape[0]):

            col = n

            p = temp[n, col]

            c = n
            while p.equals(0):
                c += 1
                if c >= (temp.shape[0]):
                    break

                temp[n, :], temp[c, :] = temp[c, :].copy(), temp[n, :].copy()
                sign *= -1

                p = temp[n, col]

            pivot_list.append(p)

            for m in range(temp.shape[0]):
                if m <= n:
                    continue

                k = temp[m, col] / p
                temp[m, :] = temp[m, :] - k * temp[n, :]

        R = Matrix(temp)

        det = sign * prod(pivot_list)

        return det
    

if __name__ == '__main__':

    M = ([[2, 1],
          [1, 2]])
    
    eig = Eigen(M)

    print(eig.values())
    print(eig.vectors())