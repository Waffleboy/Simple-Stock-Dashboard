# Simple_Stock_Dashboard

See a trial of it in action at http://thiru.ml/simplestockdashboard

## Description

Frustrated with having to open multiple tabs to see the performance of multiple stocks? Want to get a quick comprehensive overview of your portfolio quickly without being forced to pay for an expensive service?

Simple Stock Dashboard was built with these principles in mind. It aims to provide a holistic overview of your entire portfolio with key metrics, with minimal user input and frustration.

Simple Stock Dashboard also collects no information, and the data is only stored in your local computer, under your total control.

## Installation

Simply clone the folder, and install the dependencies in the requirements.txt. You need python with pip installed for this step. (pip is included by default for python 3.5 and above)

```python
pip install -r requirements.txt
```

## How to Use - 3 Simple Steps

1. Edit the 'stockname' column in input.csv with the symbols of the stock that you want to track. 
  + The other columns, boughtprice and boughtamount are optional.
  + boughtprice: price you bought the stock for
  + boughtamount: amount of stock bought at specified price

2. In the main folder, run app.py

   ```python
   python app.py
   ```

3. Navigate to http://localhost:5000 and see your dashboard!

## Future Improvements

+ Realtime graph
+ Stock Health metric
+ ~~Profit Made~~ Done

## IMPORTANT NOTES 21/06/2017
Yahoo just disabled access to their Finance API, and only mobile requests or a loophole using crumbs to work. I've patched this, but there's no guarantee this will continue working. Use at own risk.


