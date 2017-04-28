#!/usr/bin/env python
# -*- coding: utf8 -*-

import base_merge as bm
import sys
import time


def main():
    cre_day = time.strftime("%Y%m%d")
    operator = sys.argv[1]  #operator
    programer = sys.argv[2]  #programer
    branches_file = sys.argv[3]  #branches_file
    merge_log_path = '%s/%s_%s_merge.log' % (sys.path[0],cre_day,programer)  #20170325_changlh_merge.log
    merge_error_log_path = '%s/%s_%s_merge_error.log' % (sys.path[0],cre_day,programer) #20170325_changlh_merge_err.log

    branches_ori_dict = bm.get_ori_branches(branches_file)
    branches_new_dict = bm.create_new_branches(branches_ori_dict, operator,programer,cre_day,'pre-trunk')
    bm.merge(branches_ori_dict, branches_new_dict,merge_log_path)
    bm.format_output(branches_new_dict,'pre-trunkes')


if __name__ == '__main__':
    if len(sys.argv) == 1:
         bm.usage()
         sys.exit()
    if sys.argv[1] == '-h':
	 bm.usage()
         sys.exit()
    main()

