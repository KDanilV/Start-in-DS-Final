import sys
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly

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
dat = pd.read_excel('data/saldat.xlsx', header=1)
dat['Наименование отрасли'] = dat['Наименование отрасли'].apply(lambda x: x.strip())
data = dat.iloc[-3:, :]

# Загрузка данных об инфляции
inf = pd.read_excel('data/inflation.xlsx', index_col='Год')
inf = inf['Всего']
inf.name = 'Инфляция'
inf = inf.iloc[1:]
inf = inf.sort_index()

# Список отраслей
spheres = [
    "Обеспечение электрической энергией, газом и паром; кондиционирование воздуха",
    "Строительство",
    "Торговля оптовая и розничная; ремонт автотранспортных средств и мотоциклов"
]

# Функция для отображения данных в Streamlit
def main():
    st.set_page_config('Среднемесячная начисленная заработная плата', layout='wide', initial_sidebar_state='auto')

    # Фильтры
    st.sidebar.header('Фильтр')
    branches = st.sidebar.multiselect('Отрасли:', data['Наименование отрасли'].unique(), spheres)
    years = st.sidebar.slider('За период:', min_value=2000, max_value=2023, value=(2000, 2023))
    show_infl = st.sidebar.checkbox('С учетом накопленной инфляции', value=True)

    if years[0] >= years[1]:
        st.write("Год начала должен быть меньше года окончания")
        sys.exit(0)

    # Фильтрация данных
    filtered_data = data[data['Наименование отрасли'].isin(branches)]
    filtered_data = filtered_data.loc[:, (filtered_data.columns >= str(years[0])) & 
                                        (filtered_data.columns <= str(years[1]))]

    # Отображение данных
    st.markdown("#### Данные о номинальной начисленной заработной плате по выбранным отраслям:")
    st.table(filtered_data)

    # Графическое представление данных
    st.markdown(f"##### Графическое представление значений номинальной {('и реальной ' if show_infl else '')}заработной платы:")
    fig = plt.figure(figsize=(16, 10))
    for sphere in branches:
        data_sphere = filtered_data[filtered_data['Наименование отрасли'] == sphere].drop(columns=['Наименование отрасли'])
        data_sphere_long = data_sphere.melt(var_name='Год', value_name='Зарплата')
        sns.lineplot(data=data_sphere_long, x='Год', y='Зарплата', label=sphere)

    plt.title('Среднемесячная номинальная начисленная заработная плата')
    plt.xlabel('Год')
    plt.ylabel('Средняя заработная плата, руб.')
    plt.legend()
    st.pyplot(fig)

    # Вывод результатов
    st.markdown('''##### Выводы
    Полученные данные позволяют нам заключить, что средняя номинальная зарплата с течением времени многократно увеличилась.
    Как можно видеть из визуализации на момент 2023 года самая высокая зарплата в добывающей промышленности нефти и газа, 
    наименьшая зарплата в промышленности, производящей одежду.''')

# Запуск основной функции
if __name__ == "__main__":
    main()

# import sys
# import streamlit as st
# from wsp import SalaryService
# import math
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# import matplotlib
# import plotly.graph_objects as go
# import plotly
# import openpyxl


# st.set_page_config('Среднемесячная начисленная заработная плата', layout='wide', initial_sidebar_state='auto')
# service = SalaryService()
# service.reload_data()


# st.set_page_config('Среднемесячная начисленная заработная плата', layout='wide', initial_sidebar_state='auto')
# service = SalaryService()
# service.reload_data()

# # --------------------------------------------------------------------------

# default_select = ["Обеспечение электрической энергией, газом и паром; кондиционирование воздуха",
#                   "Строительство",
#                   "Торговля оптовая и розничная; ремонт автотранспортных средств и мотоциклов"]

# st.sidebar.header('Фильтр')

# branches = st.sidebar.multiselect('Отрасли:', service.get_all_branches(), default_select)
# years = st.sidebar.slider('За период:', min_value=2000, max_value=2023, value=(2000, 2023))
# show_infl = st.sidebar.checkbox('С учетом накопленной инфляции', value=True)

# if years[0] >= years[1]:
#     st.write("Год начала должен быть меньше года окончания")
#     sys.exit(0)

# service.set_filter(branches, years[0], years[1])

# st.markdown("#### Данные о номинальной начисленной заработной плате по выбранным отраслям:")
# st.table(service.get_data())

# st.markdown(f"##### Графическое представление значений номинальной {('и реальной ' if show_infl else '')}заработной платы:");
# fig = service.get_salary_plot(years[0], years[1], show_infl)
# st.plotly_chart(fig, use_container_width=True)

# st.markdown(f"##### Заработная плата, дисконтированная к ценам {years[1]} гг.:")

# fig = service.get_salary_discount_plot(years[0], years[1])
# st.plotly_chart(fig, use_container_width=True)

# st.markdown(f'##### Наименьшие и наибольшие з/п по отраслям по состоянию на {years[1]} г.')
# st.markdown('Наведите мышь на столбец, чтобы увидеть название.')

# fig = service.get_min_max_salary_plot(years[1])
# st.plotly_chart(fig, use_container_width=True)

# st.markdown('''##### Выводы
# Полученные данные позволяют нам заключить, что средняя номинальная зарплата с течением времени многократно увеличилась.
# Как можно видеть из визуализации на момент 2023 года самая высокая зарплата в добывающей промышленности нефти и газа, 
# наименьшая зарплата в промышленности, производящей одежду.''')

# st.markdown('---')
# st.markdown('#### Влияние инфляции на изменение з/п')
# st.markdown('Динамика роста заработной платы относительно уровня инфляции:')

# fig = service.get_salary_change_plots()
# st.plotly_chart(fig, use_container_width=True)


# fig = service.get_salary_change_corr_plot()
# st.plotly_chart(fig, use_container_width=True)

# st.markdown('##### Выводы')
# st.markdown('''Средняя реальная зарплата выросла в 3-5 раз за 2000-2023, что значительно отличается от первоначально
#  полученного результата: рост номинальной средней зарплатаы (без учета инфляции) отличается от скорректированного 
#  показателя более чем в 7 раз. Инфляция оказала огромное влияние на показатель изменения зарплаты. Переломным моментом 
#  является 2008 год, когда случился кризис, это видно из корреляционной карты. 
#  До кризиса зарплата росла выше инфляции.''')
