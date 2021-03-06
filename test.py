import pandas as pd
import re

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
#
filename = 'PoynterCovid19Database_Reference_Article.csv'
fields = ['docID', 'content', 'accuracy', 'date', 'region', 'explanation', 'reference_url', 'reference_html', 'reference_text']
df = pd.read_csv(filename, usecols = fields)
# for index, row in df.iterrows():
#     print(row['docID'], row['content'])
print(df[df['docID']==3890]['content'].item())

# for doc in df.iloc[0]['content']:
#     print(doc)
# print(df.iloc[8404]['content'])

# csv_input = pd.read_csv(filename)
# csv_input.to_csv('output.csv', index=True, index_label='docID')

# df = pd.read_csv('queries_toy.csv', encoding='latin1')
# for index, row in df.iterrows():
#     print(row)

# query_ranked_file = open("queries_toy.txt", "r")
# query_ranked_str = query_ranked_file.read()
# query_ranked_list = re.split(r'\n', query_ranked_str)
# print(query_ranked_list)