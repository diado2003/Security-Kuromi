import streamlit as st
from datetime import datetime
import requests

dt = datetime.now()

if "client" not in st.session_state:
    st.session_state["client"] = requests.Session()

if "failed_login_attempts" not in st.session_state:
    st.session_state.failed_login_attempts = 0
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False
if "login_input_username" not in st.session_state:
    st.session_state.login_input_username = ""
if "login_input_password" not in st.session_state:
    st.session_state.login_input_password = ""
if "last_reset_token" not in st.session_state:
    st.session_state.last_reset_token = ""
if "pending_login_username" not in st.session_state:
    st.session_state.pending_login_username = ""
if "pending_login_password" not in st.session_state:
    st.session_state.pending_login_password = ""

# Apply pending autofill before widgets are created.
if st.session_state.pending_login_username:
    st.session_state.login_input_username = st.session_state.pending_login_username
    st.session_state.pending_login_username = ""
if st.session_state.pending_login_password:
    st.session_state.login_input_password = st.session_state.pending_login_password
    st.session_state.pending_login_password = ""

st.subheader("\u00a0\u00a0\u00a0\u00a0Authentification and Security in Web Applications :heart:")

st.markdown(
        """
        <style>
            .role-pill {
                margin: 8px 0 14px 0;
                display: inline-block;
                background: linear-gradient(135deg, #ffd1e8, #ff92c9);
                color: #67163f;
                border: 2px solid #ff5faa;
                border-radius: 18px;
                padding: 10px 16px;
                font-size: 1rem;
                font-weight: 800;
                letter-spacing: 0.04em;
                text-align: center;
                box-shadow: 0 8px 18px rgba(255, 122, 191, 0.25);
            }
        </style>
        """,
        unsafe_allow_html=True,
)



with st.form("login", clear_on_submit=False):
    email = st.text_input("Email (for register)")
    username = st.text_input("Username", key="login_input_username")
    password = st.text_input("Password", type="password", key="login_input_password")
    role = st.selectbox("Role (for register)", ["USER", "ADMIN"], index=0)
    admin_secret = ""
    if role == "ADMIN":
        admin_secret = st.text_input("Enter password for admin", type="password")
    col1, col2, col3= st.columns(3)
    with col1:
        submitted = st.form_submit_button("Login")
    with col3:
        registered = st.form_submit_button("Register")

    if submitted:
        response = st.session_state["client"].post("http://localhost:5000/login",
                                                    json={"username": username, "password": password})
        if response.json()["success"]:
            st.session_state.username = response.json().get("username", username)
            st.session_state.role = response.json().get("role", "USER")
            st.session_state.failed_login_attempts = 0
            st.session_state.show_forgot_password = False
            st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
        else:
            st.session_state.failed_login_attempts += 1
            if st.session_state.failed_login_attempts >= 3:
                st.session_state.show_forgot_password = True
                st.error("Invalid credentials")
                st.warning("Ai depasit 3 incercari gresite. Poti folosi Forgot password mai jos.")
            else:
                remaining = 3 - st.session_state.failed_login_attempts
                st.error(f"Invalid credentials. Incercari ramase pana la reset: {remaining}")

    if 0 < st.session_state.failed_login_attempts < 3:
        st.caption(f"Failed login attempts: {st.session_state.failed_login_attempts}/3")

    if registered:
        response = st.session_state["client"].post("http://localhost:5000/register",
                                                   json={"email": email, "username": username, "password": password, "role": role, "admin_secret": admin_secret})
        if response.json()["success"]:
            st.success("Account creat! Te poti loga acum.")
        else:
            st.error(response.json().get("error", "Eroare la register."))

if st.session_state.show_forgot_password:
    with st.form("forgot_password", clear_on_submit=False):
        st.caption("Forgot password")
        forgot_username = st.text_input(
            "Username for reset",
            value=st.session_state.get("login_input_username", ""),
            key="forgot_username",
        )
        forgot_submit = st.form_submit_button("Generate reset token")
        if forgot_submit:
            response = st.session_state["client"].post(
                "http://localhost:5000/forgot-password",
                json={"username": forgot_username},
            )
            body = response.json()
            if body.get("success"):
                st.session_state.last_reset_token = body.get("reset_token", "")
                st.success("Reset token generat. Acum seteaza parola noua mai jos.")
            else:
                st.error(body.get("error", "Eroare la forgot password."))

    with st.form("reset_password", clear_on_submit=True):
        st.caption("Reset password")
        new_password = st.text_input("New password", type="password", key="new_password_input")
        reset_submit = st.form_submit_button("Reset password")
        if reset_submit:
            reset_token = st.session_state.get("last_reset_token", "")
            if not reset_token:
                st.error("Mai intai apasa Generate reset token.")
                st.stop()

            response = st.session_state["client"].post(
                "http://localhost:5000/reset-password",
                json={"token": reset_token, "new_password": new_password},
            )
            body = response.json()
            if body.get("success"):
                st.session_state.pending_login_username = st.session_state.get("forgot_username", "")
                st.session_state.pending_login_password = new_password
                st.session_state.failed_login_attempts = 0
                st.session_state.show_forgot_password = False
                st.session_state.last_reset_token = ""
                st.success("Parola a fost resetata si completata automat in formularul de login.")
                st.rerun()
            else:
                st.error(body.get("error", "Eroare la reset password."))

if "username" in st.session_state:
    st.sidebar.title(f"Hello {st.session_state.username} :wave:")
    st.sidebar.markdown(
        f"""
        <div class="role-pill">
            ROLE: {st.session_state.get('role', 'USER')}
        </div>
        """,
        unsafe_allow_html=True,
    )
    



c1, c2, c3 = st.columns(3)
with c2:
    st.markdown('<img src="https://i.pinimg.com/originals/0e/39/db/0e39db6b419a3cb9fbc81b2b41a42b4a.gif" width="300">', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    if "username" in st.session_state:
        logged_out = st.button("Logout")
        if logged_out:
            try:
                st.session_state["client"].post("http://127.0.0.1:5000/logout", timeout=5)
            except requests.RequestException:
                pass

            keys_to_clear = [
                "username",
                "role",
                "failed_login_attempts",
                "show_forgot_password",
                "login_input_username",
                "login_input_password",
                "last_reset_token",
                "pending_login_username",
                "pending_login_password",
                "forgot_username",
                "new_password_input",
            ]
            for key in keys_to_clear:
                st.session_state.pop(key, None)

            st.rerun()

c1, c2, c3, c4 = st.columns(4)
with c1: 
    st.write(dt.strftime("%Y-%m-%d\u00a0\u00a0\u00a0\u00a0%H:%M:%S"))






