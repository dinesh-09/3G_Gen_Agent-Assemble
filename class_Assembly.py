# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 08:51:56 2018

@author: Demon King
"""
from class_product import component as product
import os
import traceback
from copy import deepcopy
from Gen_IDs import create_ID_dir
# ************************************************************************************** #

class translator():
    
   # ********************** Initialise ********************** #
    def __init__(self,dic,in_typ='',out_typ=''):
        self.in_typ = in_typ
        self.out_typ = out_typ
        self.dic=dic    
            
# ************************************************************************************** #
       
class assembly(product):

    # ********************** Initialise ********************** #
        
    def __init__(self,name='',level=-1):
        product.__init__(self)
        self.name=name
        self.level=level
        self.child=None
        self.prnt=None
        self.is_assm=0
        self.glob_attribs = []
        self.attr_excl_list = []
        self.id_dir=[]
    # ******************************************************** #
    def place_folder(self,fold):
        if fold.prnt is None:
            fold.prnt = self
        fold.glob_attribs = self.glob_attribs
        if self.child is None:
            self.child=[fold]
        else:
            self.child.append(fold)
    
    # ******************************************************** #
    def conv_obj(self): # Converts object to array
        #print("\t\t",self.name)
        out_arr=[]
        if self.child is not None:
            for child in self.child:
                out_arr.append(child.conv_obj())
            out_arr = [self.name,out_arr]
        else:
            out_arr = self.name
        
        return(out_arr)
                        
    # ******************************************************** #
    def cr_dict(self,ances_obj,infile): # Creates dictionary for converting global attributes to local attributes
        from operator import itemgetter
        if not all(['=' in line for line in infile]):
            raise Exception('The conversion expression needs =')
        # The 5-6 lines below are to ensure that the data is sorted by in_typ before logging into dictionary    
        splt_file = [line.split('=') for line in infile]
        typ_file = [[[ances_obj.convert_attr_to_code(ats)[0][0] for ats in a[0].split('+')],\
                     self.convert_attr_to_code(a[1])[0][0]] for a in splt_file]
        sort_ind = [ind for ind,_ in sorted(enumerate(typ_file),key=itemgetter(1))]
        typ_file = [typ_file[i] for i in sort_ind]
        splt_file = [splt_file[i] for i in sort_ind]
        dict_list = [{key:value} for key,value in splt_file]
        #typ2_file =[]
        #[typ2_file.append(typ) for typ in typ_file if typ not in typ2_file]
        self.tlator=[]
        dic = {}
        curr_typ=''
        for i in range(len(dict_list)):
            if typ_file[i] != curr_typ and curr_typ != '':
                self.tlator.append(translator(dic,curr_typ[0],curr_typ[1]))
                dic={}

            if splt_file[i][0] in dic:
                dic[splt_file[i][0]].append(splt_file[i][1])
            else: 
                dic[splt_file[i][0]]=splt_file[i][1]
                
            curr_typ=typ_file[i]
        self.tlator.append(translator(dic,curr_typ[0],curr_typ[1]))
         
        # IN CASE OF BUG IN OUT_TYP : Here I am assuming only one out_typ present for each in_typ 
#        for line_ind in range(len(splt_file)):
#            key,value = splt_file[line_ind]
#            o_t = typ_file[line_ind[1]]
#            if o_t != -1:
#                typ = typ_file[line_ind[1]]
#                if typ!=curr_typ and curr_typ!='':
#                    self.tlator.append(translator(dic,curr_typ,o_typ))
#                    dic={}
#                    
#                if key in dic:
#                    dic[key].append(value)
#                else: 
#                    dic[key]=[value]
#                o_typ=o_t
#                curr_typ=typ
            

    # ******************************************************** #
    def dict_to_list(self):
        loc_list=[[],[]]
        glob_list=[[],[]]
        from operator import itemgetter
        for tlator in self.tlator:
            for key in tlator.dic.keys():
                # Loc List creation, assuming, Assuming only one out_typ present per key
                if tlator.out_typ not in loc_list[0]: 
                    loc_list[0].append(tlator.out_typ)
                    loc_list[1].append([key])
                else: 
                    loc_list[1][loc_list[0].index(tlator.out_typ)].append(key)
                
                for ind in range(len(tlator.in_typ)):
                    if tlator.in_typ[ind] not in glob_list[0]:
                        glob_list[0].append(tlator.in_typ[ind])
                        glob_list[1].append([])
                    ins_ind = glob_list[0].index(tlator.in_typ[ind])
                
                    [glob_list[1][ins_ind].append(entry[ind]) \
                     for entry in tlator.dic[key] if entry[ind] not in glob_list[1][ins_ind]]
        glob_list = [list(n) for n in zip(*glob_list)]
        loc_list = [list(n) for n in zip(*loc_list)]
        glob_list = sorted(glob_list, key=itemgetter(0))
        loc_list = sorted(loc_list, key=itemgetter(0))
        return(glob_list,loc_list)

    # ******************************************************** #
    def conv_to_loc(self,attrib,ances=None): # Converts global attribute to local attribute
        from operator import itemgetter
        prev_typ=-1
        in_list = []
        out_list = []
        for tl in self.tlator:
            if prev_typ!=tl.in_typ:
                in_attrib = [attrib[i-1] for i in tl.in_typ]
                if '+'.join(in_attrib) in tl.dic.keys():
                # removing values present in in_attrib from attrib
                    [in_list.append(i-1) for i in tl.in_typ]
                    #attrib = [attrib[i] for i in range(len(attrib)) if i+1 not in tl.in_typ] 

                # Potential bug in the line below if sub-assembly name is present in attrib
                    out_list.append([tl.out_typ-1,tl.dic['+'.join(in_attrib)]]) 
                    prev_typ = tl.in_typ
        attrib = [attrib[i] for i in range(len(attrib)) if i not in in_list]
        out_list = sorted(out_list,key=itemgetter(0))
        attrib_typ = [self.convert_attr_to_code(a)[0][0] for a in attrib] # Converting to code for filtering
        if -1 in attrib_typ:            
            neg_list = [[ances.convert_attr_to_code(attrib[ind])[0][0]-1,attrib[ind]] for ind in range(len(attrib)) if attrib_typ[ind]==-1] #the index and value of locally absent attributes
            attrib = [attrib[ind] for ind in range(len(attrib)) if attrib_typ[ind]!=-1] #Filtering
            [attrib.insert(o[0],o[1]) for o in out_list] #Inserting local attributes, at the correct place
            # Ensuring the values are inserted in the correct place 
            for n in neg_list:
                glb_typ = [ances.convert_attr_to_code(a)[0][0] for a in attrib]
                llist=[ind for ind in range(len(glb_typ)) if glb_typ[ind]-1>n[0] and glb_typ[ind]!=-1] # Indices less than the insert loc
                if n[0]==0 or llist ==[]:
                    if glb_typ[-1]-1<n[0]:
                        attrib.append(n[1])
                    else:
                        attrib.insert(n[0],n[1])
                else:
                    attrib.insert(llist[0],n[1])
        else:
            [attrib.insert(o[0],o[1]) for o in out_list]
        return(attrib)
            
    # ******************************************************** #
    def back_prop(self):
        curr_fold=self
        while curr_fold.is_assm!=1:
            curr_fold=curr_fold.prnt
        if curr_fold.level>1: # No need to back propagate data if current level <=1   
            dummy = curr_fold.prnt
            while dummy.is_assm !=1:
                dummy = dummy.prnt
            for att_typ_ind in range(len(dummy.attrib_flags)):
                for j in range(len(dummy.attrib_flags[att_typ_ind])):
                    if dummy.attrib_flags[att_typ_ind][j]==0 and curr_fold.attrib_flags[att_typ_ind][j]==1:
                       dummy.attrib_flags[att_typ_ind][j]=1 
            if dummy.level !=1:
                dummy.back_prop()
        


    # ******************************************************** #                
    def read_id_dir(self):
        from copy import deepcopy       
        if not os.path.isfile(self.path+'\\ID_dir.csv'):
            print('IDs not found, generating IDs')
            if not os.path.isfile(self.path+'\\ID_Dir_input.csv'):
                raise Exception('Need the ID_Dir_input.csv file at',path,'to generate ID\'s')
            else:
                self.id_dir = create_ID_dir(self.path,ret_op=1)[1:]
        else: self.id_dir = self.transfer_csv(self.path+'\\ID_dir.csv')[1:]     
    # ******************************************************** #                
    def conv_flags(self):
        if self.is_assm==1 and self.level!=0:
            for i in range(len(self.attrib_flags)):
                for j in range(len(self.attrib_flags[i])):
                    if self.attrib_flags[i][j]==1:
                        self.attrib_flags[i][j] = self.glob_attribs[i][j]   
        if self.child is not None:
            for child in self.child:
                child.conv_flags()
        
    # ******************************************************** #                
    def gen_ids(self,attribs):
        import itertools
        from numpy import prod
        if self.var != '':
            var_ats = [[m for m in attribs[n]] for n in self.var_cds]
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


    # ******************************************************** #
    def create_comb(self,order_attribs):   # Creates all the possible combinations of the attributes excluding non-combs. 
        import itertools

        # ******** Creating all possible combinations ******** #
        if self.var != '':
            self.var_cds = [self.convert_attr_to_code(m)[0][0] for m in self.var.split('-')]
            attribs = [[order_attribs[ind-1]] if ind in self.var_cds else self.attribs[ind].copy()\
                       for ind in range(len(self.attribs))] # This ensures that attribs has only one particular variation of var
        else:
            attribs = self.attrib_comb
#        comb = itertools.product(*attribs)
#        attrib_comb=[]
#        for element in comb:
#            attrib_comb.append(list(element))
        self.attrib_comb= [list(element) for element in itertools.product(*attribs)]
            
        # ******** Converting non_combs to codes ******** #
        if self.non_combs != []:
            non_combs_code = self.convert_attr_to_code(self.non_combs)
            non_combs_code = [sorted(m) for m in non_combs_code]
    
            for l in range(len(self.non_combs)):
                self.attrib_comb = \
                list(itertools.filterfalse(lambda x: x if [x[y] \
                for y in non_combs_code[l]]== self.non_combs[l] else 0,self.attrib_comb))
        self.gen_ids(attribs)
                   
    # ********************* Get Attr Index ******************** #   

    def get_attr_index(self,attr,attr_list):
        import traceback
        try:
            attr_index=[x in [attr] for x in attr_list].index(True)    
        except ValueError:
            err_string = "Error in searching the attribute "+attr+\
                  " in the list: "+",".join(attr_list)
            print(err_string)
            raise #Exception(err_string)
            print(traceback.format_exc())
        return(attr_index)         

    # ******************************************************** #
    def select_id(self,attribs):

        iid,idesc=[list(n) for n in zip(*self.id_dir)]
        id_comp_file=[list(n) for n in zip(*[i.split('-') for i in idesc])]

        for i in id_comp_file:
            [i.insert(m,['ATTR_VALUE','AV'][m]) for m in range(2)]
        iid.insert(0,'Component_ID')
        iid.insert(1,'D')
        id_comp_file.append(iid)
#        add_on=[['Component_ID','V',''],['Sequence','S','10'],['QTY','Q-D','1'],['QTY','Q-V','1']]
        add_on=[['Sequence','S','10']]

        for entry in add_on:
            add_list = [entry[2] for n in range(len(id_comp_file[0])-2)]
            [add_list.insert(m,[entry[0],entry[1]][m]) for m in range(2)]
            id_comp_file.append(add_list)
        [i.insert(0,'') for i in id_comp_file]
        id_comp_file[0][0]='Var_Flag'
        id_comp_file[1][0]='0'
        id_comp_file = [list(n) for n in zip(*id_comp_file)]
        
        self.read_comp_infile(id_comp_file,file_flag=1)
        self.iid= [self.select_component2(attribs)]

    # ******************************************************** #
    def search_id(self,attribs):
        attrib_desc = attribs.copy()
        iid,idesc=[list(n) for n in zip(*self.id_dir)]
        id_comp_file=idesc[0].split('-')
        if len(id_comp_file) == len(attrib_desc)+1: 
            attrib_desc.insert(0,id_comp_file[0])
        attrib_desc='-'.join(attrib_desc)
        self.iid=[iid[idesc.index(attrib_desc)]]   

    # ******************************************************** #
    def calc_id(self,ord_list):
        import numpy as np
        
        attribs=self.attribs[1:].copy()
        tot_nos = [len(m) for m in attribs]
        prod_index = np.array([np.prod(tot_nos[a+1:]) for a in range(len(tot_nos)-1)])
        try:
            curr_index=[]
            curr_index = np.array([1+self.get_attr_index(ord_list[m],attribs[m]) for m in range(len(attribs))])
            iid = (np.sum(prod_index[:,np.newaxis]*\
                         ((curr_index[:-1]-1)[:,np.newaxis]))+curr_index[-1])
            max_iid = len(str(np.product(np.array([len(a) for a in ord_list]))))
            #var_indices = [m-1 if m>0 else m for m in self.var_indices]
            code ='{0:0'+str(max_iid)+'}'
            iid = code.format(iid)
            var = [self.convert_attr_to_code(v)[0][0] for v in self.var.split('-')]
            var='-'.join([ord_list[v-1] for v in var])            
            self.iid = [self.p_id+'-'+var+'-'+iid]
            #return("FHA-"+"-".join([attr_list[m] for m in var_indices])+"-"+iid)
        except Exception as e:
            print(e)        

        
    # ******************************************************** #
    def cr_content(self,attribs):  # Basically this function runs almost the old BOM Automator
        self.attrib_comb=[attribs]
        if self.level==0:
            self.calc_id(attribs)
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
            self.c_header=self.header        
            self.create_components_content(mute=1)
            self.c_content=deepcopy(self.content)
            
        
        except:
            print('Error found at',self.path,traceback.format_exc())
            raise
    # ******************************************************** #
    def map_assm(path): # path should belong to the folder where all standard files are stored
        
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

                    fold_obj = assembly(fold[0],0)
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
                    fold_obj = assembly(name_arr[-1],len(name_arr)) # New Object
                    if '(' in fold_obj.name: #
                        fold_obj.is_assm = 0
                        # Splitting to discard the folder category name
                        fold_obj.var_conv,name =  fold_obj.name.split('(')
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
    def fetch_content(self,order_attribs,prnt_level,prefix=None,assm=None): # Currently not able to handle options 
        from copy import deepcopy
        if prefix is None:
            if self.level==0:
                prefix='3G'
                assm=self
            elif self.is_assm==1:
                prefix=self.name

        self.p_id = prefix
        ret_obj = assembly(self.name,prnt_level+1)
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
        #  ************** Fetching any components from the current folder ************** #

        if self.attribs != []: # Stock,Routing,Components are present in the object

            # ***** Converting global attributes to local, if any, for selection ******* #
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
                    loc_attribs = [loc_attribs[i] for i in range(len(self.loc_at_typs)) if self.loc_at_typs[i]!=-1]


            # ******************** Reading the local product id ********************* #    
#            self.iid,self.attrib_comb=[list(n) for n in zip(*self.transfer_csv(self.path+'\\ID_dir.csv')[1:])]
#            self.attrib_comb=[a.split('-') for a in self.attrib_comb]
#            truth_arr = [all([a in loc_attribs for a in attrib[1:]]) for attrib in self.attrib_comb]
#            try:
#                curr_assm_id = ['-'.join([self.iid[truth_arr.index(True)]])]
#                c_list = self.select_component2(loc_attribs)
#                curr_assm_id.extend(c_list[0][1:])
#                comp_list= [curr_assm_id,c_list[1:]]
#            except Exception as e:
#                if type(e).__name__ == 'ValueError':
#                    raise Exception('Some order attributes are not found in the location', self.path)
#                else:
#                    raise(e)

            # ******************** Fetching Content ********************* # 
            self.cr_content(loc_attribs)
            ret_obj.p_header = self.p_header
            ret_obj.r_header = self.r_header
            ret_obj.c_header = self.c_header
            ret_obj.p_content = deepcopy(self.p_content)
            ret_obj.r_content = deepcopy(self.r_content)
            ret_obj.c_content = deepcopy(self.c_content)
            

        #  ***************** Fetching any components from the children ***************** #    
        if loc_flag==0:
            loc_attribs=order_attribs

        if self.child is not None:
            ret_obj.child=[]
            for child in self.child:
                if child.is_assm == 1: #Selecting the Sub-A
                    if child.attr_excl_list!=[]:
                        if any([loc_attribs[e[0]-1] in e[1] for e in child.attr_excl_list]):
                            continue
                    # Inserting the correct objects
                    ret_obj.place_folder(child.fetch_content(loc_attribs,ret_obj.level,assm=assm))
                elif any([a==child.name for a in loc_attribs]):
                    ret_obj.place_folder(child.fetch_content(loc_attribs,ret_obj.level,prefix=self.p_id,assm=assm))
                #if comps!=[]:    
                    #if len(comp_list)>1 and type(comps[0][0]) is str: # Data coming from a sub-assembly
                        #comp_list[1].insert(0,comps)
                    #else: # Will this ever happen ? 
                        #comp_list= comps
#        return(comp_list)
        return(ret_obj)        

    # ******************************************************** #
    def gather_content(self):
        if self.attribs!=[]:
            p_cont = self.p_content.copy()
            r_cont = self.r_content.copy()
            c_cont = self.c_content.copy()
            comp_ind = self.c_header.index('Component') 
            lin_ind = self.c_header.index('Line No')
        else:
            p_cont,r_cont,c_cont=[],[],[]
        if self.child is not None:
            for child in self.child:
                p,r,c=child.gather_content()
                if p_cont!=[]:
                    p_cont.extend(p)
                    r_cont.extend(r)
                    if c_cont[0][comp_ind]!='':
                        c_cont.insert(0,c_cont[0].copy())
                        if self.attribs!=[]:                    
                            for i in range((len(c_cont))):
                                if i!=0 and c_cont[i][0]==c_cont[i-1][0]:
                                    c_cont[i][lin_ind] = str(int(c_cont[i-1][lin_ind])+10)
                    c_cont[0][comp_ind] = c[0][0]
                    c_cont.extend(c)
                else:
                    p_cont,r_cont,c_cont=p,r,c

        return(p_cont,r_cont,c_cont)
            
    # ******************************************************** #
    def write_out_files(self,order):
        #pth = '\\'.join(self.path.split('\\')[:-1])
        dir_name = '\\3G order dirs\\3G-'+'-'.join(order)
        if not os.path.exists(self.path+dir_name):
            os.makedirs(self.path+dir_name)
        p_cont,r_cont,c_cont= self.gather_content()
        self.header=self.p_header
        self.content=p_cont
        self.write_file(self.path+dir_name+'\\Stock_Items.csv',mute=1)
        
        self.header=self.r_header
        self.content=r_cont
        self.write_file(self.path+dir_name+'\\Routing.csv',mute=1)
        
        self.header=self.c_header
        self.content=c_cont
        self.write_file(self.path+dir_name+'\\Components.csv',mute=1)
        
        print('Writing Complete')