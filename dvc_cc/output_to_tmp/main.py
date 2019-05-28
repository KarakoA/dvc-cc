#!/usr/bin/env python3

import os
from argparse import ArgumentParser
import re
import random
import dvc
from dvc.repo import Repo as DVCRepo
from git import Git
import subprocess
import time

DESCRIPTION = 'This script gives you the possibility to get all output files that match some regex over different branches and saves them in a tmp folder.'


def create_output_dir(root_dir, path_to_output = None):
    """ This function creates the output dir to save the data.
    Args:
        root_dir (str): The root dir of the project. This could be repo.root_dir and this is the part where the .gitignore will be wroten to.
        path_to_output (str): default=None

    Returns:
        str: The foldername that was created. If no folder could be created, it will return None
    """
    if path_to_output is None:
        path_to_output = 'tmp_' + str(random.getrandbits(32))
    if os.path.exists(path_to_output):
        print('Error the path '+ path_to_output +' already exists. First remove this folder.')
        return None

    # Create folder and write them to .gitignore
    os.mkdir(path_to_output)
    f= open(os.path.join(root_dir, '.gitignore'),"a+")
    f.write('\n'+path_to_output)
    f.close()
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git', 'commit','-m','update .gitignore'])
    subprocess.call(['git', 'push'])
    print('Create folder ' + path_to_output + ' and wrote this to .gitignore')
    return path_to_output



def check_out_if_its_valid(out, regex_name_of_file=None, ex_regex_name_of_file=None, allow_dir=False):
    """ This function checks if a given file is a file of interest or not.

    Args:
        out (dvc.out): The output file that needs to be checked
        regex_name_of_file (str): The regex that should match the out if its a file of interest.
        ex_regex_name_of_file (str): The regex that should NOT match the out if its a file of interest.
        allow_dir (bool): If false, output dir are never of interest and will always return false.

    Returns:
        str: The status of the file. It can be 'valid', 'not_of_interest', 'not_created' or 'not_in_local_cache'
    """
    possible_status_messages = ['valid', 'not_of_interest', 'not_created', 'not_in_local_cache']

    if out.isdir() and not allow_dir:
        return possible_status_messages[1]

    # check if file does not match regex. If is_a_valid_file is still True, than this is a file of interest.
    if regex_name_of_file is not None:
        if not re.match(args.regex_name_of_file, out.rel_path):
            return possible_status_messages[1]

    if ex_regex_name_of_file is not None:
        if re.match(ex_regex_name_of_file, out.rel_path):
            return possible_status_messages[1]

    if out.use_cache == False:
        return possible_status_messages[1]

    if out.checksum is None:
        return possible_status_messages[2]
    
    if not out.exists:
        return possible_status_messages[3]

    return possible_status_messages[0]


def main():

    parser = ArgumentParser(description='Process some integers.')
    parser.add_argument('-f','--regex-name-of-file', type=str, default = None,
                        help='A regex of the name of the files that you want to find.')
    parser.add_argument('-ef','--exclude-regex-name-of-file', type=str, default = None,
                        help='A regex of the name of the file that are excluded.')
    parser.add_argument('-b','--regex-name-of-branch', type=str, default = None,
                        help='A regex of the name of the branches to be included in the search.')
    parser.add_argument('-eb','--exclude-regex-name-of-branch', type=str, default = None,
                        help='A regex of the name of the branch that are excluded.')
    parser.add_argument('-o','--path-to-output', type=str, default = None,
                        help='The path where you want save the files.')
    parser.add_argument('-r', '--rename-file', dest='rename_file', action='store_true', default=False,
                        help='If true, the branch name is added to the file name of the destination.')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False,
                        help='Print all files that are copied.')
    parser.add_argument('-d', '--download-stages', dest='download_stages', action='store_true', default=False,
                        help='Download a stage if the file is not in the local cache.')
    parser.add_argument('--allow-dir', dest='allow_dir', action='store_true', default=False,
                        help='If dir outputs should be included or not. This works only for flat folders. It will not work for sub directories!')
    parser.add_argument('-ns','--no-save', dest='no_save', action='store_true', default=False,
                        help='If true, it will not create a folder or link the file. This parameter is helpfull if it is used with --debug to test your regular expressions.')
    parser.add_argument('-nw','--no-print-of-warnings', dest='no_warning', action='store_true', default=False,
                        help='If true, it will not print warning if a file is not created or not in the local cache.')
    args = parser.parse_args()

    repo = DVCRepo()
    g = Git()
    starting_branch = g.branch().split('*')[1].split('\n')[0][1:]


    if not args.no_save:
        path_to_output = create_output_dir(repo.root_dir, args.path_to_output)
        if path_to_output is None:
            exit(1)
    else:
        path_to_output = 'NONE'

    try:
        file_counter = 0
        saved_files = {}
        for branch in repo.brancher(all_branches=True):
            if branch != 'Working Tree':
                print(branch)
                g.checkout(branch)
                repo.checkout()
                outs = []
                branch_names = []

                # search for all output files in the current branch
                is_branch_of_interest1 = args.regex_name_of_branch is None or re.match(args.regex_name_of_branch, branch)
                is_branch_of_interest2 = args.exclude_regex_name_of_branch is None or not re.match(args.exclude_regex_name_of_branch, branch)
                if is_branch_of_interest1 and is_branch_of_interest2:
                    for stage in repo.stages():
                        for out in stage.outs:
                            valid_msg = check_out_if_its_valid(out, args.regex_name_of_file, args.exclude_regex_name_of_file, args.allow_dir)
                            print('\t\t\t',out, valid_msg)
                            if valid_msg == 'not_in_local_cache' and args.download_stages:
                                g.pull()
                                repo.pull(stage.relpath)
                                time.sleep(1)
                                valid_msg = check_out_if_its_valid(out, args.regex_name_of_file, args.exclude_regex_name_of_file, args.allow_dir)
                                print(valid_msg)
                            if valid_msg == 'valid':
                                outs.append(out)
                                branch_names.append(branch)                  
                            elif valid_msg == 'not_created' and args.no_warning == False:
                                print('Warning: A output file of interest has not yet been created. ' +
                                        '(file: ' + str(out) + '; branch: ' + branch + ')')
                            elif valid_msg == 'not_in_local_cache' and args.no_warning == False:
                                print('Warning: A output file of interest is not on the local cache. ' +
                                        '(file: ' + out.cache_path + '; branch: ' + branch +
                                        ')\n You can use this script with -d and it will download the missing stage.')

                # create a link for each output file of interest in the current branch
                for out, branch_name in zip(outs, branch_names):
                    # create the output file name
                    if args.rename_file:
                        out_filename = branch_name + '_' + str(out).replace('/','_')
                    else:
                        out_filename = str(out).replace('/','_')
                    out_filepath = os.path.join(repo.root_dir, path_to_output, out_filename) 
                    
                    file_was_already_saved = False
                    renamer_index = 2
                    file_can_be_saved = False
                    tmp_out_filepath = out_filepath

                    while not file_can_be_saved and not file_was_already_saved:
                        if tmp_out_filepath not in saved_files:
                            file_can_be_saved = True
                            out_filepath = tmp_out_filepath
                            saved_files[out_filepath] = out.checksum
                        elif saved_files[tmp_out_filepath] == out.checksum:
                            file_was_already_saved = True
                        else:
                            tmp_out_filepath = out_filepath + '_' + str(renamer_index)
                            renamer_index += 1
                    if file_can_be_saved:
                        if args.debug:
                            print(out.cache_path, ' -> ', out_filepath)
                        if args.no_save is False:
                            if out.isfile():
                                os.link(out.cache_path, out_filepath)
                            elif out.isdir():
                                os.mkdir(out_filepath)
                                for cache in out.dir_cache:
                                    dirfile_cache_path = repo.cache.local.get(cache['md5'])
                                    dirfile_outpath = os.path.join(out_filepath,cache['relpath'])
                                    os.link(dirfile_cache_path, dirfile_outpath)

                        file_counter += 1
        
        print(str(file_counter) + ' files are linked to ' + path_to_output + '.')

    # return always to the starting branch!
    finally:
        g.checkout(starting_branch)
        repo.checkout()



