#app.py
from utils import *

def main():

   # Aplicar as configurações do Streamlit
   simulation_state = inicializa_webpage()

   # Mostrar o gráfico
   if simulation_state == True:    

      atualizar_grafico(Config)

if __name__ == "__main__":
    main()
