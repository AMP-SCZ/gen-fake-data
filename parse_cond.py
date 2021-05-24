import pandas as pd
import numpy as np


# read file
df= pd.read_csv('AMPSCZFormRepository_DataDictionary_2021-05-14.csv')
df1= df.filter(items=['Field Type','Field Label', ...
    'Choices, Calculations, OR Slider Labels','Branching Logic (Show field only if...)'])

# filter necessary columns    
for i,item in df1['Choices, Calculations, OR Slider Labels'].iteritems():
    if item is np.nan:
        continue
    try:
        for val_exp in item.split(' | '):
            val= val_exp.split(', ')[0]
            print(val)
    except:
        print('Row',i, item)
        

# parse branching logics
for logic in df1['Branching Logic (Show field only if...)']:
    if logic is np.nan:
        continue

    logic= logic.lower()
    logic= logic.replace('[','')
    logic= logic.replace(']','')
    logic= logic.replace('=','==')
    logic= logic.replace('>==','>=')
    logic= logic.replace('<==','<=')
    logic= logic.replace("<>''",'is np.nan')
    
    eval(logic)

for cond in str1.split('+'):
    cond= cond.replace('[','')
    cond= cond.replace(']','')
    cond= cond.replace('=','==')
    c,t,f=cond.split(',')
    print(f'{c})',t,f.replace(')',''))
  

for cond in str1.split('+'):
    cond= cond.replace('if([','')
    cond= cond.replace(']','')
    cond= cond.replace(')','')
    cond= cond.replace('=','==')
    c,t,f=cond.split(',')
    print(c, t, f)
    
    
    tmp_plus=[]


# dfd is data dictionary
dfd= pd.read_csv('')

# df is fake data, initialize it
df= pd.DataFrame(columns= dfd['Variable / Field Name'])

# append 100 empty rows here
df.record_id= np.random.randint(100,1000, 100)

for var in dfd.iterrows():
    
    given_cond= var['Choices, Calculations, OR Slider Labels']
    
    # dfs is each row of df i.e. fake data of each subject
    for dfs in df.iterrows():
        
        # assign a three digit random ID
        # dfs.record_id= np.random.randint(100,1000)
        
        if var['Field Type']=='calc':
            
            given_cond= given_cond.replace('[','dfs.')
            given_cond= given_cond.replace(']','')
            given_cond= given_cond.replace('=','==')
            given_cond= given_cond.lower()

            # parse calculation    
            for str_plus in given_cond.split('+'):

                tmp_and=[]
                for str_and in str_plus.split('and'):
                    
                    tmp_or=[]
                    for cond in str_and.split('or'):
                        cond= cond.replace('(','')
                        cond= cond.replace(')','')
                        cond= cond.replace(' ','')
                        
                        # evaluate condition and obtain result
                        c,t,f=cond.split(',')
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
            
            cond_value= eval(cond_new)
            
        elif var['Field Type'] in ['radio', 'checkbox', 'dropdown']:
            values= [int(val_lab.split(', ')[0]) for val_lab in given_cond.split(' | ')]
            
            # randomize according to multinomial distribution
            L= len(values)
            prob= [1/L]*L
            cond_value= values[np.where(np.random.multinomial(1,prob))[0][0]]
        
        elif var['Field Type']=='yesno':
            cond_value= '1' if round(np.random.rand()) else '0'
        
        
        print(cond_value)
        
        # ENH randomization
        dfs.var['Variable / Field Name']= cond_value


