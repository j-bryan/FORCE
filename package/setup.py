import sys
import platform
from cx_Freeze import setup, Executable, build_exe

import HERON.templates.write_inner

if platform.system() == 'Windows':
    packages = ["ravenframework","msgpack","ray","crow_modules","AMSC","sklearn","pyomo","HERON"]
else:  # Mac or Linux
    # TODO: Linux not tested
    packages = ["ravenframework","msgpack","ray","crow_modules","AMSC","sklearn","pyomo","HERON", "pyarrow", "netCDF4", "cftime"]

build_exe_options = {
    "packages": packages,
    "includes": ["ray.thirdparty_files.colorama","ray.autoscaler._private","pyomo.common.plugins","HERON.templates.template_driver"],
    "include_files": [(HERON.templates.write_inner.__file__,"lib/HERON/templates/write_inner.py")],
    "include_msvcr": True,
}


setup(
    name="force",
    version="0.1",
    description="FORCE package",
    executables=[Executable("raven_framework.py"),Executable("heron.py")],
    options={"build_exe": build_exe_options},
)
