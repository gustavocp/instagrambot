import streamlit as st
from instagrapi import Client
import os
import random
import time
import json

# Configuração do cliente
client = Client()
SESSION_FILE = "session.json"
STATS_FILE = "stats.json"

# Estatísticas de interações
INTERACTIONS_PER_HOUR = 20
INTERACTIONS_PER_DAY = 300
hourly_interactions = 0
daily_interactions = 0

# Lista de comentários
comments = [
    "🤣", "😂", "🔥", "😎", "😍", "👍", "👏", "❤️", "💯", "😅",
    "Muito bom!", "Incrível!", "Que top!", "Amei isso!", "Haha, demais!",
    "Uhuu!", "Rsrs", "Hahaha!", "Espetacular!", "Que massa!",
    "Show!", "Top demais!", "Kkkk!", "Adorei!", "Divertido!",
    "Genial!", "Ótimo post!", "Boa essa!", "Criativo!", "Melhor do dia!",
    "Rsrs, curti!", "Interessante!", "Legal!", "Uhuul!", "😂😂",
    "Haha, incrível!", "Super criativo!", "Que conteúdo!", "Post genial!", "Tô rindo muito!",
    "😆😆", "👏👏", "Haha, show!", "Melhor hashtag!", "Arrasou!",
    "🤣🤣", "Mandou bem!", "Que ideia!", "Haha, curti muito!", "Rsrs, gostei!"
]

# Função para carregar estatísticas de interações
def load_stats():
    global hourly_interactions, daily_interactions
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            stats = json.load(file)
            hourly_interactions = stats.get("hourly_interactions", 0)
            daily_interactions = stats.get("daily_interactions", 0)

# Função para salvar estatísticas de interações
def save_stats():
    with open(STATS_FILE, "w") as file:
        json.dump({
            "hourly_interactions": hourly_interactions,
            "daily_interactions": daily_interactions
        }, file)

# Função para fazer login e salvar sessão
def login(username, password):
    if os.path.exists(SESSION_FILE):
        st.info("[INFO] Restaurando sessão salva...")
        client.load_settings(SESSION_FILE)
    if not client.user_id:
        st.info("[INFO] Sessão inválida ou expirada. Reautenticando...")
        client.login(username, password)
        client.dump_settings(SESSION_FILE)
        st.success("[INFO] Login bem-sucedido!")
    else:
        st.success("[INFO] Sessão carregada com sucesso!")

# Função para garantir que o login está válido
def ensure_login(username, password):
    if not client.user_id:
        st.warning("[WARNING] Sessão inválida. Reautenticando...")
        login(username, password)

# Função para curtir, seguir e comentar usuários de uma hashtag
def interact_with_hashtags(hashtags, username, password, log_container):
    global hourly_interactions, daily_interactions
    ensure_login(username, password)  # Garante que o login é válido
    try:
        # Seleciona uma hashtag aleatória
        hashtag = random.choice(hashtags)
        hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        log_container.markdown(
            f"[INFO] Acessando hashtag: <a href='{hashtag_url}' target='_blank'>#{hashtag}</a>",
            unsafe_allow_html=True
        )

        # Obtém postagens da hashtag
        posts = client.hashtag_medias_recent(hashtag, amount=20)
        if not posts:
            log_container.write(f"[INFO] Nenhum post encontrado para a hashtag #{hashtag}")
            return

        # Seleciona um post aleatório
        post = random.choice(posts)
        user_id = post.user.pk
        username = post.user.username
        post_url = f"https://www.instagram.com/p/{post.code}/"
        profile_url = f"https://www.instagram.com/{username}/"

        # Log com links clicáveis
        log_container.markdown(
            f"[INFO] Selecionado post de <a href='{profile_url}' target='_blank'>@{username}</a> "
            f"(ID: {user_id}) - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        actions = {"liked": False, "followed": False, "commented": False}

        # Decide aleatoriamente se irá curtir o post (50% de chance)
        if random.choice([True, False]):
            client.media_like(post.id)
            log_container.markdown(
                f"[SUCCESS] Curtiu o post de <a href='{profile_url}' target='_blank'>@{username}</a>",
                unsafe_allow_html=True
            )
            hourly_interactions += 1
            daily_interactions += 1
            actions["liked"] = True
        else:
            log_container.write(f"[INFO] Decidiu não curtir o post de @{username}.")

        # Decide aleatoriamente se irá seguir o usuário (50% de chance)
        if random.choice([True, False]):
            client.user_follow(user_id)
            log_container.markdown(
                f"[SUCCESS] Seguiu o usuário <a href='{profile_url}' target='_blank'>@{username}</a>",
                unsafe_allow_html=True
            )
            hourly_interactions += 1
            daily_interactions += 1
            actions["followed"] = True
        else:
            log_container.write(f"[INFO] Decidiu não seguir o usuário @{username}.")

        # Decide aleatoriamente se irá comentar (10% de chance)
        if random.randint(1, 100) <= 10:
            comment = random.choice(comments)
            client.media_comment(post.id, comment)
            log_container.markdown(
                f"[SUCCESS] Comentou no post de <a href='{profile_url}' target='_blank'>@{username}</a>: '{comment}'",
                unsafe_allow_html=True
            )
            hourly_interactions += 1
            daily_interactions += 1
            actions["commented"] = True
        else:
            log_container.write(f"[INFO] Decidiu não comentar no post de @{username}.")

        log_container.write(f"[INFO] Ações realizadas: {actions}")
        save_stats()  # Salva as estatísticas após cada interação

    except Exception as e:
        if "challenge_required" in str(e):
            log_container.error("[ERROR] Challenge required detectado. Pausando bot.")
            st.stop()
        else:
            log_container.error(f"[ERROR] Erro ao interagir com a hashtag: {str(e)}")

# Interface do Streamlit
def main():
    global hourly_interactions, daily_interactions
    load_stats()  # Carrega as estatísticas ao iniciar

    st.title("Bot de Interação no Instagram")

    # Sidebar com informações de login e estatísticas
    username = st.sidebar.text_input("Usuário do Instagram", value="dr.economicomics")
    password = st.sidebar.text_input("Senha do Instagram", type="password", value="PadraoSS2024!")
    st.sidebar.write(f"Interações na última hora: {hourly_interactions}")
    st.sidebar.write(f"Interações no dia: {daily_interactions}")
    hashtags = st.sidebar.text_area("Hashtags (separadas por vírgulas)", value="memes,humor,engracado,humorbrasil,piadas,rindoalto,comedia,zoeira,memesbr,memesengracados,humornacional,humornegro,risadas,memezando,memedodia,brasilmemes,brincadeiras,zoeirabr,comediaengracada,memesbrasileiros,humordehoje,memesvirais,engracados,zoeiramemes,humoristas,vidadehumorista,piadabr,piadasengracadas,zoeiradiaria,memeiros,humorinteligente,humoradulto,memesdiarios,risos,zoeiraengracada,comediabrasil,divertido,humorbr,zoeiradiaria,humor360,memeshumor,piadadodia,humorvideos,humormemes,memesviral,humorvideosengracados,memesehumor,humorcompartilhado,humorvirais,humorzoeira,comediadigital,memesbrasil,humorlocal,zoeiraextrema,humornacara,risadassinceras,memebrasileiro").split(",")

    # Contêiner para logs
    log_container = st.container()

    # Botões na interface
    if st.sidebar.button("Fazer Login"):
        login(username, password)

    if st.button("Iniciar Interações"):
        while True:
            interact_with_hashtags(hashtags, username, password, log_container)
            delay = random.randint(60, 600)
            log_container.write(f"[INFO] Ciclo completo. Aguardando {delay} segundos antes do próximo ciclo...")
            time.sleep(delay)

if __name__ == "__main__":
    main()
