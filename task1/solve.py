import pandas

pandas.options.display.float_format = '₽{:,.1f}'.format

df = pandas.read_csv("fns_for_model.csv", sep=';')
df2020_2 = df[(df['year'] == 2020) & (df['quarter'] == 2)]
print(df2020_2.describe()[['income', 'income_lic', 'taxesProfit']])

'''
                 income       income_lic      taxesProfit
mean      ₽49,162,468.5     ₽2,799,691.5       ₽934,444.3
std      ₽561,168,304.5    ₽59,778,581.3    ₽25,356,893.8
min                ₽0.0             ₽0.0             ₽0.0
max   ₽65,003,701,175.0 ₽5,025,774,543.0 ₽3,893,742,355.0
'''