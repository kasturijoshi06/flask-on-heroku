import requests
import pandas as pd
from bokeh.plotting import figure, output_notebook, show
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.vars = {}


def plot_timeseries(tick, month, year):
    api_URL = "https://www.alphavantage.co/query?"
    data = {
        "function": "TIME_SERIES_DAILY",
        "symbol": tick,
        "outputsize": "full",
        "apikey": "GK74CKOOBO8C3T4B"
    }
    response = requests.get(api_URL, params=data)
    res = response.json()
    data = pd.DataFrame.from_dict(res['Time Series (Daily)'], orient='index').sort_index(axis=1)
    # data.reset_index(level=0, inplace=True)
    data = data.rename(
        columns={"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close",
                 "5. volume": "volume"})
    data.index = pd.to_datetime(data.index)
    data['day'] = data.index.day
    data['month'] = data.index.month
    data['year'] = data.index.year
    data = data.loc[(data['year'] == year) & (data['month'] == month)]
    print(data.head())

    source = ColumnDataSource(data)

    p = figure()
    p.line(source=source, x='day', y='close')
    p.title.text = 'Daily Stock Price'
    p.xaxis.axis_label = 'Date'
    # p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d'], months=['%m/%Y'], years=['%Y'])
    p.yaxis.axis_label = 'Closing price'
    # show(p)
    return p


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        app.vars['ticker'] = request.form['ticker']
        app.vars['month'] = request.form['month']
        app.vars['year'] = request.form['year']
        print(type(app.vars['ticker']))
        print(type(app.vars['month']))
        print(type(app.vars['year']))
        result = plot_timeseries(app.vars['ticker'], int(app.vars['month']), int(app.vars['year']))
        script, div = components(result)
        print(result)
        print(div)
        print(script)
        return render_template('index2.html', script=script, div=div)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=33507, debug=True)
