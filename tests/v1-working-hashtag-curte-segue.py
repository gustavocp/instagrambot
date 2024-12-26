from instagrapi import Client
import os
import random
import time

# Configuração do cliente
client = Client()
SESSION_FILE = "session.json"

# Limites de interações
INTERACTIONS_PER_HOUR = 20
INTERACTIONS_PER_DAY = 300
hourly_interactions = 0
daily_interactions = 0

# Função para fazer login e salvar sessão
def login(username, password):
    if os.path.exists(SESSION_FILE):
        print("[INFO] Restaurando sessão salva...")
        client.load_settings(SESSION_FILE)
        client.login(username, password)
    else:
        print("[INFO] Realizando login manual...")
        client.login(username, password)
        client.dump_settings(SESSION_FILE)
    print("[INFO] Login bem-sucedido!")

# Função para aplicar delay aleatório e limitar interações
def enforce_limits():
    global hourly_interactions, daily_interactions
    if hourly_interactions >= INTERACTIONS_PER_HOUR:
        print("[WARNING] Limite de interações por hora alcançado. Aguardando 1 hora...")
        time.sleep(3600)  # Aguarda 1 hora
        hourly_interactions = 0
    if daily_interactions >= INTERACTIONS_PER_DAY:
        print("[WARNING] Limite de interações diárias alcançado. Finalizando...")
        exit()  # Finaliza o programa para evitar mais interações
    # Delay aleatório entre 2-8 segundos
    delay = random.randint(10, 20)
    print(f"[INFO] Aguardando {delay} segundos antes da próxima ação...")
    time.sleep(delay)

# Função para curtir e seguir usuários de uma hashtag
def interact_with_hashtags(hashtags):
    global hourly_interactions, daily_interactions
    for hashtag in hashtags:
        try:
            print(f"[INFO] Acessando hashtag: #{hashtag}")
            
            # Obtém postagens da hashtag
            posts = client.hashtag_medias_recent(hashtag, amount=20)
            if not posts:
                print(f"[INFO] Nenhum post encontrado para a hashtag #{hashtag}")
                continue

            # Seleciona um post aleatório
            post = random.choice(posts)
            user_id = post.user.pk
            username = post.user.username
            print(f"[INFO] Selecionado post de @{username} (ID: {user_id})")

            # Tenta curtir o post
            enforce_limits()
            client.media_like(post.id)
            print(f"[SUCCESS] Curtiu o post de @{username}")
            hourly_interactions += 1
            daily_interactions += 1

            # Tenta seguir o usuário
            enforce_limits()
            client.user_follow(user_id)
            print(f"[SUCCESS] Seguiu o usuário @{username}")
            hourly_interactions += 1
            daily_interactions += 1

            delay = random.randint(20, 60)
            print(f"[WAITING..] Waiting @{delay} seconds to start again...")
            time.sleep()
            print(f"[INFO] Interações até agora: {hourly_interactions} (hora) / {daily_interactions} (dia)")

        except Exception as e:
            print(f"[ERROR] Erro ao interagir com a hashtag #{hashtag}: {str(e)}")

# Configuração principal
if __name__ == "__main__":
    USERNAME = "dr.economicomics"
    PASSWORD = "PadraoSS2024!"

    # Lista de hashtags para interagir
    hashtags = [
        "humor", "memes", "engracado", "humorbrasil", "piadas",
        "rindoalto", "comedia", "zoeira", "memesbr", "memesengracados",
        "humornacional", "humornegro", "risadas", "memezando", "memedodia",
        "brasilmemes", "brincadeiras", "zoeirabr", "comediaengracada", "memesbrasileiros",
        "humordehoje", "memesvirais", "engracados", "zoeiramemes", "humoristas",
        "vidadehumorista", "piadabr", "piadasengracadas", "zoeiradiaria", "memeiros",
        "humorinteligente", "humoradulto", "memesengracados", "memesdiarios", "risos",
        "zoeiraengracada", "comediabrasil", "divertido", "humorbr", "zoeiradiaria",
        "humor360", "memeshumor", "piadadodia", "humorvideos", "humormemes",
        "memesviral", "humorvideosengracados", "memesehumor", "memesengraçados", "humorcompartilhado",
        "humorvirais", "memesatrasados", "humorzoeira", "comediadigital", "memesbrasil",
        "humorlocal", "zoeiraextrema", "humornacara", "risadassinceras", "memebrasileiro",
        "memesnacionais", "memetemporario", "memetroll", "piadasbr", "risosencontados",
        "memedodiahoje", "humorsincero", "zoeiracomedia", "humorrapido", "memestrending",
        "memesatuais", "comediadiaria", "zoeiravirtual", "zoeiracultural", "memesculturais",
        "zoeirageral", "memesbrasilengraçados", "humorglobal", "memesnovos", "piadasatrasadas",
        "zoeiraviral", "piadasviral", "mememania", "risomania", "memesinterativos",
        "zoeirainterativa", "comediaviral", "memefunny", "memesfamosos", "humorfamoso",
        "memeinterativo", "zoeirafamosa", "humormemesdiarios", "humornotemporario", "humorbrasiliero"
    ]

    # Realiza login e salva sessão
    login(USERNAME, PASSWORD)

    # Interage com as hashtags
    interact_with_hashtags(hashtags)
