import pandas as pd
import numpy as np


def below(df, data, data2, name=None):
    if name is None:
        name = "Below"
    df_data = pd.DataFrame({'A': data,
                            'B': data2})

    df[name] = df_data['A'].le(df_data['B'])


def above(df, data, data2, name=None):
    if name is None:
        name = "Above"
    df_data = pd.DataFrame({'A': data,
                            'B': data2})

    df[name] = df_data['A'].ge(df_data['B'])


def crossunder(df, data, data2, name=None):
    if name is None:
        name = "Crossunder"

    df_data = pd.DataFrame({'A': data,
                            'B': data.shift(1),
                            'C': data2})

    df_data['Below'] = df_data['A'].le(df_data['C'])
    df_data['Above_Prev'] = df_data['B'].ge(df_data['C'])

    crossunder_list = []
    for i, j in zip(df_data['Below'], df_data['Above_Prev']):
        if i == True and j == True:
            crossunder_list.append(True)
        else:
            crossunder_list.append(False)

    df[name] = crossunder_list


def crossover(df, data, data2, name=None):
    if name is None:
        name = "Crossover"

    df_data = pd.DataFrame({'A': data,
                       'B': data.shift(1),
                       'C': data2})

    df_data['Above'] = df_data['A'].ge(df_data['C'])
    df_data['Below_Prev'] = df_data['B'].le(df_data['C'])

    crossover_list = []
    for i,j in zip(df_data['Above'], df_data['Below_Prev']):
        if i == True and j == True:
            crossover_list.append(True)
        else:
            crossover_list.append(False)

    df[name] = crossover_list


def moving_avg(df, source, length):
    df['MA' + str(length) + '(' + source + ')'] = df[source].rolling(window=length).mean()
    return 'MA' + str(length) + '(' + source + ')'


def percentage_distance(df, comparator, compared):
    df[comparator + '_to_' + compared] = (df[comparator] - df[compared]) / df[compared]
    return comparator + '_to_' + compared