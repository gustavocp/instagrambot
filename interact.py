import random
import streamlit as st

comments = [
    "🤣", "😂", "🔥", "😎", "😍", "👍", "👏", "❤️", "💯", "😅",
    "Muito bom!", "Incrível!", "Que top!", "Amei isso!", "Haha, demais!",
    "Uhuu!", "Rsrs", "Hahaha!", "Espetacular!", "Que massa!"
]

def interact_with_feed(client, log_container, like_chance):
    """
    Interage com o feed de postagens.
    """
    try:
        log_container.write("[INFO] Acessando feed...")
        feed_posts = client.get_timeline_feed().get("feed_items", [])
        if not feed_posts:
            log_container.write("[INFO] Nenhuma postagem encontrada no feed.")
            return

        # Seleciona um post válido do feed
        post = random.choice([item for item in feed_posts if item.get("media_or_ad")])
        media = post["media_or_ad"]
        username = media["user"]["username"]
        post_url = f"https://www.instagram.com/p/{media['code']}/"

        log_container.markdown(
            f"[INFO] Visualizando postagem de <a href='https://www.instagram.com/{username}/' target='_blank'>@{username}</a> - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        if random.randint(1, 100) <= like_chance:
            client.media_like(media["id"])
            log_container.write(f"[SUCCESS] Curtiu a postagem no feed de @{username}")
        else:
            log_container.write(f"[INFO] Apenas visualizou o post de @{username}.")
    except Exception as e:
        log_container.error(f"[ERROR] Erro ao interagir com o feed: {str(e)}")

def interact_with_hashtags(client, hashtags, log_container, like_chance, follow_chance):
    """
    Interage com postagens de hashtags.
    """
    try:
        hashtag = random.choice(hashtags)
        log_container.write(f"[INFO] Acessando hashtag #{hashtag}")
        posts = client.hashtag_medias_recent(hashtag, amount=20)
        if not posts:
            log_container.write(f"[INFO] Nenhum post encontrado para #{hashtag}")
            return

        post = random.choice(posts)
        username = post.user.username
        post_url = f"https://www.instagram.com/p/{post.code}/"
        profile_url = f"https://www.instagram.com/{username}/"

        log_container.markdown(
            f"[INFO] Post de <a href='{profile_url}' target='_blank'>@{username}</a> - <a href='{post_url}' target='_blank'>Ver Post</a>",
            unsafe_allow_html=True
        )

        if random.randint(1, 100) <= like_chance:
            client.media_like(post.id)
            log_container.write(f"[SUCCESS] Curtiu o post de @{username}")
        else:
            log_container.write(f"[INFO] Decidiu não curtir o post de @{username}.")

        if random.randint(1, 100) <= follow_chance:
            client.user_follow(post.user.pk)
            log_container.write(f"[SUCCESS] Seguiu o usuário @{username}")
        else:
            log_container.write(f"[INFO] Decidiu não seguir o usuário @{username}.")
    except Exception as e:
        log_container.error(f"[ERROR] Erro ao interagir com hashtags: {str(e)}")
