#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import time
import subprocess
import pexpect
import base_merge as bm


def usage():
    print '''\033[31;1mexample:\033[0m
python trunk_merge.py zjc trunkes.txt
\033[31;1mzjc\033[0m is operator name.
\033[31;1mtrunkes.txt\033[0m is file,has multiple trunk links.'''


svn_base_path = "http://192.168.1.13/code/gopay_2.1"
cre_day = time.strftime("%Y%m%d")
merge_log_path = '%s/%s_merge.log' % (sys.path[0], cre_day)
merge_error_log_path = '%s/merge_error.log' % sys.path[0]


def write_logs(content, merge_path):
    fobj = open(merge_path, 'a')
    fobj.writelines(content)
    fobj.close()


# return a dictionary for new braches,example {'common':'http://192.168.1.13/code/gopay_2.1/common/branches/20170315_common_zjc'}
def create_new_branches(branches, user):
    new_branches = {}
    for br_name in branches.keys():
        new_branchName = '%s%s/trunk' % (svn_base_path, bm.apps_dict[br_name])
        new_branches[br_name] = new_branchName
    return new_branches


# return a dict,example {'common':'http://192.168.1.13/code/gopay_2.1/common/branches/20170312_common_zjc'}
def get_ori_branches(bran_file):
    fobj = open(bran_file)
    branches = fobj.readlines()
    ori_branches = {}
    for _br in branches:
        if _br != "\n":
            _name = _br.split("/")[-1].split("_")[1]
            ori_branches[_name] = _br.strip()
    fobj.close()
    return ori_branches


def get_log_version(branch):
    logs = os.popen("svn log --stop-on-copy %s" % branch)
    v_lines = logs.readlines()
    v_list = []
    if (len(v_lines)) > 5:
        try:
            v_list.append(v_lines[1].split(" |")[0])
            v_list.append(v_lines[-4].split(" |")[0])
        except BaseException, e:
            print '%s  merge  error' % branch
            print e
            return 'error'
    else:
        v_logs = '%s dont merge,it is latest!\n' % branch
        time.sleep(0.1)
        write_logs('############################################\n', merge_log_path)
        write_logs(v_logs, merge_log_path)
        return 'latest'
    return v_list[1] + ":" + v_list[0]


def merge(ori_dict, new_dict):
    print '==========start merge==============='
    for bran_name in new_dict:
        svn_co_cmd = 'svn co %s %s &> /dev/null' % (new_dict[bran_name], bran_name)
        subprocess.call(svn_co_cmd, shell=True)
        os.chdir('./%s' % bran_name)
        versions = get_log_version(ori_dict[bran_name])
        print '\033[32;1mstart merge %s...\033[0m' % bran_name
        print '\033[32;1m%s\033[0m\n' % versions
        time.sleep(0.1)
        if versions.startswith('r'):
            merge_dry_cmd = 'svn merge --dry-run -%s %s' % (versions, ori_dict[bran_name])
            merge_info = os.popen(merge_dry_cmd)
            info_list = list(merge_info.readlines())
            if len(info_list):
                if "冲突" in info_list[-1]:
                    write_logs('############################################\n', merge_log_path)
                    conflict_brname = '%s merge has conflict!!!!\n' % bran_name
                    print conflict_brname
                    time.sleep(0.2)
                    write_logs(conflict_brname, merge_log_path)
                    # write_logs(conflict_logs.readlines(), merge_log_path)
                    continue
                else:
                    merge_cmd = 'svn merge -%s %s' % (versions, ori_dict[bran_name])
                    subprocess.call(merge_cmd, shell=True)
                commit_cmd = 'svn ci -m "merge -%s %s "' % (versions, ori_dict[bran_name])
                subprocess.call(commit_cmd, shell=True)
        os.chdir('./..')
        rm_cmd = 'rm -rf %s' % bran_name
        subprocess.call(rm_cmd, shell=True)
        time.sleep(0.2)
        print '============================'
    print '===========end=============='


def main():
    branches_dict = {}
    user = sys.argv[1]
    branches_file = sys.argv[2]
    branches_ori_dict = get_ori_branches(branches_file)
    branches_new_dict = create_new_branches(branches_ori_dict, user)
    merge(branches_ori_dict, branches_new_dict)


if __name__ == '__main__':
    arg_one = sys.argv[1]
    if arg_one == '-h' or arg_one == '--help':
        usage()
        sys.exit()
    main()
