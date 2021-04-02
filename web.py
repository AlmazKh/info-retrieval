# streamlit для разворота приложения
import streamlit as st
import pandas as pd
import numpy as np

def web_search():

    st.title('Поисквая система')
    title = st.text_input('Что найти?', 'Слово')
    if st.button('Найти'):
        st.write('Идет поиск.... по ...', title)

    # возвращем строку, которую необходимо найти
    return title

# web_search()
array_url=['https://habr.com/ru/news/t/541746/', 'https://habr.com/ru/news/t/541726/']

def web_output(array_url):
    df = pd.DataFrame(array_url)
    st.table(df)

web_output(array_url)