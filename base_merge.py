#!/usr/bin/env python
# -*- coding: utf8 -*-

import commands
import sys
import os
import time
import subprocess
import pexpect

def usage():
    fname='%s' % sys.argv[0]
    print '''\033[32;1mexample:\033[0m
\033[32;1m%s zjc changlh branches.txt\033[0m
\033[31;1mzjc\033[0m is operator name.
\033[31;1mchanglh\033[0m is programer name.
\033[31;1mbranches.txt\033[0m is file,has multiple branche links.''' % fname


svn_base_path = "http://192.168.1.13/code"

apps_dict = {"common": "/library/common"}

#write merge log to merge_path file.
def write_logs(content, merge_path):
    fobj = open(merge_path, 'a')
    fobj.writelines(content)
    fobj.close()


# return a dictionary for new braches,example {'common':'http://192.168.1.13/code/gopay_2.1/common/branches/20170315_common_zjc'}
def create_new_branches(branches,operator,programer,cre_day,merge_pattern):
    new_branches = {}
    for br_name in branches.keys():
        br_app = br_name.split("_")[1]
        if br_app=='cms':
            merge_pattern='pretrunk'
        br_fullName = "%s_%s_%s" % (cre_day, br_app, programer)
        new_branchName = '%s%s/%s/%s' % (svn_base_path, apps_dict[br_app],merge_pattern,br_fullName)
        br_exist_cmd='svn info %s &> /dev/null' % new_branchName
        br_exist=commands.getstatusoutput(br_exist_cmd)[0]
        if br_exist != 0:
                print '==> %s' % br_app
                cre_cmd = 'svn copy %s%s/trunk %s -m "%s" ' % (svn_base_path, apps_dict[br_app], new_branchName, operator)
                subprocess.call(cre_cmd, shell=True)
                time.sleep(0.1)
        new_branches[br_app] = new_branchName
        merge_pattern='pre-trunk'
    return new_branches

# return a dict,example {'20170312_common_zjc':'http://192.168.1.13/code/gopay_2.1/common/branches/20170312_common_zjc'}
def get_ori_branches(bran_file):
    fobj = open(bran_file)
    branches = fobj.readlines()
    ori_branches = {}
    for _br in branches:
        if _br != "\n":
            _name = _br.split("/")[-1]
            ori_branches[_name] = _br.strip()
    return ori_branches

def get_log_version(branch,merge_log_path):
    logs = os.popen("svn log --stop-on-copy %s" % branch)
    v_lines = logs.readlines()
    v_list=[]
    if (len(v_lines)) > 5:
        try:
            v_list.append(v_lines[1].split(" |")[0])
            v_list.append(v_lines[-4].split(" |")[0])
        except BaseException,e:
            print '%s  merge  error' % branch
            print e
            return 'error'
    else:
        v_logs = '%s dont merge,it is latest!\n' % branch
        write_logs('############################################\n', merge_log_path)
        write_logs(v_logs, merge_log_path)
        return 'latest'
    return v_list[1] + ":" + v_list[0]



def merge(ori_dict, new_dict,merge_log_path):
    print '==========start merge==============='
    for _name in ori_dict.keys():
        bran_name=_name.split('_')[1]
        svn_co_cmd = 'svn co %s %s &> /dev/null' % (new_dict[bran_name], bran_name)
        subprocess.call(svn_co_cmd, shell=True)
        os.chdir('./%s' % bran_name)
        versions = get_log_version(ori_dict[_name],merge_log_path)
        print '\033[32;1mstart merge [%s]\033[0m' % ori_dict[_name]
        print '\033[32;1m%s\033[0m\n' % versions
        time.sleep(0.1)
        if versions.startswith('r'):
            merge_dry_cmd = 'svn merge --dry-run -%s %s' % (versions, ori_dict[_name])
            merge_info = os.popen(merge_dry_cmd)
            info_list = list(merge_info.readlines())
            if len(info_list):
                if "冲突" in info_list[-1]:
                    merge_cmd = 'svn merge -%s %s' % (versions, ori_dict[_name])
                    try:
                        child = pexpect.spawn(merge_cmd)
                        while child.expect('选择:') == 0:
                            child.sendline("p")
                    except pexpect.EOF:
                        print '\033[32;1m%s 冲突已解决！！！\033[0m' % bran_name
                        pass
                    except pexpect.TIMEOUT:
                        pass
                    conflict_logs = os.popen("svn resolved -R .")
                    write_logs('############################################\n', merge_log_path)
                    conflict_brname = '%s merge has conflict!!!!\n' % ori_dict[_name]
                    write_logs(conflict_brname, merge_log_path)
                    write_logs(conflict_logs.readlines(), merge_log_path)
                else:
                    merge_cmd = 'svn merge -%s %s' % (versions, ori_dict[_name])
                    subprocess.call(merge_cmd,shell=True)
            commit_cmd = 'svn ci -m "merge -%s %s "' % (versions, ori_dict[_name])
            subprocess.call(commit_cmd, shell=True)
        os.chdir('./..')
        rm_cmd = 'rm -rf %s' % bran_name
        subprocess.call(rm_cmd, shell=True)
        time.sleep(0.3)
	row_str='============================'
        print row_str
    end_str='===========end=============='
    print end_str
    end_time=time.ctime()
    write_logs(row_str+'\n'+'End time is: '+end_time +'\n'+end_str+'\n',merge_log_path)



def format_output(branches,merge_pattern):
	width=120
	print '\033[32;1mnew %s:\033[0m' % merge_pattern
	print '+%s+' % ('*' * width)
	for bran in branches.values():
	    print '%s' % (bran)
	print '+%s+' % ('*' * width)
