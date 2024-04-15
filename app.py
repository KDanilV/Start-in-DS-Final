import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import plotly.express as px
import sys
import streamlit as st
import seaborn as sns

st.set_page_config('Среднемесячная начисленная заработная плата', layout='wide', initial_sidebar_state='auto')
st.balloons()
# Загрузка данных об инфляции
inf = st.cache_data(pd.read_excel)('data/inflation.xlsx', index_col='Год')
inf = inf['Всего']
inf.name = 'Инфляция'
inf = inf.iloc[1:]
inf = inf.sort_index()


# Функции для работы с инфляцией
def discount(year_from, year_to, total):
    result = total
    for x in range(year_from, year_to, -1):
        result /= 1.0 + inf.loc[x] / 100.0
    return result

def compound(year_from, year_to, total):
    result = total
    for x in range(year_from, year_to):
        result *= 1.0 + inf.loc[x] / 100.0
    return result

# Загрузка данных
data = st.cache_data(pd.read_excel)('data/saldat.xlsx', header=1)
data['Наименование отрасли'] = data['Наименование отрасли'].apply(lambda x: x.strip().capitalize())
data_2023 = st.cache_data(pd.read_excel)('data/tab3-zpl_2023.xlsx', sheet_name='с 2017 г.')
data_2023['Наименование отрасли'] = data_2023['Наименование отрасли'].apply(lambda x: x.strip().capitalize())
d2000 = data.copy()
for year in range(2000, 2024):
    d2000[year] = discount(year, 2000, d2000[year])
d2023 = data.copy()
for year in range(2000, 2024):
    d2023[year] = compound(year, 2023, d2023[year])

# Список исследуемых отраслей
spheres = [
    "Обеспечение электрической энергией, газом и паром; кондиционирование воздуха",
    "Строительство",
    "Торговля оптовая и розничная; ремонт автотранспортных средств и мотоциклов"
]

# Фильтры
st.sidebar.header('Фильтр')
branches = st.sidebar.multiselect('Отрасли:', data['Наименование отрасли'].unique(), spheres)
years = st.sidebar.slider('За период:', min_value=2000, max_value=2023, value=(2000, 2023))
show_infl = st.sidebar.checkbox('С учетом накопленной инфляции', value=True)

if years[0] >= years[1]:
    st.write(":red[Год начала должен быть меньше года окончания]")
    sys.exit(0)

# Фильтрация данных
filtered_data = data[data['Наименование отрасли'].isin(branches)]
filtered_data.columns = filtered_data.columns.astype(str)
filtered_data_years = filtered_data.loc[:, (filtered_data.columns >= str(years[0])) &
                                           (filtered_data.columns <= str(years[1]))]
filtered_data = pd.concat([filtered_data['Наименование отрасли'], filtered_data_years], axis=1)

st.markdown("#### :orange[Данные о номинальной начисленной заработной плате по выбранным отраслям:]")
st.table(filtered_data)
st.markdown(f"##### :orange[Графическое представление значений номинальной {('и реальной ' if show_infl else '')}заработной платы:]")
fig1 = plt.figure(figsize=(16, 10))
for sphere in branches:
    if show_infl == True:
        data_sphere = d2000[d2000['Наименование отрасли'] == sphere].drop(columns=['Наименование отрасли'])
        data_sphere = data_sphere.loc[:, years[0]:years[1]]
        data_sphere_long = data_sphere.melt(var_name='Год', value_name='Зарплата')
        sns.lineplot(data=data_sphere_long, x='Год', y='Зарплата', label=sphere)
    else:
        data_sphere = data[data['Наименование отрасли'] == sphere].drop(columns=['Наименование отрасли'])
        data_sphere = data_sphere.loc[:, years[0]:years[1]]
        data_sphere_long = data_sphere.melt(var_name='Год', value_name='Зарплата')
        sns.lineplot(data=data_sphere_long, x='Год', y='Зарплата', label=sphere)

plt.title('Среднемесячная номинальная начисленная заработная плата')
plt.xlabel('Год')
plt.ylabel('Средняя заработная плата, руб.')
plt.legend()
st.pyplot(fig1)

data_list = []
for sphere in spheres:
    if show_infl == True:
        data_sphere = d2000[d2000['Наименование отрасли'] == sphere]
        mean_val = (data_sphere[2023] / data_sphere[2000]).iloc[0]
        data_list.append({'Наименование отрасли': sphere, 'Коэффициент роста': mean_val})
    else:
        data_sphere = data[data['Наименование отрасли'] == sphere]
        mean_val = (data_sphere[2023] / data_sphere[2000]).iloc[0]
        data_list.append({'Наименование отрасли': sphere, 'Коэффициент роста': mean_val})

st.markdown("#### ***__:orange[Исследуемые экономические отрасли]__***")
st.table(pd.DataFrame(data_list))
st.markdown('''#### Вывод: 
На текущем этапе можно сделать вывод, что влияние инфляции огромно, 
достаточно сравнить рост заработной платы с учётом и без учёта инфляции, 
значения могут отличаться друг от друга более, чем в 7 раз''')
st.markdown("#### ________________________________________________________________________")
st.markdown("##### :orange[Сравнение средних значений зарплаты за 2023 год между отраслями]")
salaries_2023 = data_2023[['Наименование отрасли', 2023]]
salaries_2023_sorted = salaries_2023.set_index('Наименование отрасли').sort_values(by=2023)
st.table(salaries_2023_sorted.head(10))
fig2 = plt.figure(figsize=(16, 10))
sns.barplot(x=salaries_2023_sorted.index, y=2023, data=salaries_2023_sorted, palette='viridis')
plt.title('Зарплаты на 2023 год по отраслям')
plt.ylabel('Заработная плата, руб.')
plt.xlabel(None)
plt.grid(True, axis='y')
plt.xticks(ticks=[], labels=[])
plt.tight_layout()
st.pyplot(fig2)
st.markdown('''##### Выводы:
Полученные данные позволяют нам заключить, 
что средняя номинальная зарплата с течением времени многократно увеличилась. 
Как можно видеть из визуализации на момент 2023 года самая высокая зарплата 
в добывающей промышленности нефти и газа, наименьшая зарплата в промышленности, 
производящей одежду.''')
st.markdown("#### ________________________________________________________________________")
dt = data.transpose()
dt = dt.set_axis(dt.iloc[0], axis='columns')
dt = dt.iloc[1:]
dt.index.name = 'Год'
dt.index = dt.index.map(int)
dt = dt.pct_change() * 100.0
dt = dt.iloc[1:]
dt.join(inf)[spheres + ['Инфляция']].transpose()
# Корреляция изменения з/п с инфляцией предыдущего года до и после примерно 2008 г
dx = dt.subtract(inf[inf.index > 2000], axis=0)
dx = dx[spheres]
dx = pd.concat([dx[dx.index <= 2008].corrwith(inf).round(2), dx[dx.index > 2008].corrwith(inf).round(2)], axis=1)
dx = dx.rename({ 0: 'До 2008', 1: 'После 2008' }, axis=1)
# Создаем тепловую карту
fig3 = plt.figure(figsize=(16, 10))
sns.heatmap(dx.transpose(), annot=True, cmap='YlOrBr')
plt.title('Зависимость изменения зааработной платы к прошлому году от уровня инфляции')
plt.xlabel('Год')
plt.ylabel('Наименование отрасли')
plt.xticks(ticks=range(len(dx.index)), labels=[str(year)[:20] for year in dx.index], rotation=45)
st.pyplot(fig3)
st.markdown("#### :green[________________________________________________________________________]")
st.markdown('''#### Выводы:
Средняя реальная зарплата выросла в 3-5 раз за 2000-2023, 
что значительно отличается от первоначально полученного результата: 
рост номинальной средней зарплатаы (без учета инфляции) отличается 
от скорректированного показателя более чем в 7 раз. Инфляция оказала 
огромное влияние на показатель изменения зарплаты. Переломным моментом 
является 2008 год, когда случился кризис, это видно из корреляционной карты. 
До кризиса зарплата росла выше инфляции.''')
st.markdown("#### :green[________________________________________________________________________]")