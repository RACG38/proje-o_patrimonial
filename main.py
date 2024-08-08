import streamlit as st

def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"  # Página inicial

    if st.session_state.page == "login":
        import login
        login.main()
    elif st.session_state.page == "app":
        import app
        app.main()

if __name__ == "__main__":
    main()
