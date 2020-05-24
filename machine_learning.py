import pandas as pd

#!head -n 5 credit_card_default.csv

def get_df_memory_usage(df, top_columns=5):
    print('Memory usage ----')
    memory_per_column = df.memory_usage(deep=True) / 1024 ** 2
    print(f'Top {top_columns} columns by memory (MB):')
    print(memory_per_column.sort_values(ascending=False) \
                           .head(top_columns))
    print(f'Total size: {memory_per_column.sum():.4f} MB')

df = pd.read_csv('credit_card_default.csv', index_col=0,
                  na_values='')

X = df.copy()
y = X.pop('default_payment_next_month')

df.dtypes



get_df_memory_usage(df)

df_cat = df.copy()
object_columns = df_cat.select_dtypes(include='object').columns
df_cat[object_columns] = df_cat[object_columns].astype('category')

get_df_memory_usage(df_cat)

column_dtypes = {'education': 'category',
                 'marriage': 'category',
                 'sex': 'category',
                 'payment_status_sep': 'category',
                 'payment_status_aug': 'category',
                 'payment_status_jul': 'category',
                 'payment_status_jun': 'category',
                 'payment_status_may': 'category',
                 'payment_status_apr': 'category'}
df_cat2 = pd.read_csv('credit_card_default.csv', index_col=0,
                      na_values='', dtype=column_dtypes)

df_cat.equals(df_cat2)
# True
