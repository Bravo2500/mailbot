#!/bin/env python
# -*- coding: utf-8 -*-


"""

"""

TASKIN_SUFFIX = ".data.json"
TASKOUT_SUFFIX = ".result.json"

from datetime import datetime
import json
import sys, os, shutil


def err(msg):
    sys.stderr.write(msg+"\n")
#--

def flush_result(res, of):
    tmp = of+".tmp"
    json.dump(res, open(tmp,"w+"), ensure_ascii=False)
    shutil.move(tmp, of)
#--

def process_file(base_dir, in_name, out_name):

    of = os.path.join(base_dir, out_name)
    open(of, "w+").close() # touch output

    try:
        task = json.load( open(os.path.join(base_dir, in_name)) )
    except ValueError as ex:
        err("Unable to load: "+in_name+"\n"+str(ex))
        return

    res = dict(pid=os.getpid(), ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    flush_result(res, of)


    # do_task( task, of )
#--

def scandir(base_dir):
    fls = sorted(os.listdir(base_dir))
    sl = len(TASKIN_SUFFIX)
    for f in fls:
        if f.endswith(TASKIN_SUFFIX):
            out = f[:-sl]+TASKOUT_SUFFIX
            if out in fls:
                continue
            process_file(base_dir, f, out)
            return
        #-
    #-
#--

if __name__ == "__main__":

    if len(sys.argv) > 1:
        scandir(sys.argv[1])
    else:
        sys.stderr.write("Parameter missing\n")
        sys.exit(1)
    #-
#.
