#!/usr/bin/env python

import pandas as pd
import numpy as np
from datetime import date, timedelta
import re
import sys
from os.path import abspath


if len(sys.argv)!=3:
    print('''Usage: /path/to/gen_data.py dict.csv fake_out.csv''')
    exit(0)


start_date= date(2021,5,13)

# dfd is data dictionary
dfd= pd.read_csv(abspath(sys.argv[1]))

# df is fake data, initialize it
df= pd.DataFrame(columns= dfd['Variable / Field Name'])

# append 100 empty rows
N=10
# assign a three digit random ID to each row i.e. research subject
df.chric_subject_id= np.random.randint(100,1000,N)

for var in dfd.iterrows():    
    
    var= var[1]
    
    # dfs is each row of df i.e. fake data of each subject
    all_cond_values= []

    # TODO below branching logic block could be placed here

    for dfs in df.iterrows():
        
        cond_value=''
        
        given_cond= var['Choices, Calculations, OR Slider Labels']
        if given_cond is not np.nan:
            if var['Field Type']=='calc':
                
                if 'if(' in given_cond:
                    
                    # parse calculation
                    tmp_plus=[]
                    for str_plus in given_cond.split('+'):

                        tmp_and=[]
                        for str_and in str_plus.split('and'):
                            
                            tmp_or=[]
                            for cond in str_and.split('or'):
                                # for all
                                cond= cond.replace(']','')
                                cond= cond.replace('[', 'dfs[1].')
                                cond= cond.replace('=','==')
                                cond= cond.replace('if(',' ')
                                # for round() only
                                cond= cond.replace('round(','')
                                cond= cond.replace(',1))',')')
                                # for all
                                cond= cond.replace(')','')
                                
                                # evaluate condition and obtain result
                                # print(cond)
                                try:
                                    c,t,f=cond.split(',')
                                except:
                                    print(cond)
                                
                                if eval(c):
                                    value= t
                                else:
                                    value= f
                                    
                                tmp_or.append(value)
                                

                            # rejoin the ors
                            cond_or_new= ' or '.join(tmp_or)
                            tmp_and.append(cond_or_new)
                        
                        # rejoin the ands
                        cond_and_new= ' and '.join(tmp_and)
                        tmp_plus.append(cond_and_new)

                    # rejoin the pluses
                    cond_new= ' + '.join(tmp_plus)
                    
                    
                    # print(cond)
                    cond_value= eval(cond_new)
                    # print(cond_new, '=', cond_value)
                    
                elif 'sum(' in given_cond:
                
                    given_cond= given_cond.replace(']','')
                    given_cond= given_cond.replace('[','dfs[1].')
                    given_cond= given_cond.replace('sum(','sum([')
                    given_cond+= ']'
                    given_cond= given_cond.replace(')]','])')
                    given_cond= given_cond.lower()
                    
                    cond_value= eval(given_cond)
                
                # this deals with arithmatic addition
                else:
                
                    given_cond= given_cond.replace(']','')
                    given_cond= given_cond.replace('[','dfs[1].')
                    given_cond= given_cond.replace('=','==')
                    given_cond= given_cond.lower()
                    
                    cond_value= eval(given_cond)
                
            elif var['Field Type'] in ['radio', 'checkbox', 'dropdown']:
                values= []
                for val_lab in given_cond.split(' | '):
                    try:
                        if 'chrrecruit_self_other'==var['Variable / Field Name']:
                            print(val_lab, var['Variable / Field Name'])
                            
                        values.append(int(val_lab.split(', ')[0]))
                    except:
                        # float
                        try:
                            values.append(float(val_lab.split(', ')[0]))
                        # FIX in the form
                        # NA, Not Sure --> -99, Not Sure
                        except:
                            values.append('NA')
                
                # randomize according to multinomial distribution
                L= len(values)
                prob= [1/L]*L
                cond_value= values[np.where(np.random.multinomial(1,prob))[0][0]]

                
        else:
            if var['Field Type']=='text':
                
                text_type= var['Text Validation Type OR Show Slider Number']
                
                if  text_type=='number' or text_type=='integer':
                        
                    if var['Text Validation Min'] is np.nan:
                        num_min= 1
                    else:    
                        num_min= float(var['Text Validation Min'])
                        
                    if var['Text Validation Max'] is np.nan:
                        num_max= 100
                    else:    
                        num_max= float(var['Text Validation Max'])
                        
                    cond_value= np.random.randint(num_min, num_max)
                    
                    if var['Field Note'] is not np.nan and 'x 10^' in var['Field Note']:
                        
                        tmp= var['Field Note'].replace('/L','')
                        exp= tmp.split('10^')[-1]
                        cond_value= cond_value * 10**int(exp)
                        
                elif text_type=='time':
                    
                    if var['Text Validation Min'] is np.nan:
                        num_min= 0
                    else:
                        num_min= int(var['Text Validation Min'].split(':')[0])
                        
                    if var['Text Validation Max'] is np.nan:
                        num_max= 24
                    else:
                        num_max= int(var['Text Validation Max'].split(':')[0])
                    
                    cond_value= f'{np.random.randint(num_min, num_max)}:00'
                    
                    
                elif text_type=='date_ymd':
                    if var['Variable / Field Name']=='chric_consent_date':
                        # recruitment within the next 3 months
                        cond_value= start_date+ timedelta(days=np.random.randint(1,90))
                        chrcrit_date= cond_value
                    
                    else:
                        # dates in a column must be after chrcrit_date
                        # and should be within 5 days of chrcrit_date
                        cond_value= chrcrit_date+ timedelta(days=np.random.randint(0,5))
                    
                    cond_value= cond_value.strftime('%Y-%m-%d')
                
                elif text_type=='datetime_ymd':
                    # dates in a column must be after chrcrit_date
                    # and should be within 5 days of chrcrit_date
                    cond_value= chrcrit_date+ timedelta(days=np.random.randint(0,5), 
                                                        hours=np.random.randint(0,24))
                    
                    cond_value= cond_value.strftime('%Y-%m-%d %H:%M')

            elif var['Field Type']=='yesno':
                cond_value= round(np.random.rand())
                
                
        # print(cond_value)
        all_cond_values.append(cond_value)
    
    try:
        df[var['Variable / Field Name']]= all_cond_values
    except:
        print(all_cond_values)
    

df.to_csv(abspath(sys.argv[2]), index= False)

# TODO keeping this block separate from the above to have more control on debugging
# apply branching logic
for var in dfd.iterrows():

    var= var[1]

    # dfs is each row of df i.e. fake data of each subject
    all_cond_values= []

    for dfs in df.iterrows():
        
        cond_value= dfs[1][var['Variable / Field Name']]

        # check branching logic
        logic= var['Branching Logic (Show field only if...)']


        if logic is not np.nan:


            logic= logic.lower()
            logic= logic.replace(']','')
            logic= logic.replace('[','dfs[1].')
            logic= logic.replace('=','==')
            logic= logic.replace('>==','>=')
            logic= logic.replace('<==','<=')
            logic= logic.replace('\n',' ')
            logic= logic.replace("<>''",' is not np.nan')
            logic= logic.replace('<>', '!=')
            # convert the right side of logical expression to int
            logic= logic.replace("'",'')
            

            # notorious checkbox condition
            # e.g. dfs[1].health_skincond(99) == '1'
            is_checkbox= False
            paren_elm= re.search('\((.+?)\)', logic)
            if paren_elm:
                # at most two chars inside () for checkboxes
                if len(paren_elm.group(1))<3:
                    is_checkbox= True
                
            if is_checkbox:
                # obtain checked status
                checked= logic.split('==')[-1].strip()
                if checked:
                    # obtain checked value
                    # print(var['Variable / Field Name'])
                    checked_value= int(re.search('\((.+?)\)', logic).group(1))
                    # eliminate parenthetical element
                    logic= re.sub('\((.+?)\)', '', logic)
                    # reform logic with checked_value
                    logic= logic.split('==')[0]+ f' == {checked_value}'

            try:
                # print(logic)
                logic = eval(logic)
                if not logic:
                    cond_value=''

            except TypeError:
                # TypeError means dfs[1].chrfigs_depdxcalc is np.nan
                cond_value= ''


        all_cond_values.append(cond_value)

    df[var['Variable / Field Name']]= all_cond_values

df.to_csv(abspath(sys.argv[2]), index= False)
