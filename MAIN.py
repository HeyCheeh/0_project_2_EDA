import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from scipy.stats import ttest_ind
#from statsmodels.stats import weightstats
pd.set_option('display.max_columns', None)
df = pd.read_csv('C:/Users/Пользователь/Desktop/Python/skillFacktory_Pandas/12. Project EDA/stud_math.xls')

# ПОДГОТОВКА ДАННЫХ ДЛЯ АНАЛИЗА
# числовые значения в единый формат
df = df.astype({'age': 'float64'})

#все названия колонок с маленькой буквы
df.columns = [x.lower() for x in list(df.columns)]

# переименовываем колонку чтобы из одного слова без разделителей
df.rename({'studytime, granular': 'studytime2'}, axis=1, inplace=True)

# Для каждого столбца найдено количество пустых строк
# Удалить пустые только после определения значимых столбцов!!!!
#print(df.isna().sum())

# удаляем данные с результатом теста = 0, как не релевантныею. "0" = тест не сдавался
df = df[df.score != 0]

# выбираем колонки по типу данных и делим базу на две по этому признаку. Позднее поменялся подход.
# Сначала рассматривается вся база, а стиранее строк будет после отбора колонок.
Ncols = df.select_dtypes(include=['number']).columns
NumDF = df.select_dtypes(include=['number'])
Ncols2 = Ncols.drop('score')
Ocols = df.columns.drop(Ncols2)
ObjDF = df.drop(Ncols2, axis=1)

# Зполняем НАН
num_columns = ['age', 'famrel', 'freetime', 'goout', 'health', 'absences', 'score', 'failures', 'studytime', 'traveltime', 'Medu', 'Fedu']
for column in df.columns:
    if column in num_columns:
        median_ = df[column].median()
        df[column].fillna(value=median_, inplace=True, axis=0)
    else:
        mode_ = df[column].mode()[0]
        df[column].fillna(value=mode_, inplace=True, axis=0)

# найдены и убраны выбросы.
# создаем функцию которая создает таблицу со статистикой по каждой колонке
def calc_iqr(columns):
    out = []
    for column in list(columns):
        IQR = df[column].quantile(0.75) - df[column].quantile(0.25)
        perc25 = df[column].quantile(0.25)
        perc75 = df[column].quantile(0.75)
        Lbound = ((perc25 - 1.5 * IQR))
        Ubound = ((perc75 + 1.5 * IQR))
        out.append((column, IQR, perc25, perc75, Lbound,Ubound))
    temp = pd.DataFrame(out, columns=('columns', 'IQR', 'perc25','perc75','Lbound','Ubound'))
    return temp

# Создаем таблицу с результатами вычислений функции
x = calc_iqr(Ncols)

# Цикл удаляет из числовой ДФ строки в которых функция обнаружилы выбросы
df2= df.copy()
for y in range(len(x)):
    lbound = x.iloc[y,4]
    ubound = x.iloc[y,5]
    name = x.iloc[y,0]
    if name != 'failures':  # потому что все считается выбросами, хотя информация важная
         df2 = df2[(df2[name] >= lbound) & (df2[name] <= ubound)]

# Для количественных переменных построены гистограммы распределений и сделаны выводы.
# нужно заменять название обрабатываемой DF внутри функции
def get_boxplot(column):
    fig, ax = plt.subplots(figsize = (14, 4))
    sns.boxplot(x=column, y='score',
                data=df2.loc[df2.loc[:, column].isin(df2.loc[:, column].value_counts().index[:10])],
               ax=ax)
    plt.xticks(rotation=0)
    ax.set_title('Boxplot for ' + column)
    plt.show()

print(get_boxplot('absences'))

# выводы по Номинативным
# school - щкола GP немного лучше в среднем но и разброс больше
# Sex - у женщин максимальный балл выше, средний выше на 7-10 баллов, разброс немного меньше
# address - городские жители слегка выше в среднем, но разброс больше
# famsize -размер семьи. В большой семье слегка ниже в среднем и разброс больше
# pstatus - кто живет раздельно в среднем так же кто и вместе
# mjob - health лучше всего средняя, минимальная, максимальная
# fjob - только те у кого отец учитель - оценки заметно выше
# reason - в среднем одинаково
# guardian - в среднем одинаково
# schoolsup - БЕЗ доп образования сдали тест ЛУЧШЕ в среднем, максимальном, разброс выше
# famsup - одинаково
# paid - дополнительные  занятия - не влияют
# activities - ВНЕучебные не влияют
# nursery - детский сад не влияет
# higher - те кто хочет поступать в высшее стараются получить лучший балл, и это им удается. средняя выше, основная масса
# наблюдений в более высоком диапазоне, выше максимальные значения
# internet - не влияет
# romantic - не влияет

# Гистограммы распределения

# Выводы по колличественным
# Age - явно заметоно что те кому 19 лет плохо сдают, скорее всего оставались на второй год из за неусвоения программы
# medu - у кого мать с высшим образованием слегка выше средняя
# fedu - нет значимых отличий
# traveltime - слишком мало случаев, но все они в узком диапазоне. 7 чел. средний балл 50, макс 60  мин. 34
# studytime - нет значимых отличий
# failures - У кого было больше 1 неудачи - никто не сдавал лучше 50 баллов, но такиз всего 20 чел
# famrel - не влияет
# freetime - не влияет
# goout - не влияет
# health - не влияет
# absences - нужно рассмотреть по-другому


# Дополнительный анализ номинативных переменных Т-тес
def get_stat_dif(column):
    cols = df2.loc[:, column].value_counts().index[:10]
    combinations_all = list(combinations(cols, 2))
    for comb in combinations_all:
        if ttest_ind(df2.loc[df2.loc[:, column] == comb[0], 'score'],
                        df2.loc[df2.loc[:, column] == comb[1], 'score']).pvalue \
            <= 0.05/len(combinations_all):
            print('Найдены статистически значимые различия для колонки', column)
            break

for col in Ocols:
     get_stat_dif(col)

# for col in Ncols:
#     fig, ax = plt.subplots(figsize=(14, 4))
#     df[col].hist()
#     ax.set_title('Boxplot for ' + col)
#     plt.show()

# выводы распределения
# age - сновная масса значений в диапазоне от 15 до 19. то что больше- выбросы ?
# medu - в основном у всех от 9 классов образования
# fedu - есть выбросы,  макс = 4
# traveltime - в основном все живут близко
# studytime - не много тех кто занимается более 5 часов в неделю
# failures - все молодцы
# famrel - есть выбросы, в основном отношения хорошие
# freetime - распределение близко к нормальному
# goout -распределение близко к нормальному
# health - преимущественно хорошее здоровье, но с плохим тоже много около 80 чел.
# absences - есть те кто не появлялись на учебе их так мало что можно считать выбросами
# score - распределение близко к нормальному

# df.medu.hist()
print(df2.corr())




