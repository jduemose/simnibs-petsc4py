# start patch
# this is similar in spirit to what delvewheel does
depth = 4
dll_dir = r"Library\bin"

import os
libs_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        os.pardir,
        os.pardir,
        dll_dir,
    )
)
if os.path.isdir(libs_dir):
    os.add_dll_directory(libs_dir)
# end patch