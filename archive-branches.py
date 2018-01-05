#!/usr/bin/env python

import commands
import sys
import subprocess
import time
import base_merge as bm

merge_path='archive_branches.log'

def usage():
    fname='%s' % sys.argv[0]
    print '''\033[32;1mexample:\033[0m
\033[33;1m%s\033[0m''' % fname


#write merge log to merge_path file.
def write_logs(content, merge_path):
    fobj = open(merge_path, 'a')
    for line in content:
	fobj.writelines(line+"\n")
    fobj.close()


def move_branches(svnpath):
    mv_branches_list = []
    svn_list_cmd = 'svn list %s' % svnpath
    #subprocess.call(svn_list_cmd,shell=True)
    bran_list=commands.getstatusoutput(svn_list_cmd)[1].__str__().split('\n')
    for branches in bran_list:
        if '_' in branches and ('2015' in branches or '2016' in branches):
	    brans=branches[:-1]
            archive_month = brans.split('_')[0][:6]
            svn_archive_month = svnpath + "/" + archive_month
            br_exist_cmd = 'svn info %s &> /dev/null' % svn_archive_month
            br_exist = commands.getstatusoutput(br_exist_cmd)[0]
            if br_exist != 0:
		print '\033[32;1mcreating %s\033[0m' % svn_archive_month
                cre_archive_month_cmd = 'svn mkdir %s -m "%s" ' % (svn_archive_month,"python script auto mkdir")
                subprocess.call(cre_archive_month_cmd, shell=True)
		time.sleep(0.1)
		#print cre_archive_month_cmd
            mv_bran_cmd = 'svn mv %s %s -m "%s" ' % (svnpath+'/'+brans, svn_archive_month, "python script auto archive.")
	    print "\033[31;1marchive %s\033[0m" % brans
            subprocess.call(mv_bran_cmd, shell=True)
	    time.sleep(0.1)
	    #print mv_bran_cmd
            mv_branches_list.append(svn_archive_month+"/"+brans)


    write_logs(mv_branches_list, merge_path)


def main():
    svn_modules_list=[]
    for key in bm.apps_dict.keys():
        svn_modules_list.append(bm.svn_base_path+bm.apps_dict[key]+"/branches")
    for module in svn_modules_list:
        move_branches(module)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        usage()
        sys.exit()
    main()
