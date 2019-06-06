from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime
from dvc_cc.dummy.class_variable import Variable
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path


DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('name_of_variable', help='The name of variable to show. Use "all" to show all variables. If you use "all" --set and --set-type has no effect.', type=str)
    parser.add_argument('--set', help='Set a constant value for one parameter. If a constant value is set, it will not be queried when running "dvc-cc run". Use "None" to undo the constant value.', type=str, default=None)
    parser.add_argument('--set-type', help='If you want to reset the type of the variable you can use this parameter. This should be one of the following: float, ufloat, int, uint or file.', type=str, default=None)
    args = parser.parse_args()                                                 

    # go to the main git directory.
    os.chdir(get_main_git_directory_path())

    if not os.path.exists('dvc'):
        os.mkdir('dvc')
    
    if not os.path.exists('dvc/.dummy'):
        os.mkdir('dvc/.dummy')

    # find and read all dummy files and search for all variables
    variables = Variable.get_all_already_defined_variables()
    
    if args.name_of_variable.lower() == 'all':
        print('%25s%8s%6s'%('Varname','type','value'))
        for v in variables:
            print(variables[v].__pretty_str__())
    elif args.name_of_variable in variables:
        if args.set_type is not None:
            variables[args.name_of_variable].vartype = args.set_type
            variables[args.name_of_variable].set_type_of_variable()
            variables[args.name_of_variable].set_constant_value(None)
        if args.set is not None:
            variables[args.name_of_variable].set_constant_value(args.set)
        if args.set_type is not None or args.set is not None:
            Variable.update_all_dummyfiles(variables)
            
        print('%25s%8s%6s'%('Varname','type',
'value'))
        print(variables[args.name_of_variable].__pretty_str__())
    else:
        raise ValueError("This variable does not exist. Use 'dvc-cc dummy variable all' to get a list of all variable names.")

















