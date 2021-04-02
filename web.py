# streamlit для разворота приложения
import streamlit as st

def web_search():

    st.title('Поисквая система')
    title = st.text_input('Что найти?', 'Слово')
    if st.button('Найти'):
        st.write('Идет поиск.... по ...', title)

    # возвращем строку, которую необходимо найти
    return title

web_search()
# print(web_search())