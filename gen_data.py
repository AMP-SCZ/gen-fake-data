#!/usr/bin/env python

import pandas as pd
import numpy as np
from datetime import date, timedelta
import re
import sys
from os.path import abspath
from conversion import read_cases
import argparse


def sanity_check(fields):
    if event_name=='baseline_arm_1':
        print('\nSanity check:\n')
        for v in fields:
            print(v)
            print(df[v])
            print('')


parser = argparse.ArgumentParser(description='Fake data generator for REDCap forms')

parser.add_argument('--dict', help='Data dictionary')
parser.add_argument('--template', help='Import template')
parser.add_argument('--map', help='Instrument event map')
parser.add_argument('--arm', type=int, help='CHR(1), HC(2)', choices=[1,2])
parser.add_argument('--outPrefix', help="Fake data CSVs are saved as {outPrefix}.{redcap_event_name}.csv")
parser.add_argument('--caselist', help='Text file containing subject IDs')

args= parser.parse_args()

cases= read_cases(abspath(args.caselist))
N= len(cases)

start_date= date(2021,5,13)

# dfd is data dictionary
dfd= pd.read_csv(abspath(args.dict))

# df is fake data, initialize it
# df= pd.DataFrame(columns= dfd['Variable / Field Name'])
template_cols= pd.read_csv(args.template).columns

# drop 'Unnamed: 2345' last column
if 'Unnamed' in template_cols[-1]:
    template_cols= template_cols.drop(template_cols[-1])
# df= pd.DataFrame(columns=template_cols)

outPrefix= abspath(args.outPrefix)


# dfm is instrument-event mapping
dfm= pd.read_csv(abspath(args.map))

serial=0
for event_name in dfm['unique_event_name'].agg('unique'):
    
    if not event_name.endswith(f'arm_{args.arm}'):
        continue
    
    df= pd.DataFrame(columns=template_cols)
    df.chric_subject_id= cases
    
    event_forms= dfm.groupby('unique_event_name').get_group(event_name).form.values
    # event_forms=['informed_consent','inclusionexclusion_criteria_review_51ae86','guid_form',
    #   'schizotypal_personality_scid5_pd','sofas','recruitment_source']
    
    outfile= f'{outPrefix}_{event_name}.csv'
    
    for var in dfd.iterrows():
        
        var= var[1]
        
        if var['Variable / Field Name']=='chric_subject_id':
            continue
        
        # TODO delete this if block
        if var['Form Name'] not in event_forms:
            continue
        
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
                    
                    # this deals with arithmetic addition
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
                            values.append(float(val_lab.split(', ')[0]))
                            
                    
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
                        
                    
                    elif text_type=='date_ymd' or text_type=='datetime_ymd':
                        if var['Variable / Field Name']=='chric_consent_date':
                            # recruitment within the next 3 months
                            cond_value= start_date+ timedelta(days=np.random.randint(1,90))
                            chrcrit_date= cond_value
                        
                        else:
                            # dates in a column must be after chrcrit_date
                            # and should be within 5 days of chrcrit_date
                            cond_value= chrcrit_date+ timedelta(days=np.random.randint(0,5))
                        
                        if text_type=='date_ymd':
                            cond_value= cond_value.strftime('%Y-%m-%d')
                        else:
                            cond_value= f'{cond_value} {np.random.randint(0,24)}:00'
                            
                    
                elif var['Field Type']=='yesno':
                    cond_value= round(np.random.rand())
                    
                    
            # print(cond_value)
            all_cond_values.append(cond_value)
        
        
        df[var['Variable / Field Name']]= all_cond_values
        
    
    # populate form status
    '''
    dropdown
    ''  Incomplete (no data saved)
    0	Incomplete
    1	Unverified
    2	Complete
    '''
    L=4
    prob= [1/L]*L
    values=['',0,1,2]
    for form in event_forms:
        
        # randomize according to multinomial distribution
        
        cond_value= []
        for i in range(N):
            cond_value.append(values[np.where(np.random.multinomial(1,prob))[0][0]])
        
        df[f'{form}_complete']= cond_value
    
    
    df.redcap_event_name= [event_name]*N


    sanity_check(['chrfigs_depdxcalc','chrchs_bmi','chrchs_bedtime'])


    # df.to_csv(outfile, index= False)

    # exit(0)

    # TODO keeping this block separate from the above to have more control on debugging
    # apply branching logic
    for var in dfd.iterrows():

        var= var[1]

        # dfs is each row of df i.e. fake data of each subject
        all_cond_values= []

        for dfs in df.iterrows():
            
            if var['Field Type']=='calc':
                all_cond_values.append('')
                continue
            
            cond_value= dfs[1][var['Variable / Field Name']]

            # check branching logic
            logic= var['Branching Logic (Show field only if...)']


            if (logic is not np.nan) and ('datediff' not in logic) and (var['Field Type']!='descriptive'):

                logic= logic.lower()
                logic= logic.replace(']','')
                logic= logic.replace('[','dfs[1].')

                # consider two null comparisons--w/o space (= '') and w/ space (<>'')
                logic = logic.replace("= ''", ' is np.nan')
                logic = logic.replace("=''", ' is np.nan')
                logic= logic.replace('=','==')
                logic= logic.replace('>==','>=')
                logic= logic.replace('<==','<=')
                logic= logic.replace('\n',' ')

                # consider two null comparisons--w/o space (<>'') and w/ space (<> '')
                logic= logic.replace("<>''",' is not np.nan')
                logic= logic.replace("<> ''", ' is not np.nan')
                logic= logic.replace('<>', '!=')

                # convert the right side of logical expression to int
                logic= logic.replace("'",'')

                # remove leading zeros from branching logic of medlist_dosage_mg_01 et al
                logic= logic.replace('046','46')
                logic= logic.replace('048','48')

                # notorious checkbox condition
                # e.g. dfs[1].health_skincond(99) == '1'
                # the search fails if there are both parenthetical logic and checkbox item
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


                # print(var['Variable / Field Name'])

                try:
                    # print(logic)
                    logic = eval(logic)
                    if not logic:
                        cond_value=''

                except TypeError:
                    # TypeError means dfs[1].chrfigs_depdxcalc is np.nan
                    cond_value = ''

                    # original logic
                    # print(var['Branching Logic (Show field only if...)'])

                    # modified logic
                    print(logic)

                    print('')



            all_cond_values.append(cond_value)

        df[var['Variable / Field Name']]= all_cond_values
        
        
    df.to_csv(outfile, index= False)
    
    
    # debug break
    serial+=1
    if serial==3:
        pass
        # break

    
    sanity_check(['chrfigs_mother_info', 'chrfigs_mother_age'])



