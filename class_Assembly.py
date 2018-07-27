# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 08:51:56 2018

@author: Demon King
"""
from class_product import *
import os

class assembly(component):
    # ********************* Initialise ******************** #
    def __init__(self,order_desc):
        component.__init__(self)    
        self.sa_list=[]
    # ********************* Fetch Sub-Assembly List ******************** #
    def fetch_sa_list(self):
        self.dir_struct = [m for m in os.walk(os.getcwd())]
        sa_list=[]
        sa_index = 0
        end_flag=0
        pr_dir = self.dir_struct[0][0]
        
        for dir_ind in range(len(self.dir_struct)):

            if end_flag!=1:
                if len(sa_list)==0:
                    if 'Attributes_input.csv' not in self.dir_struct[dir_ind][-1] or self.dir_struct[dir_ind][1]==[]: 
                        raise Exception('The main assembly level does not have '+\
                                        'any sub-assemblies or Attributes_input.csv is not present')
                    else:
                        sa_list=[[m] for m in self.dir_struct[0][1] if not m=='3G order dirs']
                        sa_dir = pr_dir+'\\'+sa_list[sa_index][0]

                else: # sa_index increment loop
                    while sa_dir not in self.dir_struct[dir_ind][0]:
                        if sa_index!=len(sa_list)-1:
                            sa_index+=1
                            sa_dir = pr_dir+'\\'+sa_list[sa_index][0]
                        else:
                            end_flag=1
                            break
                curr_dir=sa_dir
                #sa_dir = pr_dir+'\\'+sa_list[sa_index]
            if self.dir_struct[dir_ind][1] != [] and dir_ind!=0: # Has sub-directories hence possible sub-assemblies
                #if dir_struct[dir_ind][-1]==[]: # The current folder is a Variant/Variant group
                    #continue # kept here for a near-future update to gather variant list
                if 'Attributes_input.csv' in self.dir_struct[dir_ind][-1]: # Is a subassembly
                    if self.dir_struct[dir_ind][0] !=sa_dir:
                        fold_list = [(self.dir_struct[dir_ind][0]+'\\'+m) for m in self.dir_struct[dir_ind][1]]
                        if len(sa_list[sa_index])==1:
                            sa_list[sa_index].append([fold_list]) # Sub Assembly Name
                        else:
                            sa_list[sa_index][1].append(fold_list) # Sub Assembly Name
                        
                    
                
                
        