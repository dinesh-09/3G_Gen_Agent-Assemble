# -*- coding: utf-8 -*-
"""
Created on Tue May  8 12:03:07 2018

@author: Demon King
"""
from class_product import *
from Read_File import Read_File  
import os.path
import traceback


def create_ID_dir(path,ret_op=0):
    stock_file = path+r'\ID_Dir_input.csv'
    if os.path.isfile(stock_file) == True:
        attrib_file = path
        stock_items = ID()
        stock_items.read_attribs(attrib_file)
        stock_items.read_out_file(stock_file)
        stock_items.create_comb()
        stock_items.populate_items(print_type=1)
        stock_items.write_file(path+'\\'+'ID_dir.csv')
        if ret_op==1:
            return(stock_items.content)
    else:
        raise Exception('ID_dir.csv not found at',path)

list_exc=[]
class ID(component):
    def gen_ids(self):
        import itertools
        from numpy import prod

        if self.var != '':
            self.var_cds = [self.convert_attr_to_code(m)[0][0] for m in self.var.split('-')]
            var_ats = [[m for m in self.attribs[n]] for n in self.var_cds]
            n_list=int(len(self.attrib_comb)/prod([len(n) for n in var_ats]))
            num = len(str(n_list))
            code='{0:0'+str(num)+'}'
            iid = [code.format(n) for n in range(1,n_list+1)]            

            # ******** Creating all possible combinations ******** #
            self.var_comb = ['-'.join(list(element)) for element in itertools.product(*var_ats)]

            iid = [[j+'-'+iid[i] for i in range(len(iid))] for j in self.var_comb]
            iid = [m for n in iid for m in n]
        else:
            n_list=len(self.attrib_comb)
            num = len(str(n_list))
            code='{0:0'+str(num)+'}'
            iid = [code.format(n) for n in range(1,n_list+1)]
            iid = [self.var + '-' + i for i in iid]
        
        self.iid=iid        
    

        
#with open(r'P:\out.txt', 'w') as f:
#    file_paths = Read_File(r'P:\paths-file.txt')
#    i,s,r,c=-1,0,0,0
#    file_paths = [path for path in file_paths if not path.startswith('#')]
#    for path in file_paths:
#        i+=1
#    print('\n\n*********Processing files at path ',path,'*********', file=f)
#
#    # **************************************************************** #
#    try: create_ID_dir(path)    
#    except Exception as e:
#        if i != len(file_paths)-1:
#            raise(e)
#            list_exc.append(i)
#            print('\nError in entry number',c,'in the list:', e, file=f)
#            traceback.print_exc()
#    
#    print('\nFolder list complete!')
#    if len(list_exc)!=0:
#        print('\n Exceptions occured in the following entries in the list : ',end="", file=f)
#        print(*list_exc, sep = ", ", file=f)