import streamlit as st
import streamlit.components.v1 as components
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import main

def send_email(user_name, user_email):

    from_email = 'renan.acg7@gmail.com'
    from_password = 'wppz gjes uctc hnmc'  # Use a senha de aplicativo gerada aqui
    to_email = 'renan.godinho@svninvest.com.br'

    subject = 'Novo login no site'
    message = f'O usuário {user_name} com o email {user_email} fez login no site.'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

def main():

    st.title("Login seguro")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        user_name = st.text_input("Nome")
        user_email = st.text_input("Email")
        login_button = st.button("Login", key='login_button', help='Fazer login')

        if login_button:

            if user_name and user_email:
                st.session_state.authenticated = True
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                send_email(user_name, user_email)
                st.session_state.page = "app"  # Define a página para redirecionar
                st.rerun()  # Força a reinicialização da aplicação
            else:
                st.error("Por favor, preencha todos os campos.")

        with st.expander("Disclaimer de Privacidade e Proteção de Dados", expanded=False):
            st.write(
                """**1. Proteção de Dados Pessoais**
                
                De acordo com a Lei Geral de Proteção de Dados (LGPD), Lei nº 13.709/2018, garantimos que todas as informações pessoais fornecidas pelos usuários em nossa plataforma são tratadas com a máxima confidencialidade e segurança. Nenhum dado pessoal informado será retido ou utilizado pelo criador da plataforma ou por outros usuários de forma não autorizada.

                **2. Coleta e Uso de Dados**
                
                Os dados pessoais coletados, como nome e e-mail, são utilizados exclusivamente para o propósito de autenticação e controle de acesso. Não coletamos, armazenamos ou utilizamos essas informações para outros fins que não sejam aqueles explicitamente informados ao usuário no momento da coleta.

                **3. Compartilhamento de Informações**
                
                Não compartilhamos informações pessoais com terceiros, exceto conforme exigido por lei ou quando necessário para cumprir obrigações legais. Nenhuma informação fornecida será utilizada para fins publicitários ou promocionais sem o devido consentimento do usuário.

                **4. Armazenamento de Dados**
                
                As informações fornecidas são armazenadas de forma segura e são excluídas automaticamente após a utilização necessária para o controle de acesso. Não mantemos registros de dados pessoais além do necessário para os fins para os quais foram coletados.

                **5. Direitos dos Titulares**
                
                Você tem o direito de acessar, corrigir ou excluir seus dados pessoais a qualquer momento. Para solicitar a exclusão de seus dados ou para quaisquer dúvidas relacionadas à sua privacidade, entre em contato conosco através dos canais disponibilizados em nossa plataforma.

                **6. Alterações no Disclaimer**
                
                Podemos atualizar este disclaimer periodicamente para refletir mudanças nas práticas de privacidade ou exigências legais. Recomendamos que você revise esta política regularmente para se manter informado sobre como protegemos suas informações.
                """
            )

if __name__ == "__main__":
    main()