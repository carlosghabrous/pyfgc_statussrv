import setuptools

with open("README.md", "r") as fh:
	description = fh.read()


setuptools.setup(
 name             = "pyfgc_statussrv",
 version          = "1.0.0",
 author           = "Carlos Ghabrous Larrea",
 author_email     = "carlos.ghabrous@cern.ch",
 description      = description,
 url              = "https://gitlab.cern.ch/ccs/fgc/tree/master/sw/clients/python/pyfgc_statussrv",
 python_requires  = ">=3.6",
 install_requires = ["pyfgc", "pyfgc_decoders", "pyfgc_const"],
 py_modules       = ["pyfgc_statussrv"]
)
