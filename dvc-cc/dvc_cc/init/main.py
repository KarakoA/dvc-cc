from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes
import yaml
import subprocess
import os


SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-r','--ram', help='The ram that you need.',type=int,default=131072)
    parser.add_argument('-T','--test', help='Run at cctest.',default=False, action='store_true')
    parser.add_argument('-g','--num-of-gpus', help='The number of gpus that you need to ',type=int,default=1)
    #TODO: implement sample projects?
    #parser.add_argument('-ms', '--mini-sample', help='Creates a mini sample project.', default=False,action='store_true')
    #parser.add_argument('-ls', '--large-sample', help='Creates a large sample project.', default=False,action='store_true')
    args = parser.parse_args()
    
    # Change the directory to the main git directory.
    os.chdir(get_main_git_directory_path())
    
    gitrepo = GITRepo('.')
    try:
        dvcrepo = DVCRepo('.')

        #TODO: this can be removed!?
        if not os.path.exists('.dvc'):
            dvcrepo.init()
    except:
        subprocess.call(['dvc', 'init'])
        dvcrepo = DVCRepo('.')
    
    # create the main folder of the dvc_cc software package.
    if not os.path.exists('.dvc_cc'):
        os.mkdir('.dvc_cc')
    
    # create the config file.    
    if not os.path.exists('.dvc_cc/cc_config.yml'):
        create_cc_config_file(args)
        subprocess.call(['git', 'add', '.dvc_cc/cc_config.yml'])
    #TODO: CREATE THE SAMPLE PROJECTS !!!


def create_cc_config_file(args):
    #TODO: Allow interactive sessions.
    #TODO: Allow more parameters to set in the config.
    with open('.dvc_cc/cc_config.yml',"w") as f:
        print("cli:", file=f)
        print("  baseCommand: [dvc-cc-agent]", file=f)
        print("  class: CommandLineTool", file=f)
        print("  cwlVersion: v1.0", file=f)
        print("  doc: some descriptions of the package...", file=f)
        print("  inputs:", file=f)
        print("    git_authentication_json:", file=f)
        print("      doc: 'A path to json file which contains the git authentication. This should include the keys: username. email and password.'", file=f)
        print("      inputBinding: {position: 0}", file=f)
        print("      type: File", file=f)
        print("    git_path_to_working_repository:", file=f)
        print("      doc: 'The git working directory. With this you can specify what the main git root is.'", file=f)
        print("      inputBinding: {position: 1}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_owner:", file=f)
        print("      doc: 'The name of the owner of the git repository which you want to execute.'", file=f)
        print("      inputBinding: {position: 2}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_name:", file=f)
        print("      doc: 'The git repository name.'", file=f)
        print("      inputBinding: {position: 3}", file=f)
        print("      type: string", file=f)
        print("    git_name_of_tag:", file=f)
        print("      doc: 'The source code jumps to this here defined git tag (with git checkout) and execute dvc repro there.'", file=f)
        print("      inputBinding: {position: 4}", file=f)
        print("      type: string", file=f)
        print("    dvc_authentication_json:", file=f)
        print("      doc: 'A path to json file which contains the dvc authentication. This should include the keys: username and password.'", file=f)
        print("      inputBinding: {position: 5}", file=f)
        print("      type: File", file=f)
        print("    dvc_servername:", file=f)
        print("      doc: 'The servername of the dvc directory.'", file=f)
        print("      inputBinding: {position: 6}", file=f)
        print("      type: string", file=f)
        print("    dvc_path_to_working_repository:", file=f)
        print("      doc: 'The directory that is used for the dvc script.'", file=f)
        print("      inputBinding: {position: 7}", file=f)
        print("      type: string", file=f)
        print("    dvc_data_dir:", file=f)
        print("      doc: 'This is optional parameter. Here you can specify a sshfs folder for the \"data\" folder.'", file=f)
        print("      inputBinding: {prefix: --data_dir}", file=f)
        print("      type: Directory?", file=f)
        print("    dvc_file_to_execute:", file=f)
        print("      doc: 'This is optional parameter. If this parameter is given it will run \"dvc repro DVC_FILE_TO_EXECUTE\". Is this parameter is not set it will run \"dvc repro -P\"'", file=f)
        print("      inputBinding: {prefix: --dvc_file_to_execute}", file=f)
        print("      type: string?", file=f)
    
        print("  outputs: {}", file=f)
        print("container:", file=f)
        print("  engine: nvidia-docker", file=f)
        print("  settings:", file=f)
        print("    gpus: {count: "+str(args.num_of_gpus)+"}", file=f)
        # TODO: ASK FOR THIS!
        print("    image: {url: 'docker.io/deepprojects/dvc_repro_starter_tf2.alpha:dev'}", file=f)
        print("    ram: "+str(args.ram), file=f)
        print("execution:", file=f)
        print("  engine: ccagency", file=f)
        print("  settings:", file=f)
        print("    access:", file=f)
        print("      auth: {password: '{{agency_password}}', username: '{{agency_username}}'}", file=f)    
        if args.test:
            print("      url: https://agency.f4.htw-berlin.de/cctest", file=f)
        else:
            print("      url: https://agency.f4.htw-berlin.de/cc", file=f)
        print("    batchConcurrencyLimit: 12", file=f)
        print("    retryIfFailed: false", file=f)
        print("redVersion: '7'", file=f)
        
        
