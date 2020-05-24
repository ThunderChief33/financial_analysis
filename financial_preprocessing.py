import pandas as pd
import yfinance as yf
import quandl
import numpy as np
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode

QUANDL_KEY = '{fJGyUxTo_FKtorXJm2oN}'
quandl.ApiConfig.api_key = QUANDL_KEY

df_quandl = quandl.get(dataset='WIKI/AAPL',
                       start_date='2000-01-01',
                       end_date='2010-12-31')
"""
We can specify multiple datasets at once using a list such as ['WIKI/AAPL', 'WIKI/MSFT'].
The collapse parameter can be used to define the frequency (available options: daily, weekly, monthly, quarterly, or annually).
"""

df_yahoo = yf.download('AAPL',
                       start='2000-01-01',
                       end='2010-12-31',
                       progress=False)
"""
We can pass a list of multiple tickers, such as ['AAPL', 'MSFT'].
We can set auto_adjust=True to download only the adjusted prices.
We can additionally download dividends and stock splits by setting actions='inline'.
Setting progress=False disables the progress bar.
"""

df = yf.download('AAPL',
                 start='2000-01-01',
                 end='2010-12-31',
                 progress=False)

def realized_volatility(x):
    return np.sqrt(np.sum(x**2))

def indentify_outliers(row, n_sigmas=3):
    x = row['simple_rtn']
    mu = row['mean']
    sigma = row['std']

    if (x > mu + 3 * sigma) | (x < mu - 3 * sigma):
        return 1
    else:
        return 0

df = df.loc[:, ['Adj Close']]
df.rename(columns={'Adj Close':'adj_close'}, inplace=True)

df['simple_rtn'] = df.adj_close.pct_change()
df['log_rtn'] = np.log(df.adj_close/df.adj_close.shift(1))

df_all_dates = pd.DataFrame(index=pd.date_range(start='1999-12-31',
                                                end='2010-12-31'))
df = df_all_dates.join(df[['adj_close']], how='left') \
                 .fillna(method='ffill') \
                 .asfreq('M')

df_cpi = quandl.get(dataset='RATEINF/CPI_USA',
                                     start_date='1999-12-01',
                                     end_date='2010-12-31')
df_cpi.rename(columns={'Value':'cpi'}, inplace=True)

df_merged = df.join(df_cpi, how='left')

df_merged['simple_rtn'] = df_merged.adj_close.pct_change()
df_merged['inflation_rate'] = df_merged.cpi.pct_change()

df_merged['real_rtn'] = (df_merged.simple_rtn + 1) / (df_merged.inflation_rate + 1) - 1

df_rv = df.groupby(pd.Grouper(freq='M')).apply(realized_volatility)
df_rv.rename(columns={'log_rtn': 'rv'}, inplace=True)

df_rv.rv = df_rv.rv * np.sqrt(12)

fig, ax = plt.subplots(2, 1, sharex=True)
ax[0].plot(df)
ax[1].plot(df_rv)

fig, ax = plt.subplots(3, 1, figsize=(24, 20), sharex=True)

df.adj_close.plot(ax=ax[0])
ax[0].set(title = 'MSFT time series',
          ylabel = 'Stock price ($)')

df.simple_rtn.plot(ax=ax[1])
ax[1].set(ylabel = 'Simple returns (%)')

df.log_rtn.plot(ax=ax[2])
ax[2].set(xlabel = 'Date',
          ylabel = 'Log returns (%)')


init_notebook_mode()
df.iplot(subplots=True, shape=(3,1), shared_xaxes=True,
               title='MSFT time series')

df_rolling = df[['simple_rtn']].rolling(window=21) \
                               .agg(['mean', 'std'])
df_rolling.columns = df_rolling.columns.droplevel()
df_outliers = df.join(df_rolling)

df_outliers['outlier'] = df_outliers.apply(indentify_outliers,
                                           axis=1)
outliers = df_outliers.loc[df_outliers['outlier'] == 1,
                           ['simple_rtn']]

fig, ax = plt.subplots()

ax.plot(df_outliers.index, df_outliers.simple_rtn,
        color='blue', label='Normal')
ax.scatter(outliers.index, outliers.simple_rtn,
           color='red', label='Anomaly')
ax.set_title("Apple's stock returns")
ax.legend(loc='lower right')
