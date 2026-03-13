import streamlit as st
from datetime import datetime
import requests

dt = datetime.now()

st.title("Authentification and Security in Web Applications :heart:")

if "username" in st.session_state:
    st.sidebar.title(f"Hello {st.session_state.username} :wave:")
    


with st.form("login", clear_on_submit=True):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("Login")
    with col2:
        registered = st.form_submit_button("Register")

    if submitted:
        response = requests.post("http://localhost:5000/login",
                                 json={"username": username, "password": password})
        if response.json()["success"]:
            st.session_state.username = username
            st.success(f"Logged in as {username}")
        else:
            st.error("Invalid credentials")

    if registered:
        response = requests.post("http://localhost:5000/register",
                                 json={"username": username, "password": password})
        if response.json()["success"]:
            st.success("Account creat! Te poti loga acum.")
        else:
            st.error(response.json().get("error", "Eroare la register."))


c1, c2, c3 = st.columns(3)
with c2:
    st.markdown('<img src="https://i.pinimg.com/originals/0e/39/db/0e39db6b419a3cb9fbc81b2b41a42b4a.gif" width="300">', unsafe_allow_html=True)


c1, c2, c3, c4 = st.columns(4)
with c4: 
    st.write(dt.strftime("%Y-%m-%d\u00a0\u00a0\u00a0\u00a0%H:%M:%S"))



