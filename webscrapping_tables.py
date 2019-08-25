'''
Web Scrapping: Extract table

Powell Chu
August 2019

- written in Python3
- this program creates two csv file, extracting information
on Lakes water mean:
'dataset_1_lakes_monthly.csv' - monthly across all years
'dataset_2_lakes_all-time.csv' - all time

URL not specified due to privacy

'''



import requests
import lxml.html as lh
import pandas as pd
import numpy as np

def extract_table(url,xpath_all,contains_header):
    
    #Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)

    col_all=[]
    nrows=[] # number of rows for each table
    
    for xpath in xpath_all:
        #Parse data that are stored between <tr>..</tr> of HTML
        tr_elements = doc.xpath(xpath)

        #Check the number of columns of the first 12 rows
        print("Number of columns of the table:")
        print([len(T) for T in tr_elements[:12]])

        #Create empty list
        #tables that store a header (if there's one) and data
        #assuming all tables have the same header
        col=[]  

        ## Getting header
        i=0
        #For each row, store each first element (header)
        #and an empty list
        print("Table Header:")
        for t in tr_elements[0]:
            if contains_header==True:
                name=t.text_content()
            else:
                name=contains_header[i]
            i+=1
            print('%d:"%s"'%(i,name))
            col.append((name,[]))

        #print(col)


        ## Getting data
        if contains_header==True:
            start_ind = 1
        else:
            start_ind = 0

        nrows_current = 0
        for j in range(start_ind,len(tr_elements)):
            #T is our j'th row
            T=tr_elements[j]

            #If row matches with the header of table 1, 
            #we skip that row
            if (contains_header==True and 
                    T.text_content() == tr_elements[0].text_content()):
                print("contains_header:")
                print(contains_header)
                nrows.append(nrows_current)
                nrows_current=0
                continue

            nrows_current+=1


            #if reaching the last row of the table
            if j == len(tr_elements)-1 :
                nrows.append(nrows_current)


            #i is the index of our column
            i=0
            
            #Iterate through each element of the row
            for t in T.iterchildren():
                data=t.text_content()
                #print(data)
                #input()


                #Convert any numerical value to numbers (int or 
                #float)
                try:
                    data=int(data)
                except:
                    try:
                        data=float(data)
                    except:
                        pass
                #Append the data to the empty list of the 
                #i'th column
                col[i][1].append(data)
                #Increment i for the next column
                i+=1

        #Check the length of the columns
        print([len(C) for (title,C) in col])

        col_all.append(col)

    return col_all,nrows


## Create Dataframe
def create_dataframe(table,num_table):

    df_all = pd.DataFrame()

    for t in range(0,num_table):
        Dict={title:column for (title,column) in table[t]}

        df=pd.DataFrame(Dict)

        df_all=df_all.append(df,ignore_index=True)

    return df_all


## Create new column to label each section of table
def create_new_col(df,new_col_header,col_value,table_nrows):
    #df_test = df
    for i in range(0,len(table_nrows)):
        from_ind = sum(table_nrows[:i])
        to_ind = sum(table_nrows[:i+1])-1

        #print(from_ind)
        #print(to_ind)
        #print(col_value[i])
        #print(df_test.loc[from_ind:to_ind,'Year'])
        #input()

        df.loc[from_ind:to_ind,'Lake_Name'] = col_value[i]




##MAIN

url='BLANK'         #url not shown...need to specify in order to execute the code

xpath1_1='//table[@class="span-8"]/tr'
xpath1_2='//table[@title="Montreal Harbour monthly mean water levels in metres referred to IGLD 1985"]/tr'

print(xpath1_2)
input()
xpath2='//table[@title="All-Time"]/tr'


#Table1
contains_header=True
[table1,table1_nrows] = extract_table(url,[xpath1_1,xpath1_2],
    contains_header)

#table[table 0-1][header for each column][each row of data]


#Table2
header_list=[title for (title,column) in table1[0]]
[table2,table2_nrows] = extract_table(url,[xpath2],header_list)


df_1 = create_dataframe(table1,len([xpath1_1,xpath1_2]))
df_2 = create_dataframe(table2,len([xpath2]))


new_col_header = 'Lake_Name'
lake_names=['Lake Superior','Lake Michigan-Huron',
    'Lake St. Clair','Lake Erie','Lake Ontario','Montreal Harbour']


#Create new column to specify which lake
create_new_col(df_1,new_col_header,lake_names,table1_nrows)
table2_nrows = [3,3,3,3,3,3]
create_new_col(df_2,new_col_header,lake_names,table2_nrows)

#Reorder columns
header_list.insert(0,new_col_header)
df_1 = df_1[header_list]
df_2 = df_2[header_list]


## Drop unnecessary columns in each dataset

#df_1
df_1.drop(["MaximumMonthly","MinimumMonthly","Range","YearlyAverage"],
    axis=1,inplace=True)

#df_2 : change name of column from "Year" to "All-Time_level"
df_2.rename(columns = {'Year':'All-Time_level'}, inplace = True)

##Save files

df_1.to_csv('dataset_1_lakes_monthly.csv')
df_2.to_csv('dataset_2_lakes_all-time.csv')
