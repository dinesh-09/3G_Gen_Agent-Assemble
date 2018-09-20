# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 08:51:56 2018

@author: Demon King
"""
from class_Assembly import assembly
import os
import traceback
from copy import deepcopy
from configure_Linia import configure_Linia as fit_8_3
           
# ************************************************************************************** #
       
class Linia(assembly):

    # ********************** Initialise ********************** #
        
    def __init__(self,name='',level=-1):
        assembly.__init__(self,name,level)

    # ******************************************************** #
    def configure(self,order_attribs):
        linia_cat = order_attribs[0].strip("4").strip("2")
        linia_shape = order_attribs[-2]
        linia_config = order_attribs[-1]
        if linia_cat=='PLI' or linia_cat=='SLI':
            pflag=1
            if linia_cat=='PLI':
                pend=1
        else:
            pend=0
            pflag=0
    
        linia_config = linia_config.split('X')  
        
        if linia_shape!='T' or linia_shape!='X': 
            suffix='C'
        elif linia_shape=='T': 
            suffix='T'
        elif linia_shape=='X': 
            suffix='X'
        
        linia_config = [int(n) for n in linia_config]   
        if len(linia_config) > 1:
            for n in range(len(linia_config)):
                linia_config[n] -= 1
                if len(linia_config)>2 and n>0 and n<len(linia_config)-1:
                    linia_config[n] -= 1
        lengths=[fit_8_3(leg,pend,ret_op=1) for leg in linia_config]
        op = []
        n_legs=len(lengths)
        
        for leg_no in range(n_legs):
            desc_suff = []    
            if n_legs==1: # Standard section
                if len(lengths[0])>1: # S+J and/or E present
                    desc_suff.append(['SS', lengths[leg_no][0][0],lengths[leg_no][0][1]])
                    if len(lengths[0])>2: # Joiner Present
                        [desc_suff.append(n) for n in [['J',m[0],m[1]] for m in lengths[leg_no][1:-1]]]
                        desc_suff.append(['E', lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                    else: # Only Ender Present
                        desc_suff.append(['E', lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                else:
                    desc_suff.append(['S', lengths[leg_no][0][0],lengths[leg_no][0][1]])
                
            else: # Not a Straight Run 
                if pflag==0: # Not a Pendant or Surface Linia
                    if leg_no==0: # Need a Starter
                        if len(lengths[leg_no])==1:
                            desc_suff.append(['SSB', lengths[leg_no][0][0],lengths[leg_no][0][1]])
                        else:
                            desc_suff.append(['SS',lengths[leg_no][0][0],lengths[leg_no][0][1]])
                            if len(lengths[leg_no])>2:
                                [desc_suff.append(n) for n in [['J', m[0],m[1]] for m in lengths[leg_no][1:-1]]]
                            desc_suff.append(['JB',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
    
                            
                    #lengths[leg_no] = lengths[leg_no][::-1] # Largest Sections First ? 
                    elif leg_no != n_legs-1:
                        if len(lengths[leg_no])>1:
                            desc_suff.append(['JA',lengths[leg_no][0][0],lengths[leg_no][0][1]])
                            if len(lengths[leg_no])>2:
                                [desc_suff.append(n) for n in [['J', m[0],m[1]] for m in lengths[leg_no][1:-1]]]
                            desc_suff.append(['JB',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                        else: # Both sides is a section
                            desc_suff.append(['JAB',lengths[leg_no][0][0],lengths[leg_no][0][1]])
                    elif leg_no == n_legs-1: # Last Section
                        if len(lengths[leg_no])>1: # Joiners present
                            desc_suff.append(['JA', lengths[leg_no][0][0],lengths[leg_no][0][1]])
                            if len(lengths[leg_no])>2:
                                [desc_suff.append(n) for n in [['J', m[0],m[1]] for m in lengths[leg_no][1:-1]]]
                            desc_suff.append(['E',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                        else: # Only Ender
                            desc_suff.append(['EA', lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                else:
                    if leg_no==0: # Need a Starter
                        if len(lengths[leg_no])==1:
                            desc_suff.append(['SSB', lengths[leg_no][0][0],lengths[leg_no][0][1]])
                        else:
                            desc_suff.append(['SS',lengths[leg_no][0][0],lengths[leg_no][0][1]])
                            if len(lengths[leg_no])>2:
                                [desc_suff.append(n) for n in [['J',m[0],m[1]] for m in lengths[leg_no][1:-1]]]
                            desc_suff.append(['JB',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
    
                            
                    #lengths[leg_no] = lengths[leg_no][::-1] # Largest Sections First ? 
                    elif leg_no != n_legs-1:
                        if len(lengths[leg_no])>1:
                            [desc_suff.append(n) for n in [['J',m[0],m[1]] for m in lengths[leg_no][:-1]]]
                            desc_suff.append(['JB',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                        else: # Both sides is a section
                            desc_suff.append(['JAB',lengths[leg_no][0][0],lengths[leg_no][0][1]])
                        
                    elif leg_no == n_legs-1: # Last Section
                        if len(lengths[leg_no])>1: # Joiners present
                            [desc_suff.append(n) for n in [['J',m[0],m[1]] for m in lengths[leg_no][:-1]]]
                        desc_suff.append(['E',lengths[leg_no][-1][0],lengths[leg_no][-1][1]])
                if leg_no != n_legs-1:
                    desc_suff.append([suffix,"1'",1])
            op.extend([order_attribs[:-2]+m for m in desc_suff])
        #op2 = op.copy()
        op = [['-'.join(o[:-1]),o[-1]] for o in op]
        op = [list(n) for n in zip(*op)]
        unq_val=[]
        [unq_val.append(o) for o in op[0] if o not in unq_val]
        dups = [[i for i in range(len(op[0])) if op[0][i]==o] for o in unq_val]
        op[1] = [sum([op[1][i] for i in d]) for d in dups]
        op[0] = [op[0][d[0]] for d in dups]
        op = [list(n) for n in zip(*op)]
        op = [o[0].split('-')+[o[1]] for o in op]
        return(op)

    # ******************************************************** #
    def cr_content(self,attribs):  # Basically this function runs almost the old BOM Automator
        import operator
        self.attrib_comb=[attribs]
        if self.level==0:
            ats=attribs[:-1]+[self.attribs[-1][0]]
            self.calc_id(ats)
            iid = self.iid[0].split('-')
            iid[-2] = attribs[-1]
            self.iid = ['-'.join(iid)]
        else:
            self.read_id_dir() 
            self.search_id(attribs)
        try:            

            # ***************** Stock Items *********************** #
            self.read_out_file(self.path+r'\Stock_Items.csv')
            self.p_header=self.header
            self.p_content=self.populate_items\
                (id_no=0,attrib=attribs,mute=1)
        
        # ********************** Routing ********************** #
            self.read_routing_infile(self.path+r'\ROUTING_LIST.csv')
            self.read_out_file(self.path+r'\Routing.csv')
            self.r_header=self.header
            self.create_routing_content(mute=1)
            self.r_content=deepcopy(self.content)
                          
        # ********************* Components ********************* #
            self.read_comp_infile(self.path+r'\COMPONENTS_LIST.csv')
            self.read_out_file(self.path+r'\Components.csv')
            self.c_header=self.header.copy() 
            if self.level!=0:
                self.create_components_content(mute=1)
                self.c_content=deepcopy(self.content)
            else:
                self.comp_list = [list(n) for n in zip(*self.comp_list)] # Transposing
                done_list=[]
                comp_len=len(self.comp_list[0])
                curr_index = 0
                for i in range(comp_len):
                    dups = [j for j, x in enumerate(self.comp_list[0]) if j not in done_list and x == self.comp_list[0][i]]
                    self.comp_list[0] = [str(curr_index)+'+'+self.comp_list[0][m] \
                                  if m in dups and m not in done_list else self.comp_list[0][m] for m in range(comp_len)]
                    done_list.extend(dups)
                    if dups != []:
                        curr_index +=1
                self.comp_list = [list(n) for n in zip(*self.comp_list)] # Transposing
                cont_base = deepcopy(self.content)
                add_on_cont=[]

                for ind in range(len(self.sa_list)):
                    self.header = self.c_header.copy()
                    self.content = deepcopy(cont_base)
                    sq = str(self.sa_list[ind][-1])
                    self.attrib_comb = [self.sa_list[ind][:-1]]
                    self.create_components_content(mute=1)                  
                    qty_ind=self.header.index("Usage Qty")
                    for s in self.content:
                        if s[qty_ind]=='x' and not any([s=='C' or s=='T' or s=='X' for s in self.sa_list[ind][:-1]]):
                            s[qty_ind]=str(sq)  
                    add_on_cont.extend(self.content)
                comp_ind=self.header.index("Component")
                fix_ind= self.header.index('Fixed Qty')
                add_on_cont = sorted(add_on_cont,key=operator.itemgetter(comp_ind))
                curr_num=-1
                curr_entry=[]
                del_list=[]
                
                for ind in range(len(add_on_cont)):
                    num,add_on_cont[ind][comp_ind] = add_on_cont[ind][comp_ind].split('+')
                    num=int(num)
                    if num!=curr_num:
                        curr_entry=add_on_cont[ind]
                        if curr_entry[qty_ind] != '' and curr_entry[qty_ind] != 'x':
                            curr_entry[qty_ind] = int(curr_entry[qty_ind])
                        if add_on_cont[ind][qty_ind] == 'x':
                            del_list.append(ind)
                        curr_num = num
                    else:
                        if type(curr_entry[qty_ind]) is not str:
                            if add_on_cont[ind][fix_ind] != 'T' and add_on_cont[ind][qty_ind]!='x':
                                curr_entry[qty_ind] += int(add_on_cont[ind][qty_ind])
                            del_list.append(ind)
                        else:
                            if add_on_cont[ind][qty_ind] != 'x' and add_on_cont[ind][qty_ind] != '':         
                                curr_entry[qty_ind] = int(add_on_cont[ind][qty_ind])
                            else:
                                del_list.append(ind)
                self.c_content = []        
                for ind in range(len(add_on_cont)):
                    if ind not in del_list:
                        add_on_cont[ind][qty_ind] = str(add_on_cont[ind][qty_ind])
                        self.c_content.append(add_on_cont[ind])                    

            self.c_header=self.header
        except:
            print('Error found at',self.path,traceback.format_exc())
            raise
            
    # ******************************************************** #
    def map_assm(path): #Rewriting since the class to be called changes
        # path should belong to the folder where all standard files are stored
        from copy import deepcopy
        import operator
        
        os.chdir(path)    
        assm_map = None
        curr_obj=None
        
        for fold in os.walk(os.getcwd()):
            if assm_map is None:
                if 'Attributes_input.csv' not in fold[2]:
                    raise Exception('The files not present at the location ',path)
                else:
                    pr_assm = fold[0]

                    fold_obj = Linia(fold[0],0)
                    fold_obj.path=fold[0]
                    fold_obj.read_attribs(fold_obj.path)
                    if fold_obj.attribs[0]!=['']:
                        fold_obj.attribs.insert(0,[''])
                    fold_obj.glob_attribs = deepcopy(fold_obj.attribs)
                    fold_obj.is_assm=1

                    assm_map = fold_obj
                    curr_obj = assm_map
            else:
                try:
                    prev_arr=name_arr.copy()
                except:
                    pass
                name_arr = [n for n in (fold[0].replace(pr_assm,"")).split("\\") if n!='']
                        
                if not any([n=='3G order dirs' for n in name_arr]):
                    fold_obj = Linia(name_arr[-1],len(name_arr)) # New Object
                    if '(' in fold_obj.name: #
                        fold_obj.is_assm = 0
                        # Splitting to discard the folder category name
                        fold_obj.name,name =  fold_obj.name.split('(')
                        name = name.replace(')','').split('-')
                        fold_obj.cat=[[n[0][0] for n in assm_map.convert_attr_to_code(m,sub_conv_flag=1)] for m in name]
                        fold_obj.cat = sorted(fold_obj.cat,key=operator.itemgetter(1))
                    else:
                        m = assm_map.convert_attr_to_code(fold_obj.name,sub_conv_flag=1)

                        if m[0][0][0]!=-1:  
                            fold_obj.cat=[n[0][0] for n in m]
                            fold_obj.is_assm = 0
                        else:
                            fold_obj.is_assm = 1
                            
                                
                    if fold_obj.is_assm ==1:
                        if 'Attribute_excl.csv' in fold[2]:
                            excl_list = fold_obj.transfer_csv(fold[0]+'\\'+'Attribute_excl.csv')
                            fold_obj.attr_excl_list = [[assm_map.convert_attr_to_code(e[0])[0][0],e] for e in excl_list]
                                
                    if 'Attributes_input.csv' in fold[2]:
                        fold_obj.path=fold[0]
                        fold_obj.read_attribs(fold_obj.path)
                        if fold_obj.attribs[0]!=['']:
                            fold_obj.attribs.insert(0,[''])
                        dumm_obj=curr_obj
                        while dumm_obj.level>=fold_obj.level: # Finding parent, to convert them to loc_at_typs
                            dumm_obj=dumm_obj.prnt
                        while dumm_obj.attribs==[]:
                            dumm_obj=dumm_obj.prnt
                        # Ensuring atleast one of the local attributes of each type is present in smpl ats    
                        loc_codes = [dumm_obj.convert_attr_to_code(m[0])[0][0] for m in fold_obj.attribs[1:]]    
                        smpl_ats = [a[0] for a in dumm_obj.attribs[1:]]
                        for i in range(len(loc_codes)):
                            if loc_codes[i]!=-1:smpl_ats[loc_codes[i]-1] = fold_obj.attribs[i+1][0] 
                        if 'Attr_conv.csv' in fold[2]:
                            file = fold_obj.transfer_csv(fold[0]+'\\'+'Attr_conv.csv')
                            file = [f[0] for f in file]
                            fold_obj.cr_dict(assm_map,file)
                            # Ensuring that the input item types in the dictionary are present in the smpl ats
                            in_vars = [[m for m in tl.dic.keys()][0] for tl in fold_obj.tlator]
                            in_typs = [m for tl in fold_obj.tlator for m in tl.in_typ]
                            for s in range(len(in_typs)): 
                                smpl_ats[in_typs[s]-1] = in_vars[s]
                            smpl_ats = fold_obj.conv_to_loc(smpl_ats,ances=assm_map) 
                        fold_obj.loc_at_typs=[fold_obj.convert_attr_to_code(a)[0][0] for a in smpl_ats]

                    # Navigating back until parent level is reached
                    while curr_obj.level >= fold_obj.level:  # Traversing up                 
                        curr_obj = curr_obj.prnt

                    curr_obj.place_folder(fold_obj)
                    curr_obj = fold_obj
         

        curr_obj.back_prop() # To back propagate data from last folder in the list
        return(assm_map)
            
    # ******************************************************** #
    # Currently not able to handle options 
    def fetch_content(self,order_attribs,prnt_level,prefix=None,assm=None): 
        if prefix is None:
            if self.level==0:
                prefix='3G'
                assm=self
            elif self.is_assm==1:
                prefix=self.name

        self.p_id = prefix
        ret_obj = Linia(self.name,prnt_level+1)
        ret_obj.attribs=self.attribs
        if self.attribs!=[]:
            ret_obj.path=self.path

       # Filtering out non-combs
        if self.non_combs != []:
            non_combs=[[n for n in m if n!=''] for m in self.non_combs]
            ncc = self.convert_attr_to_code(non_combs)
            if any([all([order_attribs[ncc[l][ind]-1]==non_combs[l][ind] for ind in range(len(ncc[l]))])\
                    for l in range(len(ncc))]):
                    e = 'The order '+'-'.join(order_attribs)+' contains a disallowed combination'
                    raise ValueError(e)
#        comp_list = []
        loc_flag=0
        
        #  ***************** Fetching any components from the children ***************** #    
        if loc_flag==0:
            loc_attribs=order_attribs
        if self.level==0:
            loc_attribs = self.configure(loc_attribs)
#            unq_val=[]
#            [unq_val.append(o) for o in op[0] if o not in unq_val]
#            dups = [[i for i in range(len(op[0])) if op[0][i]==o] for o in unq_val]
#            op[1] = [[0+op[1][i] for i in d] for d in dups]
#            op[0] = [d[0] for d in dups]
#            op = [list(n) for n in zip(*op)]
            self.sa_list = deepcopy(loc_attribs)            
            ret_obj.sa_list = deepcopy(loc_attribs)
        if self.child is not None:
            ret_obj.child=[]
            for child in self.child:
                if child.is_assm == 1: # Selecting the Sub-Assm
                    if child.attr_excl_list!=[]:
                        true_flag = [any([l[e[0]-1] in e[1] for e in child.attr_excl_list]) for l in loc_attribs]    
                        if all(true_flag):
                            continue
                        ind_list = [ind for ind in range(len(true_flag)) if true_flag[ind] is True]
                    else: 
                        ind_list = list(range(len(loc_attribs)))        
                    # Inserting the correct objects
                    for ind in ind_list:
                        ret_obj.place_folder(child.fetch_content(loc_attribs[ind],ret_obj.level,assm=assm))
                else:                        
                    if type(loc_attribs[0]) is list:
                        true_flag = any([a==child.name for l in loc_attribs for a in l])
                    else:
                        true_flag = any([a==child.name for a in loc_attribs])
                    if true_flag:
                        ret_obj.place_folder(child.fetch_content(loc_attribs,ret_obj.level\
                                                                 ,prefix=self.p_id,assm=assm))

        #  ************** Fetching any components from the current folder ************** #

        if self.attribs != []: # Stock,Routing,Components are present in the object
            
            # ***** Converting global attributes to local, if any, for selection ******* #
            
            if type(order_attribs[-1]) is int:
                ret_obj.qty=order_attribs[-1]
                order_attribs = order_attribs[:-1]
                
            try:
                loc_attribs=self.conv_to_loc(order_attribs,assm)
                loc_flag=1
            except Exception as e: # Insert line to allow only AttributeError
                if type(e).__name__ == 'AttributeError':
                    loc_attribs=order_attribs
                    loc_flag=0
                else: raise    
            if self.level!=0:
                if -1 in self.loc_at_typs:
                    dummy= [not (self.loc_at_typs[i]==-1 and\
                                                      not any([loc_attribs[i]==m \
                                                    for m in ['C','T','X']])) for i in range(len(self.loc_at_typs))]
                    loc_attribs = [loc_attribs[i] for i in range(len(self.loc_at_typs)) \
                                   if not (self.loc_at_typs[i]==-1 and\
                                                      not any([loc_attribs[i]==m \
                                                    for m in ['C','T','X']]))]
    
            # ******************** Fetching Content ********************* # 
            self.cr_content(loc_attribs)
            ret_obj.p_header = self.p_header
            ret_obj.r_header = self.r_header
            ret_obj.c_header = self.c_header
            ret_obj.p_content = deepcopy(self.p_content)
            ret_obj.r_content = deepcopy(self.r_content)
            ret_obj.c_content = deepcopy(self.c_content)
            
        return(ret_obj)        

    # ******************************************************** #
    def gather_content(self):
#        if sa_list is None:
#            try:
#                sa_list = [['-'.join(s[:-1]) for s in self.sa_list]]
#                sa_list.append([s[-1] for s in self.sa_list])
#            except: pass
        
        if self.attribs!=[]:
            p_cont = self.p_content.copy()
            r_cont = self.r_content.copy()
            c_cont = self.c_content.copy()
            comp_ind = self.c_header.index('Component') 
            lin_ind = self.c_header.index('Line No')
            qty_ind = self.c_header.index('Usage Qty')
            try:
                qty = self.qty
                qty_out = qty
            except Exception as e: # Insert line to allow only AttributeError
                if type(e).__name__ == 'AttributeError':pass
                else: raise(e)
        else:
            p_cont,r_cont,c_cont=[],[],[]
            
        if self.child is not None:
            count=0
            for child in self.child:
#                if sa_list is None:
                out = child.gather_content()
                if len(out)==3:
                    p,r,c = out
                elif len(out)==4:
                    p,r,c,qty = out
                try:
                    qty_out = self.qty
                except Exception as e: # Insert line to allow only AttributeError
                    if type(e).__name__ == 'AttributeError':
                        qty_out = qty
                    else:
                         raise(e)
#                else: 
#                    p,r,c=child.gather_content(sa_list)
                if p_cont!=[]:
                    p_cont.extend(p)
                    r_cont.extend(r)
                    if c_cont[0][comp_ind]!='':
                        c_cont.insert(0+count,c_cont[0].copy())
                        if self.attribs!=[]:                    
                            for i in range((len(c_cont))):
                                if i!=0 and c_cont[i][0]==c_cont[i-1][0]:
                                    c_cont[i][lin_ind] = str(int(c_cont[i-1][lin_ind])+10)

                    c_cont[0+count][comp_ind] = c[0][0]
                    c_cont[0+count][qty_ind] = str(qty)
                    c_cont.extend(c)
                else:
                    p_cont,r_cont,c_cont=p,r,c
                count += 1
        if self.level!=0:
            try:
                return(p_cont,r_cont,c_cont,qty_out)
            except Exception as e: # Insert line to allow only AttributeError
                print(e)
                if type(e).__name__ == 'UnboundLocalError':
                    return(p_cont,r_cont,c_cont)
                else:
                    raise(e)
        else:
            return(p_cont,r_cont,c_cont)
    # ******************************************************** #
    def write_out_files(self,order,ret_op=0):
        #pth = '\\'.join(self.path.split('\\')[:-1])
        dir_name = '\\3G order dirs\\3G-'+'-'.join(order)
        if not os.path.exists(self.path+dir_name):
            os.makedirs(self.path+dir_name)
        p_cont,r_cont,c_cont= self.gather_content()
        self.header=self.p_header
        self.content=p_cont
        p_path=self.path+dir_name+'\\Stock_Items.csv'
        self.write_file(p_path,mute=1)
        
        self.header=self.r_header
        self.content=r_cont
        r_path=self.path+dir_name+'\\Routing.csv'
        self.write_file(r_path,mute=1)
        
        self.header=self.c_header
        self.content=c_cont
        c_path=self.path+dir_name+'\\Components.csv'
        self.write_file(c_path,mute=1)
        if ret_op==1:
            return(p_path,r_path,c_path)
        print('Writing Complete')