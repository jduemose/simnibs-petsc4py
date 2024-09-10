# PETSc4py with Precompiled PETSc Libraries

Overview of what dependecies PETSc is built with on different platforms.

| OS    | Arch  | BLAS/LAPACK       | MKL PARDISO | HYPRE | MUMPS |
|:------|:----- |:----------------- |:-----------:|:-----:|:-----:|
|Linux  | x64   | MKL               | x           | x     |       |
|Macos  | arm64 | Apple Accelerate  |             | x     | x     |
|Windows| x64   | MKL               | x           | x     |       |


## TODOs

- General clean-up of workflows. Some things are hardcoded.
- Compile HYPRE against MKL BLAS (linux, windows)?

### Windows
- Read compiler arguments from petscvariables (at the moment, they are hardcoded!).
- Use * to glob for wheel file. (at the moment, it is hardcoded!). Perhaps via. powershell as cmd does not seem to support wildcard expansion in the shell.
- Convert from command prompt to powershell?

### MacOS
- Test threading
- Solve phase of MUMPS is slower than python-mumps. Why?
- MUMPS seems to be statically compiled even with shared-library=1?
- Currently, I set `MACOSX_DEPLOYMENT_TARGET` to 14.0 manually since `cibuildwheel` defaults to 11. I don't know if using 11 would case problems. The current M1 mac runners on GitHub Actions uses MacOS 14.
