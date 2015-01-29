# This file contains example/dummy hooks for each possible hook location
# For documentation, see https://github.com/benjaminbrent/YCSB-runner/wiki

def pre_run():
    print("hook pre_run: Starting run")

def post_run():
    print("hook post_run: Finishing run")

def pre_db(db):
    print("hook pre_db: Starting", db.labelname)

def post_db(db):
    print("hook post_db: Finishing", db.labelname)

def pre_trial(trial, db):
    print("hook pre_trial: Starting", trial, "on", db.labelname)

def post_trial(trial, db):
    print("hook post_trial: Finishing", trial, "on", db.labelname)

def pre_mpl(mpl, trial, db):
    print("hook pre_mpl: Starting MPL", mpl, "of trial", trial, "on", db.labelname)

def post_mpl(mpl, trial, db):
    print("hook post_mpl: Finishing MPL", mpl, "of trial", trial, "on", db.labelname)

# This dictionary must be defined
# All hooks are run in the order listed for each hook location
HOOKS = {
    "PRE_RUN"   : [pre_run],
    "POST_RUN"  : [post_run],

    "PRE_DB"    : [pre_db],
    "POST_DB"   : [post_db],

    "PRE_TRIAL" : [pre_trial],
    "POST_TRIAL": [post_trial],

    "PRE_MPL"   : [pre_mpl],
    "POST_MPL"  : [post_mpl],
}
