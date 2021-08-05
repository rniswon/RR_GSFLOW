import os, sys
import shutil
import socket
import platform
import time
import multiprocessing as mp
import subprocess as sp
from datetime import datetime

def remove_readonly(func, path, excinfo):
    """remove readonly dirs, apparently only a windows issue
    add to all rmtree calls: shutil.rmtree(**,onerror=remove_readonly), wk"""
    os.chmod(path, 128) #stat.S_IWRITE==128==normal
    func(path)

def start_slaves(slave_dir, exe_rel_path, pst_rel_path, num_slaves=None, slave_root="..",
                 port=4004, rel_path=None, local=True, cleanup=True, master_dir=None,
                 verbose=False, silent_master=False, run_cmd = None):
    #warnings.warn("deprecation warning:start_slaves() has been emancipated and renamed start_workers()", PyemuWarning)
    #from pyemu.utils import start_workers
    start_workers(worker_dir=slave_dir,exe_rel_path= exe_rel_path, pst_rel_path=pst_rel_path, num_workers=num_slaves,
                  worker_root=slave_root, port=port, rel_path=rel_path,
                  local=local, cleanup=cleanup, master_dir=master_dir, verbose=verbose, silent_master=silent_master,
                  run_cmd = run_cmd)


def start_workers(worker_dir,exe_rel_path,pst_rel_path,num_workers=None,worker_root="..",
                 port=4004,rel_path=None,local=True,cleanup=True,master_dir=None,
                 verbose=False,silent_master=False, run_cmd = None):
    """ start a group of pest(++) workers on the local machine

    Parameters
    ----------
    worker_dir :  str
        the path to a complete set of input files
    exe_rel_path : str
        the relative path to the pest(++) executable from within the worker_dir
    pst_rel_path : str
        the relative path to the pst file from within the worker_dir
    num_workers : int
        number of workers to start. defaults to number of cores
    worker_root : str
        the root to make the new worker directories in
    rel_path: str
        the relative path to where pest(++) should be run from within the
        worker_dir, defaults to the uppermost level of the worker dir
    local: bool
        flag for using "localhost" instead of hostname on worker command line
    cleanup: bool
        flag to remove worker directories once processes exit
    master_dir: str
        name of directory for master instance.  If master_dir
        exists, then it will be removed.  If master_dir is None,
        no master instance will be started
    verbose : bool
        flag to echo useful information to stdout
    silent_master : bool
        flag to pipe master output to devnull.  This is only for
        pestpp Travis testing. Default is False

    Note
    ----
    if all workers (and optionally master) exit gracefully, then the worker
    dirs will be removed unless cleanup is false

    Example
    -------
    ``>>>import pyemu``

    start 10 workers using the directory "template" as the base case and
    also start a master instance in a directory "master".

    ``>>>pyemu.helpers.start_workers("template","pestpp","pest.pst",10,master_dir="master")``

    """

    assert os.path.isdir(worker_dir)
    assert os.path.isdir(worker_root)
    if num_workers is None:
        num_workers = mp.cpu_count()
    else:
        num_workers = int(num_workers)
    #assert os.path.exists(os.path.join(worker_dir,rel_path,exe_rel_path))
    exe_verf = True

    if rel_path:
        if not os.path.exists(os.path.join(worker_dir,rel_path,exe_rel_path)):
            #print("warning: exe_rel_path not verified...hopefully exe is in the PATH var")
            exe_verf = False
    else:
        if not os.path.exists(os.path.join(worker_dir,exe_rel_path)):
            #print("warning: exe_rel_path not verified...hopefully exe is in the PATH var")
            exe_verf = False
    if rel_path is not None:
        assert os.path.exists(os.path.join(worker_dir,rel_path,pst_rel_path))
    else:
        assert os.path.exists(os.path.join(worker_dir,pst_rel_path))
    if local:
        hostname = "localhost"
    else:
        hostname = socket.gethostname()

    base_dir = os.getcwd()
    port = int(port)

    if os.path.exists(os.path.join(worker_dir,exe_rel_path)):
        if "window" in platform.platform().lower():
            if not exe_rel_path.lower().endswith("exe"):
                exe_rel_path = exe_rel_path + ".exe"
        else:
            if not exe_rel_path.startswith('./'):
                exe_rel_path = "./" + exe_rel_path

    if master_dir is not None:
        if master_dir != '.' and os.path.exists(master_dir):
            try:
                shutil.rmtree(master_dir,onerror=remove_readonly)#, onerror=del_rw)
            except Exception as e:
                raise Exception("unable to remove existing master dir:" + \
                                "{0}\n{1}".format(master_dir,str(e)))
        if master_dir != '.':
            try:
                shutil.copytree(worker_dir,master_dir)
            except Exception as e:
                raise Exception("unable to copy files from base worker dir: " + \
                                "{0} to master dir: {1}\n{2}".\
                                format(worker_dir,master_dir,str(e)))

        args = [exe_rel_path, pst_rel_path, "/h", ":{0}".format(port)]
        if rel_path is not None:
            cwd = os.path.join(master_dir,rel_path)
        else:
            cwd = master_dir
        if verbose:
            print("master:{0} in {1}".format(' '.join(args),cwd))
        stdout=None
        if silent_master:
            stdout = open(os.devnull,'w')
        try:
            os.chdir(cwd)
            master_p = sp.Popen(args,stdout=stdout)#,stdout=sp.PIPE,stderr=sp.PIPE)
            os.chdir(base_dir)
        except Exception as e:
            raise Exception("error starting master instance: {0}".\
                            format(str(e)))
        time.sleep(1.5) # a few cycles to let the master get ready


    tcp_arg = "{0}:{1}".format(hostname,port)
    procs = []
    worker_dirs = []
    for i in range(num_workers):
        new_worker_dir = os.path.join(worker_root,"worker_{0}".format(i))
        if os.path.exists(new_worker_dir):
            try:
                shutil.rmtree(new_worker_dir,onerror=remove_readonly)#, onerror=del_rw)
            except Exception as e:
                raise Exception("unable to remove existing worker dir:" + \
                                "{0}\n{1}".format(new_worker_dir,str(e)))
        try:
            shutil.copytree(worker_dir,new_worker_dir)
        except Exception as e:
            raise Exception("unable to copy files from worker dir: " + \
                            "{0} to new worker dir: {1}\n{2}".format(worker_dir,new_worker_dir,str(e)))
        try:
            if exe_verf:
                # if rel_path is not None:
                #     exe_path = os.path.join(rel_path,exe_rel_path)
                # else:
                exe_path = exe_rel_path
            else:
                exe_path = exe_rel_path
            args = [exe_path, pst_rel_path, "/h", tcp_arg]
            #print("starting worker in {0} with args: {1}".format(new_worker_dir,args))
            if rel_path is not None:
                cwd = os.path.join(new_worker_dir,rel_path)
            else:
                cwd = new_worker_dir

            os.chdir(cwd)
            if verbose:
                print("worker:{0} in {1}".format(' '.join(args),cwd))
            with open(os.devnull,'w') as f:
                #args = ['start', '/B', 'start',  'cmd.exe', '@cmd', '/k', run_cmd ]
                #p = sp.Popen(args,stdout=f,stderr=f)
                ccc = "start /B start cmd.exe @cmd /k " + run_cmd
                time.sleep(2.0)
                p = os.system(ccc)
            procs.append(p)
            os.chdir(base_dir)
        except Exception as e:
            raise Exception("error starting worker: {0}".format(str(e)))
        worker_dirs.append(new_worker_dir)

    if master_dir is not None:
        # while True:
        #     line = master_p.stdout.readline()
        #     if line != '':
        #         print(str(line.strip())+'\r',end='')
        #     if master_p.poll() is not None:
        #         print(master_p.stdout.readlines())
        #         break
        if silent_master:
            # this keeps travis from thinking something is wrong...
            while True:
                rv = master_p.poll()
                if master_p.poll() is not None:
                    break
                print(datetime.now(), "still running")
                time.sleep(5)
        else:
            master_p.wait()
            time.sleep(1.5) # a few cycles to let the workers end gracefully

    # NOTE: Saalem commented out everything below this on 7/22/21 because p.kill() and p.wait() have different functionality on Windows vs. Linux computers, was causing an error on Windows
    #       Will need to manually delete the workers when finished with PEST run

    #     # kill any remaining workers
    #     for p in procs:
    #         p.kill()
    #
    # # this waits for sweep to finish, but pre/post/model (sub)subprocs may take longer
    # for p in procs:
    #      p.wait()
    # if cleanup:
    #     cleanit=0
    #     while len(worker_dirs)>0 and cleanit<100000: # arbitrary 100000 limit
    #         cleanit=cleanit+1
    #         for d in worker_dirs:
    #             try:
    #                 shutil.rmtree(d,onerror=remove_readonly)
    #                 worker_dirs.pop(worker_dirs.index(d)) #if successfully removed
    #             except Exception as e:
    #                 #warnings.warn("unable to remove slavr dir{0}:{1}".format(d,str(e)),PyemuWarning)
    #                 pass


