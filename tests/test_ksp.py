import sys

import numpy as np
import pytest
import scipy.sparse

from petsc4py import PETSc

"""Based on example from https://tbetcke.github.io/hpc_lecture_notes/petsc_for_sparse_systems.html"""

def build_A(n=1000):
    """Create empty matrix and fill manually."""
    nnz = 3 * np.ones(n, dtype=np.int32)
    nnz[0] = nnz[-1] = 2

    A = PETSc.Mat()
    A.createAIJ([n, n], nnz=nnz)

    # First set the first row
    A.setValue(0, 0, 2)
    A.setValue(0, 1, -1)
    # Now we fill the last row
    A.setValue(n-1, n-2, -1)
    A.setValue(n-1, n-1, 2)

    # And now everything else
    for index in range(1, n - 1):
        A.setValue(index, index - 1, -1)
        A.setValue(index, index, 2)
        A.setValue(index, index + 1, -1)

    A.assemble()


    return A

def build_A_from_csr_matrix(n):
    """Create empty matrix and fill from scipy sparse csr matrix."""

    ss_mat = scipy.sparse.csr_matrix()

    A = PETSc.Mat()
    A.createAIJ(size=ss_mat.shape, csr=(ss_mat.indptr, ss_mat.indices, ss_mat.data))
    A.assemble()

    return A
class TestMat:

    @pytest.mark.parametrize("n", [100, 1000])
    def test_mat_build_methods(self, n):
        A0 = build_A(n)
        A1 = build_A_from_csr_matrix(n)
        # np.testing.assert_allclose()


    @pytest.mark.parametrize("n", [100, 1000])
    def test_mat(self, n):
        A = build_A(n)
        assert A.size == (n, n)

        diagonals = A.getDiagonal().array
        assert np.all(diagonals == 2)

class TestKSP:
    @pytest.mark.parametrize("ksp_type", ["cg"])
    @pytest.mark.parametrize(
        ["pc_type","factor_solver_type"],
        [
            ("none", None),
            ("hypre", None),
            pytest.param(
                "lu",
                "mkl_pardiso",
                marks=pytest.mark.skipif(
                    sys.platform == "darwin",
                    reason="PETSc is not build with Intel MKL on macosx."
                ),
            ),
            pytest.param(
                "lu",
                "superlu",
                marks=pytest.mark.skipif(
                    sys.platform != "darwin",
                    reason="PETSc only build with superlu on macosx."
                ),
            ),
        ]
    )
    def test_KSP(self, ksp_type, pc_type, factor_solver_type, rtol=1e-10):

        A = build_A()

        b = A.createVecLeft()
        b.array[:] = 1

        x = A.createVecRight()

        # Build KSP solver object
        ksp = PETSc.KSP().create()
        ksp.setOperators(A)
        ksp = PETSc.KSP().create()
        ksp.setOperators(A)
        ksp.setTolerances(rtol=rtol)
        ksp.setType(ksp_type)
        ksp.setConvergenceHistory()
        ksp.getPC().setType(pc_type)
        if factor_solver_type is not None:
            ksp.getPC().setFactorSolverType(factor_solver_type)

        # solve
        ksp(b, x)

        b_hat = A.createVecLeft()
        A.mult(x, b_hat)

        # print(ksp.getConvergenceHistory()[-1])

        # ksp.KSP_CONVERGED_RTOL # 2
        # assert ksp.getConvergedReason() == ksp.KSP_CONVERGED_RTOL

        #assert np.isclose(0, ksp.getConvergenceHistory()[-1])
        np.testing.assert_allclose(b[:], b_hat[:])



# def blbla:

#     ksp = PETSc.KSP().create()
#     ksp.setOperators(A)
#     b = A.createVecLeft()
#     b.array[:] = 1

#     x = A.createVecRight()

#     # no PC
#     ksp = PETSc.KSP().create()
#     ksp.setOperators(A)
#     ksp.setTolerances(rtol=1e-10)
#     ksp.setType('cg')
#     ksp.setConvergenceHistory()
#     ksp.getPC().setType('none')
#     ksp(b, x)

#     b_hat = A.createVecLeft()
#     A.mult(x, b_hat)

#     # print(ksp.getConvergenceHistory()[-1])

#     #assert np.isclose(0, ksp.getConvergenceHistory()[-1])
#     np.testing.assert_allclose(b[:], b_hat[:])

#     # HYPRE
#     ksp = PETSc.KSP().create()
#     ksp.setOperators(A)
#     ksp.setTolerances(rtol=1e-10)
#     ksp.setType('cg')
#     ksp.setConvergenceHistory()
#     ksp.getPC().setType('hypre')
#     ksp(b, x)

#     b_hat = A.createVecLeft()
#     A.mult(x, b_hat)

#     # print(ksp.getConvergenceHistory()[-1])
#     #assert np.isclose(0, ksp.getConvergenceHistory()[-1])
#     np.testing.assert_allclose(b[:], b_hat[:])

#     # MKL PARDISO
#     ksp = PETSc.KSP().create()
#     ksp.setOperators(A)
#     ksp.setTolerances(rtol=1e-10)
#     ksp.setType('cg')
#     ksp.setConvergenceHistory()
#     ksp.getPC().setType('lu')
#     ksp.getPC().setFactorSolverType("mkl_pardiso")
#     ksp(b, x)

#     b_hat = A.createVecLeft()
#     A.mult(x, b_hat)

#     # print(ksp.getConvergenceHistory()[-1])
#     #assert np.isclose(0, ksp.getConvergenceHistory()[-1])
#     np.testing.assert_allclose(b[:], b_hat[:])
