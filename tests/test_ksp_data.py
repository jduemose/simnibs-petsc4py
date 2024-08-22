import time

# import mkl
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

A = PETSc.Mat(comm=PETSc.COMM_WORLD)
A.createAIJ(size=S.shape, csr=(S.indptr, S.indices, S.data))
A.assemble()

# PREONLY: use a single application of the preconditioner only
ksp_type = PETSc.KSP.Type.PREONLY # "cg"
# if SPD: cholesky
# otherwise: LU
pc_type = PETSc.PC.Type.CHOLESKY
factor_solver_type = PETSc.Mat.SolverType.MKL_PARDISO
# pc_type=PETSc.PC.Type.HYPRE
# factor_solver_type=None

if pc_type == PETSc.PC.Type.HYPRE:
    options = PETSc.Options()
    #-pc_hypre_boomeramg_coarsen_type HMIS
    options["pc_hypre_boomeramg_coarsen_type"] = "HMIS"

# Build KSP solver object
ksp = PETSc.KSP()
ksp.create(comm=A.getComm())
ksp.setOperators(A)
ksp.setTolerances(rtol=1e-10)
ksp.setType(ksp_type)
ksp.setConvergenceHistory()
ksp.getPC().setType(pc_type)
if ksp.getPC().getType() == "hypre":
    # #-pc_hypre_type boomeramg
    ksp.getPC().setHYPREType("boomeramg")
    ksp.getPC().setFromOptions()

if factor_solver_type is not None:
    ksp.getPC().setFactorSolverType(factor_solver_type)

aa = time.perf_counter()

print("Preparing KSP")
# PC preparation
a = time.perf_counter()
ksp.setUp()
print(f"Time to prepare KSP: {time.perf_counter() - a:.4f}")

b = A.createVecLeft()
x = A.createVecRight()

for i in range(len(sol)):

    b.array[:] = rhs[i]

    # solve
    start = time.perf_counter()
    ksp.solve(b, x)
    stop = time.perf_counter()

    # print(ksp.getResidualNorm())

    print(f"{stop-start:.4f} s")

    # print(x[:])
    # print(x[:] - sol[i])
    # print((x[:] - sol[i])/sol[i])
print(f"total {time.perf_counter()-aa:.4f}")
