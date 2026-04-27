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
if "register_success_message" not in st.session_state:
    st.session_state.register_success_message = ""
if "login_success_message" not in st.session_state:
    st.session_state.login_success_message = ""
if "cute_effect" not in st.session_state:
    st.session_state.cute_effect = ""

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

            .kuromi-stage {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 16px;
                margin-top: 6px;
            }

            .kuromi-card img {
                border-radius: 16px;
                box-shadow: 0 10px 24px rgba(172, 56, 124, 0.18);
            }

            .speech-wrap {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }

            .speech-bubble {
                background: linear-gradient(145deg, #fff8fb, #ffe7f2);
                border: 2px solid #ff8dc2;
                border-radius: 18px;
                color: #7d2758;
                font-size: 1.05rem;
                font-weight: 700;
                line-height: 1.35;
                padding: 12px 16px;
                box-shadow: 0 8px 18px rgba(255, 122, 191, 0.18);
                max-width: 260px;
            }

            .mini-bubbles {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-left: 8px;
            }

            .mini-bubbles span {
                display: inline-block;
                border-radius: 50%;
                background: #ffc1de;
                border: 1px solid #ff92c9;
            }

            .mini-bubbles span:nth-child(1) {
                width: 10px;
                height: 10px;
            }

            .mini-bubbles span:nth-child(2) {
                width: 14px;
                height: 14px;
            }

            .heart-pop-container {
                position: fixed;
                right: 20px;
                top: 90px;
                z-index: 9999;
                pointer-events: none;
                font-size: 1.3rem;
            }

            .heart-pop-container span {
                position: absolute;
                opacity: 0;
                animation: floatHeart 1.8s ease-out forwards;
            }

            .heart-pop-container span:nth-child(1) { left: 0px; animation-delay: 0s; }
            .heart-pop-container span:nth-child(2) { left: 20px; animation-delay: 0.2s; }
            .heart-pop-container span:nth-child(3) { left: 40px; animation-delay: 0.4s; }
            .heart-pop-container span:nth-child(4) { left: 10px; animation-delay: 0.55s; }
            .heart-pop-container span:nth-child(5) { left: 30px; animation-delay: 0.75s; }

            @keyframes floatHeart {
                0% { transform: translateY(0px) scale(0.85); opacity: 0; }
                20% { opacity: 1; }
                100% { transform: translateY(-70px) scale(1.15); opacity: 0; }
            }
        </style>
        """,
        unsafe_allow_html=True,
)

if st.session_state.register_success_message:
    st.success(st.session_state.register_success_message)
    st.session_state.register_success_message = ""

if st.session_state.login_success_message:
    st.success(st.session_state.login_success_message)
    st.session_state.login_success_message = ""

if st.session_state.cute_effect == "hearts":
    st.toast("💖 Account ready!", icon="💗")
    st.markdown(
        """
        <div class="heart-pop-container" aria-hidden="true">
            <span>💖</span><span>💕</span><span>💗</span><span>💘</span><span>💞</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.cute_effect = ""

if st.session_state.cute_effect == "confetti":
    st.toast("✨ Secure login successful!", icon="🎉")
    st.balloons()
    st.session_state.cute_effect = ""



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
            st.session_state.last_reset_token = ""
            st.session_state.pending_login_username = ""
            st.session_state.pending_login_password = ""

            for key in ["login_input_username", "login_input_password", "forgot_username", "new_password_input"]:
                st.session_state.pop(key, None)

            st.session_state.login_success_message = f"Logged in as {st.session_state.username} ({st.session_state.role})"
            st.session_state.cute_effect = "confetti"
            st.rerun()
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
            st.session_state.failed_login_attempts = 0
            st.session_state.show_forgot_password = False
            st.session_state.last_reset_token = ""
            st.session_state.pending_login_username = ""
            st.session_state.pending_login_password = ""
            st.session_state.register_success_message = "Account creat! Acum introdu username si parola pentru login."

            for key in ["login_input_username", "login_input_password", "forgot_username", "new_password_input"]:
                st.session_state.pop(key, None)

            st.session_state.cute_effect = "hearts"
            st.balloons()
            st.rerun()
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
    



c1, c2 = st.columns([1.15, 1], vertical_alignment="center")
with c1:
    st.markdown(
        """
        <div class="kuromi-stage">
            <div class="kuromi-card">
                <img src="https://i.pinimg.com/originals/0e/39/db/0e39db6b419a3cb9fbc81b2b41a42b4a.gif" width="300" alt="Kuromi" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="speech-wrap">
            <div class="speech-bubble">I'll keep your data secure.</div>
            <div class="mini-bubbles"><span></span><span></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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






