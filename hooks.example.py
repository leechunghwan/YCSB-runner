# This file contains example/dummy hooks for each possible hook location

def pre_db(db):
    print("hook pre_db: Starting", db.labelname)

def post_db(db):
    print("hook post_db: Finishing", db.labelname)

HOOKS = {
    "PRE_DB"    : [pre_db],
    "POST_DB"   : [post_db],

    "PRE_RUN"   : [],
    "POST_RUN"  : [],

    "PRE_TRIAL" : [],
    "POST_TRIAL": [],

    "PRE_MPL"   : [],
    "POST_MPL"  : [],
}
