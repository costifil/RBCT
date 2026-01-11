'''
Installing a virtual environment module
Make sure the virtaulenv is installed. If not use the command:
    pip install virtualenv
'''
import os
import platform
import subprocess
import argparse
#import virtualenv
import shutil
import time

IS_WINDOWS = platform.system().lower() == "windows"
PYTHON_BIN = "py" if IS_WINDOWS else "python3"

INSTALLER_DIR = "installer"
THISDIR = os.path.dirname(os.path.realpath(__file__))
THIS_WS = os.path.abspath(os.path.join(THISDIR, ".."))
THIS_PACKAGES = "packages.txt"


def create_venv(venv_dir):
    virtualenv.cli_run([venv_dir])

def get_bin_folder(venv_dir):
    scripts_dir = "bin" # for linux
    if IS_WINDOWS:
        scripts_dir = "Scripts"

    return os.path.join(venv_dir, scripts_dir)

def get_activate_this_path(venv_dir):
    scripts_dir = get_bin_folder(venv_dir)
    return os.path.join(scripts_dir, "activate_this.py")

def pip_install(arg, pip_config=None, get_output=False, cwd=None):
    cmd = PYTHON_BIN + " -m pip install " + arg
    env = os.environ.copy()
    if env and pip_config:
        env['PIP_CONFIG_FILE'] = pip_config

    try:
        if get_output:
            return subprocess.check_output(cmd,
                                           shell=True,
                                           env=env,
                                           stderr=subprocess.STDOUT,
                                           cwd=cwd)
        else:
            return subprocess.check_call(cmd, shell=True, env=env, cwd=cwd)
    except subprocess.CalledProcessError as ex:
        print("Error:", ex)
        args = f"{arg} --no-cache-dir"
        if get_output:
            return subprocess.check_output(cmd,
                                           shell=True,
                                           env=env,
                                           stderr=subprocess.STDOUT,
                                           cwd=cwd)
        else:
            return subprocess.check_call(cmd, shell=True, env=env, cwd=cwd)

def install_external_packages(venv_dir, packages):
    pack_file = os.path.dirname((os.path.abspath(os.path.expanduser(__file__))))

    print(">>> Install external packages in:", venv_dir)
    pip_install('-r ' + os.path.join(pack_file, packages))

def setup_venv(venv_dir):
    venv_dir = os.path.abspath(os.path.expanduser(venv_dir))
    if venv_dir and os.path.exists(venv_dir):
        # remove the venv_dir
        answer = input(f"Do you  want to remove the folder {venv_dir}? [y/n]:")
        if answer.lower() == "y":
            shutil.rmtree(venv_dir)
            print(f"{venv_dir} folder removed.")
            time.sleep(2)
        
    if venv_dir and not os.path.exists(venv_dir):
        print(">>> Creating virtualenv in:", venv_dir)
        create_venv(venv_dir)

        print(">>> Activating virtualenv in:", venv_dir)
        activate_file = get_activate_this_path(venv_dir)
        with open(activate_file, 'rb') as fp:
            exec(fp.read(), {'__file__': activate_file})

        print(">>> Ensuring virtualenv is installed in new virtual environment")
        pip_install("virtualenv")

def get_workspace_package_dir(wrksp_dir):
    current_dir = os.path.abspath(wrksp_dir)
    dirs = []
    for name in os.listdir(current_dir):
        sub_dir = os.path.join(current_dir, name)
        if os.path.isdir(sub_dir):
            if 'setup.py' in os.listdir(sub_dir):
                dirs.append(sub_dir)

    return dirs

def install_local_packages(install_dir, srcdir):
    print("Installing", srcdir)
    output = pip_install('-e .', pip_config=install_dir, cwd=srcdir, get_output=True)
    print("Install output: ", output.decode("UTF-8"))
    print("Done installing", srcdir)

def install_workspace(workspace):
    install_dir = os.path.join(workspace, INSTALLER_DIR)
    src_dirs = get_workspace_package_dir(os.path.join(workspace, "src"))
    ch_utils_idx = -1
    for idx, value in enumerate(src_dirs):
        if "ch_utils" in value:
            ch_utils_idx = idx

    if ch_utils_idx == -1:
        raise Exception('Could not find ch_utils in the project')

    # bring to front
    src_dirs.insert(0, src_dirs.pop(ch_utils_idx))

    for item in src_dirs:
        install_local_packages(install_dir, item)


try:
    import virtualenv
except ModuleNotFoundError:
    pip_install('virtualenv')
    import virtualenv


def main():
    argp = argparse.ArgumentParser(description='Creates/uses a virtualenv and installs dev/rel packages')
    argp.add_argument('--venv', help='Path to virtualenv to install against, will create if nonexistent', default=os.environ.get('VIRTUAL_ENV'))
    argp.add_argument('--package', help='Path to file containing packages tobe installed on virtual environment', default=THIS_PACKAGES)
    argp.add_argument('--workspace', help='Path to Church source workspace', default=THIS_WS)

    args = argp.parse_args()
    if args.venv:
        setup_venv(args.venv)

        if args.package:
            install_external_packages(args.venv, args.package)
    else:
        raise Exception("No virtual environment provided!")

    print("args.workspace =", args.workspace)
    install_workspace(args.workspace)
    bin_dir = get_bin_folder(args.venv)
    try:
        icon_file = os.path.join(bin_dir, "icon.exe")
        subprocess.run([icon_file], cwd=bin_dir)
    except Exception as ex:
        print("Fail to generate icons:", ex)

    print("\nInstallation completed successfully")
    print("Activate the environment using the command:")
    bin_dir = "Scripts" if IS_WINDOWS else "bin"
    activate_env = "" if IS_WINDOWS else "source "
    activate_env += os.path.join(args.venv, bin_dir, "activate")
    print("\t", activate_env, "\n")

if __name__ == "__main__":
    print(f"{THISDIR}\n{THIS_WS}")
    main()
