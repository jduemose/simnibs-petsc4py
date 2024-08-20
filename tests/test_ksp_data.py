import time

import mkl
import numpy as np
import scipy as sp

from petsc4py import PETSc

# mkl.set_num_threads(4)
# status = mkl.domain_set_num_threads(4, domain='pardiso')
# status = mkl.domain_set_num_threads(1, domain='blas')

S = sp.sparse.load_npz("data/system_matrix.npz")
rhs = np.load("data/system_rhs.npz")["arr_0"]
sol = np.load("data/system_solution_10.npz")["arr_0"]

# S.data = S.data.astype(np.float64)
# S = sp.sparse.triu(S).tocsr()
# S.data = S.data.astype(np.float64)

A = PETSc.Mat()
A.createAIJ(size=S.shape, csr=(S.indptr, S.indices, S.data))
A.assemble()

#rtol=1e-10
ksp_type="cg"
pc_type="lu"
factor_solver_type= "mkl_pardiso"
# pc_type="hypre"
# factor_solver_type=None

#-pc_hypre_type boomeramg
#-pc_hypre_boomeramg_coarsen_type HMIS


# Build KSP solver object
ksp = PETSc.KSP().create()
ksp.setOperators(A)
# ksp.setTolerances(rtol=rtol)
ksp.setType(ksp_type)
ksp.setConvergenceHistory()
ksp.getPC().setType(pc_type)
if factor_solver_type is not None:
    ksp.getPC().setFactorSolverType(factor_solver_type)

aa = time.perf_counter()

b = A.createVecLeft()
x = A.createVecRight()

for i in range(len(sol)):

    b.array[:] = rhs[i]

    # solve
    start = time.perf_counter()
    ksp(b, x)
    stop = time.perf_counter()

    print(f"{stop-start:.4f} s")

    # print(x[:])
    # print(x[:] - sol[i])
    # print((x[:] - sol[i])/sol[i])
print(f"total {time.perf_counter()-aa:.4f}")
