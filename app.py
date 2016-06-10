# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:54:03 2016

@author: waffleboy
"""
from flask import Flask, render_template
from pandas.io.data import DataReader
from datetime import datetime
from datetime import timedelta
import pandas as pd
import pickle,json
from pandas_highcharts.core import serialize
from collections import OrderedDict

app = Flask(__name__) #initialize app

# Main function - Displays the data from masterDic, which contains all the information
# to make the dashboard.
@app.route("/")
def main():
    masterDic = loadData(years=5)
    return render_template('main.html',masterDic=masterDic)

# generates the master dictionary that contains all information for text and graph
# Input: <int> years: number of years worth of data to show
# Output: <dictionary> masterDic: dictionary of dictionaries. Example:
#   {'chart0': {'textdata': {'sbux': {'Ask':3,'Bid':4,..}} ,'content':{<highcharts constructor>}}}
def loadData(years):
    df = pd.read_csv('input.csv')
    companySym = list(df['stockname'])
    query,additionalOptions = getQuery(companySym) #generate link to query from, column names to map
    queryDF = pd.read_csv(query,header=None).fillna('NA') #actual query
    columnNames = getColumnNames(additionalOptions) 
    queryDF.columns = columnNames #set columm names to actual names of options
    col = queryDF.set_index('Symbol').T.to_dict() #make dictionary of key: symbol, value: everything in the row
    masterDic = populateMasterDic(df,col,years,OrderedDict()) #populate an orderedDict with data
    return masterDic

# Used by loadData(), fills the ordered dict with information
# Input:
# 1. <pandas dataframe> df: input.csv
# 2. <dictionary> col: dictionary containing all text data for every stock
# 3. <int> years: number of years worth of data to show
# 4. <OrderedDict> masterDic: an orderedDict to populate data with
# Output:
# 1. <OrderedDict> masterDic: masterdic populated with information
def populateMasterDic(df,col,years,masterDic):
    for i in df.index:
        name=df['stockname'][i]
        boughtprice = df['boughtprice'][i]
        data = DataReader(name,'yahoo', datetime.now()-timedelta(days=365*years), datetime.now())
        data = data[['Adj Close']]
        #make 21 day moving average
        data['21DayAvg'] = data['Adj Close'].rolling(21).mean().fillna(0)
        #make 100 day average
        data['100DayAvg'] = data['Adj Close'].rolling(100).mean().fillna(0)
        if not pd.isnull(boughtprice):
            bought = [boughtprice]*len(data.index)
            data = pd.DataFrame(data)
            data['bought'] = bought
        else:
            data = pd.DataFrame(data)
        content = serialize(data,render_to='chart'+str(i), title=name.upper()+' Stock',output_type='json')
        content = changeChartOptions(content)
        masterDic['chart'+str(i)] = {'textdata':col[name],'content':content}
    return masterDic
    
# This function adds additional options into the HighCharts dictionary
# Input: <json> content: json that will be passed to highcharts
# Output: <json> content: modified json to be passed to highcharts
def changeChartOptions(content):
    content = json.loads(content)
    # add a range selector
    content['rangeSelector'] = {'buttons':[{'type':'minute','count':24*60,
    'text':'24HR'},{'type':'week','count':1,'text':'1W'},{'type':'month','count':1,
    'text':'1M'},{'type':'month','count':3,'text':'3M'},{'type':'year','count':1,
    'text':'1Y'},{'type':'all','text':'ALL'}]}
    # disable credits
    content['credits']={'enabled':False}
    # add y axis title
    content['yAxis'] = {'title':{'text':'$','rotation':0}}
    content = json.dumps(content)
    return content

# Generates the final link to query yahoo finance on, and the list of additional
# options specified. See See http://www.jarloo.com/yahoo_finance/ for options
# Input: 
# 1. <list> companySym: list of strings of company stock symbols.
# Output: 
# 1. <string> finalQuery: string to query yahoo API
# 2. <list> additionalOptions: The list of additional options to specify to the link
def getQuery(companySym):
    """
    Current options specified are: 
    
    symbol / ask / bid / dividend yield / div per share / div pay date / 
    earnings per share / EPS estimate curr year / EPS est next year / EPS est next quarter
    EBITDA / p/e ratio / p/b ratio / peg ratio/ short ratio
    """
    additionalOptions = ['s','a','b','y','d','r1','e','e7','e8','e9','j4','r','p6','r5','s7']
    base = 'http://finance.yahoo.com/d/quotes.csv?s='
    companySymJoined = '+'.join(companySym)
    base = base+companySymJoined+'&f='
    finalQuery = base +  ''.join(additionalOptions)
    return finalQuery,additionalOptions

# Generates column names for the pandas column, taken from nameMatch.pkl
# Input: <List> additionalOptions: the list of additional options
# Output: <List> columnNames: a list of the full names of the options
def getColumnNames(additionalOptions):
    with open('nameMatch.pkl', 'rb') as handle:
        referenceDic = pickle.load(handle)
    columnNames = [referenceDic[x] for x in additionalOptions]
    return columnNames
    
if __name__ == "__main__":
	app.run(port=5000,debug=True)