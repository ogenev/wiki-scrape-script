import numpy as np
import pandas as pd
import csv
import requests

# Wikipedia API has 500 items limit per query, so we are going to make continuing queries and iterate over query results.
def query(request):
     request['action'] = 'query'
     request['format'] = 'json'
     request['list'] = "categorymembers"
     request['cmtitle'] = "Category:21st-century American singers" # name of the category we want to scrape
     request['cmlimit'] = 500
     lastContinue = {}
     while True:
        # Clone original request
         req = request.copy()
        # Modify it with the values returned in the 'continue' section of the last result.
         req.update(lastContinue)
        # Call API
         result = requests.get('https://en.wikipedia.org/w/api.php', params=req).json()
         if 'error' in result:
             raise result['error']
         if 'warnings' in result:
             print(result['warnings'])
         if 'query' in result:
             yield result['query']
         if 'continue' not in result:
             break
         lastContinue = result['continue']

page_ids = [] # creating a list to store all pageids from the category

for result in query({'generator': 'links'}): # iterating over query results
    for data in result['categorymembers']:
        page_ids.append(data['pageid'])

with open('us_singers.csv', 'a') as newFile: # appending to blank csv file
    counter = 0
    newFileWriter = csv.writer(newFile)
    none_born = np.array(['None'])

    for ids in page_ids:
        page = 'http://en.wikipedia.org/?curid=' + str(ids) # url for the page to scrape
        try:
            infoboxes = pd.read_html(page, index_col=0, attrs={"class":"infobox"})[0] # reading the table with pandas
            name = infoboxes.index.values[0] # name of the page/person
            if 'Born' in infoboxes.index.values:
                born = infoboxes.loc['Born'] # collecting data from the 'Born' row
            else:
                born = pd.Series(none_born)
            if 'Spouse(s)' in infoboxes.index.values:
                spouses = infoboxes.loc['Spouse(s)']  # collecting data from the 'Spouse(s)' row

                # Writing the data to CSV file, for actors categories we can add the gender, because we have separate categories
                # for males and females. We can add too 'Political party' for politicians.
                newFileWriter.writerow([name, born.iloc[0], spouses.iloc[0]])  
                counter +=1
                print('{} profiles processed!'.format(counter))
        except Exception as e:
            print("type error: " + str(e))
