from cx_Freeze import setup, Executable

base = None    


includefiles = ['geckodriver.exe', 'pizza.json']
executables = [Executable("dominos_orderer.py", base=base)]
packages = ["idna", "requests", "queue", "selenium", "json", "os"]
options = {
    'build_exe': {   
		'include_files':includefiles,
        'packages':packages,
    },    
}

setup(
    name = "Spencer",
    options = options,
    version = "1.0",
    description = 'Test exe',
    executables = executables
)