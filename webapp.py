"""
Created on Wed Sep 22 21:41:59 2021

@author: Carlos Eduardo Gonçalves de Oliveira (cego669)

Description: file containing script for the webapp.
"""

import streamlit as st
import numpy as np
import joblib as jb
from PIL import Image
from itertools import compress
from sklearn.metrics import mean_absolute_error
import plotly.express as px

image = Image.open("Rua_T-65,_Bueno,_Goiânia,_maio_de_2020.jpg")

features = jb.load("features_name.pkl")
best_features_idx = jb.load("best_features_idx.pkl")
best_features = list(compress(features, best_features_idx))

linear_model = jb.load("final_model.pkl")
X = jb.load("X.pkl")
y = jb.load("y.pkl")
y_pred = linear_model.predict(X)

mean_error = mean_absolute_error(y, y_pred)

#####################################################################################
tab = st.sidebar.selectbox("Seções:", ["Previsão de preço", "Performance do modelo"])
st.sidebar.markdown("""

                    
***

<h4>Informações adicionais:</h4>

Os dados usados para treinar o modelo linear foram coletados do [vivareal](https://www.vivareal.com.br).

Este webapp foi criado como forma de interação, sem intenções comerciais.

**Não baseie suas decisões nas previsões do modelo!**

Há várias limitações no modelo , entre as quais pode-se citar o não tratamento
das colinearidades das variáveis preditoras e a pouca quantidade de dados usada
para treinamento. Isso influencia a performance geral e a interpretação dos
resultados.
""", unsafe_allow_html=True)

#####################################################################################

st.markdown("""
<h1 style='text-align: center;'>Apartment Prices, Goiânia</h1>
""", unsafe_allow_html=True)

st.image(image, caption = "https://pt.wikipedia.org/wiki/Ficheiro:Rua_T-65,_Bueno,_Goi%C3%A2nia,_maio_de_2020.jpg")
    
#####################################################################################

if tab == "Previsão de preço":
    st.markdown("""
    ***
    
    Preencha o formulário abaixo e descubra o valor mais provável para o apartamento!
    
    Você pode testar o modelo de previsão usando os apartamentos publicados mais recentemente no [vivareal](https://www.vivareal.com.br/venda/goias/goiania/apartamento_residencial/).
    
    *Obs: propósitos educacionais, somente.*
    
    **Nota:** o modelo foi treinado com dados de 16/09/21. Não planejo treinar o modelo com dados atualizados.
    """, unsafe_allow_html=True)
    
    with st.form(key = "user_input"):
        
        X_user = {feature: 0 for feature in best_features}
        
        st.markdown("""
        <h2 style='text-align: center;'>Dados do apartamento</h2>
        """, unsafe_allow_html=True)
        
        area = st.slider("Área do apartamento (m²)", float(np.exp(np.sqrt(X[:, 0].min()))),
                         float(np.exp(np.sqrt(X[:, 0].max()))),
                         float(np.exp(np.sqrt(X[:, 0].mean()))))
        
        cols = st.columns(4)
        bedroom = cols[0].selectbox("Número de quartos", np.sort(np.unique(X[:, 1])))
        bathroom = cols[1].selectbox("Número de banheiros", np.sort(np.unique(X[:, 2])))
        parking = cols[2].selectbox("Vagas de estacionamento", np.sort(np.unique(X[:, 3])))
        suite = cols[3].selectbox("Número de suítes", np.sort(np.unique(X[:, 4])))
        
        characteristic = st.multiselect("Características do imóvel", best_features[5:-5])
        
        region = st.selectbox("Região de Goiânia", ["region_Leste", "region_Norte", "region_Oeste",
                                                     "region_Sudoeste", "region_Sul", "NA"])
        st.markdown("""
        *Para consultar os bairros de cada região de Goiânia, [clique aqui](https://pt.wikipedia.org/wiki/Lista_de_bairros_de_Goi%C3%A2nia)*
        """, unsafe_allow_html=True)
        predict = st.columns(5)[-1].form_submit_button("Prever preço")
    
    if predict:
        
        X_user["area"] = np.log(area)**2
        X_user["bedroom"] = bedroom
        X_user["bathroom"] = bathroom
        X_user["parking"] = parking
        X_user["suite"] = suite
        
        for char_feature in best_features[5:-5]:
            if char_feature in characteristic:
                X_user[char_feature] = 1
        
        for reg_feature in best_features[-5:]:
            if reg_feature == region:
                X_user[reg_feature] = 1
        
        X_user = np.array([[X_user[feature] for feature in best_features]])
        y_pred = linear_model.predict(X_user)
        
        up_error = np.exp(y_pred + mean_error)
        price = np.exp(y_pred)
        low_error = np.exp(y_pred - mean_error)
        
        st.markdown("""
        ***
        
        <h2 style='text-align: center;'>Preço previsto:</h2>
        
        <h3 style='text-align: center;'>R${}</h3>
        
        
        <h4 style='text-align: center;'>Faixa de erro: R${} - R${}</h4>
        """.format(round(price[0]), round(low_error[0]), round(up_error[0])),
        unsafe_allow_html=True)
else:
    
    st.markdown("""
    <h2 style='text-align: center;'>Performance do modelo linear</h2>
    
    ***
    
    **Relação entre valores observados e preditos**
    """, unsafe_allow_html=True)
    
    scale1 = st.selectbox("Forma de visualização:", ["log(Preço)", "Preço (R$)"])
    if scale1 == "log(Preço)":
        st.plotly_chart(px.scatter(x = y_pred, y = y, labels = {"x": "log(Preço) predito",
                                                               "y": "log(Preço) observado"}))
    else:
        st.plotly_chart(px.scatter(x = np.exp(y_pred), y = np.exp(y), labels = {"x": "Preço predito (R$)",
                                                               "y": "Preço observado (R$)"}))
    
    st.markdown("""
    ***
    
    
    **Resíduos do modelo**
    """, unsafe_allow_html=True)
    
    scale2 = st.selectbox("Forma de visualização:", ["log(Preço)", "Preço (R$)"], key = "669")
    if scale2 == "log(Preço)":
        st.plotly_chart(px.scatter(x = y_pred, y = y - y_pred, labels = {"x": "log(Preço) predito",
                                                               "y": "log(Preço real) - log(Preço predito)"}))
    else:
        st.plotly_chart(px.scatter(x = np.exp(y_pred), y = np.exp(y) - np.exp(y_pred), labels = {"x": "Preço predito (R$)",
                                                               "y": "Preço real - Preço predito (R$)"}))
    
    