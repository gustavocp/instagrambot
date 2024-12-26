import streamlit as st
import random
import time
from instagrapi import Client
from auth import ensure_login
from interact import interact_with_feed, interact_with_hashtags

# Configurações iniciais
SESSION_FILE = "session.json"

# Função principal
def main():
    st.title("Bot de Interação no Instagram")

    # Sidebar para informações do usuário
    username = st.sidebar.text_input("Usuário do Instagram", value="seu_usuario")
    password = st.sidebar.text_input("Senha do Instagram", type="password", value="sua_senha")

    hashtags = st.sidebar.text_area(
        "Hashtags (separadas por vírgulas)",
        value="memes,humor,engracado,piadas,zoeira"
    ).split(",")

    # Configurações de ações
    st.sidebar.markdown("### Configurações de Interações")
    like_chance = st.sidebar.number_input("Chance de Curtir (%)", min_value=0, max_value=100, value=50)
    follow_chance = st.sidebar.number_input("Chance de Seguir (%)", min_value=0, max_value=100, value=50)

    # Configurações de fluxo
    st.sidebar.markdown("### Configurações de Fluxo")
    feed_chance = st.sidebar.number_input("Chance de Feed (%)", min_value=0, max_value=100, value=50)
    hashtag_chance = st.sidebar.number_input("Chance de Hashtag (%)", min_value=0, max_value=100, value=50)

    # Contêiner para logs
    log_container = st.container()

    # Inicializar o cliente do Instagram
    client = Client()
    client.load_settings(SESSION_FILE)

    # Botão para iniciar o login
    if st.sidebar.button("Fazer Login"):
        try:
            ensure_login(client, username, password)
            st.success("[INFO] Login realizado com sucesso!")
        except Exception as e:
            st.error(f"[ERROR] Falha no login: {str(e)}")

    # Botão para iniciar as interações
    if st.button("Iniciar Interações"):
        while True:
            try:
                ensure_login(client, username, password)  # Garante que o cliente está autenticado

                # Escolha entre feed e hashtags com base nas chances configuradas
                action_type = random.choices(
                    ["feed", "hashtag"],
                    weights=[feed_chance, hashtag_chance],
                    k=1
                )[0]

                if action_type == "feed":
                    interact_with_feed(client, log_container, like_chance)
                else:
                    interact_with_hashtags(client, hashtags, log_container, like_chance, follow_chance)

                # Espera aleatória entre os ciclos
                delay = random.randint(60, 300)
                log_container.write(f"[INFO] Ciclo completo. Aguardando {delay} segundos...")
                time.sleep(delay)

            except Exception as e:
                log_container.error(f"[ERROR] Erro durante a interação: {str(e)}")
                break

if __name__ == "__main__":
    main()
