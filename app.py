# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:54:03 2016

@author: waffleboy
"""
#TODO:
# chart
# highstock
# real time
# colum nnames

from flask import Flask, render_template, url_for, send_from_directory,Blueprint
from flask import make_response, request, current_app  
from functools import update_wrapper
from pandas.io.data import DataReader
from datetime import datetime
from datetime import timedelta
import chartkick
import pandas as pd
import pickle,json
from pandas_highcharts.core import serialize

app = Flask(__name__)

ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

@app.route("/")
def main():
    masterDic = loadData(years=5)
    return render_template('main.html',masterDic=masterDic)

# of form name/boughtprice
def loadData(years):
    df = pd.read_csv('input.csv')
    companyNames = list(df['stockname'])
    query,additionalOptions = getQuery(companyNames)
    queryDF = pd.read_csv(query,header=None).fillna('NA')
    columnNames = getColumnNames(additionalOptions)
    queryDF.columns = columnNames #get additional info.
    
    col = queryDF.set_index('Symbol').T.to_dict()
    masterDic = {}
    counter=0
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
        content = serialize(data,render_to='chart'+str(counter), title=name.upper()+' Stock',output_type='json')
        content = changeChartOptions(content)
        masterDic['chart'+str(counter)] = {'id':i,
                                            'name':name,
                                            'textdata':col[name],
                                          'content':content}
        counter+=1
    return masterDic

def changeChartOptions(content):
    content = json.loads(content)
    content['rangeSelector'] = {'buttons':[{'type':'minute','count':24*60,
    'text':'24HR'},{'type':'week','count':1,'text':'1W'},{'type':'month','count':1,
    'text':'1M'},{'type':'month','count':3,'text':'3M'},{'type':'year','count':1,
    'text':'1Y'},{'type':'all','text':'ALL'}]}
    content['credits']={'enabled':False}
    content = json.dumps(content)
    return content
    
def getQuery(companyNames):
    base = 'http://finance.yahoo.com/d/quotes.csv?s='
    companyNamesJoined = '+'.join(companyNames)
    base = base+companyNamesJoined+'&f='
    
    additionalOptions = ['s','a','b','y','d','r1','e','e7','e8','e9','j4','r','s7']
    #symbol / ask / bid / dividend yield / div per share / div pay date / 
     #earnings per share / EPS estimate curr year / EPS est next year / EPS est next quarter
    #EBITDA / p/e ratio / short ratio
    
    finalQuery = base +  ''.join(additionalOptions)
    return finalQuery,additionalOptions

def getColumnNames(additionalOptions):
    with open('nameMatch.pkl', 'rb') as handle:
        referenceDic = pickle.load(handle)
    columnNames = [referenceDic[x] for x in additionalOptions]
    return columnNames
    
if __name__ == "__main__":
	app.run(port=5000,debug=True)