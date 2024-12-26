import streamlit as st
from instagrapi import Client
import os
import random
import time
import json

client = Client()
SESSION_FILE = "session.json"
STATS_FILE = "stats.json"
hourly_interactions = 0
daily_interactions = 0
comments = [
    "🤣", "😂", "🔥", "😎", "😍", "👍", "👏", "❤️", "💯", "Muito bom!",
    "Incrível!", "Que top!", "Amei isso!", "Haha, demais!", "Uhuu!"
]

def load_stats():
    global hourly_interactions, daily_interactions
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            stats = json.load(file)
            hourly_interactions = stats.get("hourly_interactions", 0)
            daily_interactions = stats.get("daily_interactions", 0)

def save_stats():
    with open(STATS_FILE, "w") as file:
        json.dump({
            "hourly_interactions": hourly_interactions,
            "daily_interactions": daily_interactions
        }, file)

def login(username, password):
    if os.path.exists(SESSION_FILE):
        client.load_settings(SESSION_FILE)
    if not client.user_id:
        client.login(username, password)
        client.dump_settings(SESSION_FILE)

def interact_with_explore(log_container):
    try:
        log_container.write("[INFO] Acessando a aba Explorar...")
        explore_posts = client.explore_feed().get("items", [])
        if not explore_posts:
            log_container.write("[INFO] Nenhuma postagem na aba Explorar.")
            return

        post = random.choice(explore_posts)
        username = post["user"]["username"]
        post_url = f"https://www.instagram.com/p/{post['code']}/"

        log_container.markdown(
            f"[INFO] Visualizando postagem de <a href='https://www.instagram.com/{username}/' target='_blank'>@{username}</a> - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        if random.choice([True, False]):
            client.media_like(post["id"])
            log_container.write(f"[SUCCESS] Curtiu a postagem no explore de @{username}")
    except Exception as e:
        log_container.error(f"[ERROR] Erro no explore: {str(e)}")

def interact_with_following(log_container):
    try:
        log_container.write("[INFO] Acessando postagens de quem você segue...")
        following = client.user_following(client.user_id)
        if not following:
            log_container.write("[INFO] Nenhuma postagem de quem você segue.")
            return

        random_user = random.choice(list(following.values()))
        user_id = random_user.pk
        username = random_user.username
        profile_url = f"https://www.instagram.com/{username}/"

        log_container.markdown(
            f"[INFO] Selecionado usuário <a href='{profile_url}' target='_blank'>@{username}</a>.",
            unsafe_allow_html=True
        )

        posts = client.user_medias(user_id, amount=10)
        if not posts:
            log_container.write(f"[INFO] @{username} não tem postagens recentes.")
            return

        post = random.choice(posts)
        post_url = f"https://www.instagram.com/p/{post.code}/"

        log_container.markdown(
            f"[INFO] Visualizando post de <a href='{profile_url}' target='_blank'>@{username}</a> - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        if random.choice([True, False]):
            client.media_like(post.id)
            log_container.write(f"[SUCCESS] Curtiu o post de @{username}")
    except Exception as e:
        log_container.error(f"[ERROR] Erro ao interagir com quem você segue: {str(e)}")

def interact_with_hashtags(hashtags, log_container):
    try:
        hashtag = random.choice(hashtags)
        log_container.markdown(f"[INFO] Acessando hashtag: <a href='https://www.instagram.com/explore/tags/{hashtag}/' target='_blank'>#{hashtag}</a>", unsafe_allow_html=True)
        posts = client.hashtag_medias_recent(hashtag, amount=20)
        if not posts:
            log_container.write(f"[INFO] Nenhum post encontrado para a hashtag #{hashtag}")
            return

        post = random.choice(posts)
        user_id = post.user.pk
        username = post.user.username
        post_url = f"https://www.instagram.com/p/{post.code}/"
        profile_url = f"https://www.instagram.com/{username}/"

        log_container.markdown(
            f"[INFO] Selecionado post de <a href='{profile_url}' target='_blank'>@{username}</a> - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        if random.choice([True, False]):
            client.media_like(post.id)
            log_container.write(f"[SUCCESS] Curtiu o post de @{username}")
    except Exception as e:
        log_container.error(f"[ERROR] Erro na hashtag: {str(e)}")

def main():
    global hourly_interactions, daily_interactions
    load_stats()

    st.title("Bot de Interação no Instagram")
    username = st.sidebar.text_input("Usuário do Instagram", value="dr.economicomics")
    password = st.sidebar.text_input("Senha do Instagram", type="password", value="PadraoSS2024!")
    st.sidebar.write(f"Interações na última hora: {hourly_interactions}")
    st.sidebar.write(f"Interações no dia: {daily_interactions}")
    hashtags = st.sidebar.text_area("Hashtags (separadas por vírgulas)", value="memes,humor,engracado,piadas").split(",")

    log_container = st.container()

    if st.sidebar.button("Fazer Login"):
        login(username, password)

    if st.button("Iniciar Interações"):
        while True:
            action_type = random.choices(["hashtags", "explore", "following"], weights=[50, 30, 20], k=1)[0]

            if action_type == "hashtags":
                interact_with_hashtags(hashtags, log_container)
            elif action_type == "explore":
                interact_with_explore(log_container)
            elif action_type == "following":
                interact_with_following(log_container)

            delay = random.randint(60, 600)
            log_container.write(f"[INFO] Ciclo completo. Aguardando {delay} segundos...")
            time.sleep(delay)

if __name__ == "__main__":
    main()