import streamlit as st

st.title('Поисквая система')

title = st.text_input('Что найти?', 'Слово')

if st.button('Найти'):
    st.write('Идет поиск.... по ...', title)
