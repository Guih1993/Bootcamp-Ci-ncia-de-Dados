# -*- coding: utf-8 -*-
"""Analise COVID-2019

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nEOwveQKTne_Kdd0o-pgLA9i5SQJvK-M

# **Análises COVID-19**


Vamos analisar as séries temporais sobre a contaminação do vírus COVID-19 pelo mundo
"""

# Importando bibliotecas
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

#Agora, vamos importar os dados. É importante já dizer no comando pd.read_csv quais são as colunas que serão "parseadas" como datas. O pandas possui métodos robustos para trabalhar com esse tipo de informação

url = 'https://github.com/neylsoncrepalde/projeto_eda_covid/blob/master/covid_19_data.csv?raw=true'

# Importando os dados para a variavel, duas colunas já serão importadas como data
df = pd.read_csv(url, parse_dates=['ObservationDate', 'Last Update'])

# Observeando um amostra dos dados
df.head(10)

df.tail(10)

# Conferindo tipos das variaveis
df.dtypes

# Corrigindo nomes das colunas

import re
def corrige_colunas(col_name):
 return re.sub(r"[/| ]", "", col_name).lower()

df.columns = [corrige_colunas(col) for col in df.columns]
df

df.isnull().sum()

# Analisando dados apenas no Brasil
df.loc[df.countryregion == 'Brazil']

brasil = df.loc[
    (df.countryregion == 'Brazil') &
    (df.confirmed > 0)
]

brasil

"""# **Casos Confirmados**"""

# Grafico da evolução de casos confirmados
px.line(brasil, "observationdate", "confirmed", title="Casos confirmados no Brasil")

# Novos casos por dia
brasil["novoscasos"] = list(map(
    lambda x: 0 if (x==0) else brasil["confirmed"].iloc[x] - brasil["confirmed"].iloc[x-1],
    np.arange(brasil.shape[0])
))

# Visualizando novos casos
px.line(brasil, x="observationdate", y="novoscasos", title="Novos Casos por Dia")

# Evolução de mortes no Brasil
fig = go.Figure()
fig.add_trace(
    go.Scatter(x=brasil.observationdate, y=brasil.deaths, name="Mortes",
               mode= "lines+markers", line={"color":"red"})
)

fig.update_layout(title="Mortes por COVID-19 no Brasil")
fig.show()

# Taxa de crescimento
def taxa_crescimento(data, variable, data_inicio=None, data_fim=None):
  #Se a data de inicio for None, define como primeira data disponivel
  if data_inicio == None:
    data_inicio = data.observationdate.loc[data[variable] > 0].min()
  else:
    data_inicio = pd.to_datetime(data_inicio)

  if data_fim == None:
    data_fim = data.observationdate.iloc[-1]
  else:
    data_fim = pd.to_datetime(data_fim)

  #Define os valores do presente e passado
  passado = data.loc[data.observationdate == data_inicio, variable].values[0]
  presente = data.loc[data.observationdate == data_fim, variable].values[0]
  
  #Define o numero de pontos no tempo a avaliar
  n = (data_fim - data_inicio).days

  #Calcular a taxa
  taxa = (presente/passado)**(1/n) - 1

  return taxa*100

#Taxa de crescimento médio no Covid no Brasil em todo o periodo
taxa_crescimento(brasil, "confirmed")

def taxa_crescimento_diario(data, variable, data_inicio=None):
  #Se a data de inicio for None, define como primeira data disponivel
  if data_inicio == None:
    data_inicio = data.observationdate.loc[data[variable] > 0].min()
  else:
    data_inicio = pd.to_datetime(data_inicio)

  data_fim = data.observationdate.max()
  n = (data_fim - data_inicio).days

  taxas = list(map(
      lambda x: (data[variable].iloc[x] - data[variable].iloc[x-1]) / data[variable].iloc[x-1],
      range(1, n+1)
  ))
  return np.array(taxas) * 100

tx_dia = taxa_crescimento_diario(brasil, "confirmed")

primeiro_dia = brasil.observationdate.loc[brasil.confirmed > 0].min()

px.line(x=pd.date_range(primeiro_dia,brasil.observationdate.max())[1:],
        y=tx_dia, title="Taxa de crescimento de casos confirmados")

"""# **Predições**"""

from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

confirmados = brasil.confirmed
confirmados.index = brasil.observationdate

res = seasonal_decompose(confirmados)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10,8))

ax1.plot(res.observed)
ax2.plot(res.trend)
ax3.plot(res.seasonal)
ax4.plot(confirmados.index, res.resid)
ax4.axhline(0, linestyle="dashed", c="black");

#ARIMA
!pip install pmdarima

from pmdarima.arima import auto_arima
modelo = auto_arima(confirmados)

fig = go.Figure(go.Scatter(
    x=confirmados.index, y=confirmados, name="Observados"
))

fig.add_trace(go.Scatter(
    x=confirmados.index, y=modelo.predict_in_sample(), name="Preditos"
))

fig.add_trace(go.Scatter(
    x=pd.date_range("2020-05-20", "2020-06-20"), y=modelo.predict(31), name="Forecast"
))

fig.update_layout(title="Previsão de casos confirmados no Brasil para os proximos 30 dias")
fig.show()

# Modelo de Crescimento utilizando a biblioteca fbprophet
!conda install -c conda-forge fbprophet -y

from fbprophet import Prophet

# preparando os dados
train = confirmados.reset_index()[:-5]
test = confirmados.reset_index()[-5:]

# renomeia colunas
train.rename(columns={"observationdate":"ds","confirmed":"y"},inplace=True)
test.rename(columns={"observationdate":"ds","confirmed":"y"},inplace=True)
test = test.set_index("ds")
test = test['y']

profeta = Prophet(growth="logistic", changepoints=['2020-03-21', '2020-03-30', '2020-04-25', '2020-05-03', '2020-05-10'])

#pop = 1000000
pop = 211463256 #https://www.ibge.gov.br/apps/populacao/projecao/box_popclock.php
train['cap'] = pop

# Treina o modelo
profeta.fit(train)

# Construindo previsões para o futuro
future_dates = profeta.make_future_dataframe(periods=200)
future_dates['cap'] = pop
forecast =  profeta.predict(future_dates)

fig = go.Figure()

fig.add_trace(go.Scatter(x=forecast.ds, y=forecast.yhat, name='Predição'))
fig.add_trace(go.Scatter(x=test.index, y=test, name='Observados - Teste'))
fig.add_trace(go.Scatter(x=train.ds, y=train.y, name='Observados - Treino'))
fig.update_layout(title='Predições de casos confirmados no Brasil')
fig.show()