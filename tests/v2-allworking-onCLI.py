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
    # Delay aleatório entre 20-60 segundos
    delay = random.randint(20, 60)
    print(f"[INFO] Aguardando {delay} segundos antes da próxima ação...")
    time.sleep(delay)

# Função para curtir, seguir e comentar usuários de uma hashtag
def interact_with_hashtags(hashtags):
    global hourly_interactions, daily_interactions
    try:
        # Seleciona uma hashtag aleatória
        hashtag = random.choice(hashtags)
        print(f"[INFO] Acessando hashtag: #{hashtag}")
        
        # Obtém postagens da hashtag
        posts = client.hashtag_medias_recent(hashtag, amount=20)
        if not posts:
            print(f"[INFO] Nenhum post encontrado para a hashtag #{hashtag}")
            return

        # Seleciona um post aleatório
        post = random.choice(posts)
        user_id = post.user.pk
        username = post.user.username
        print(f"[INFO] Selecionado post de @{username} (ID: {user_id})")

        # Decide aleatoriamente se irá curtir o post (50% de chance)
        if random.choice([True, False]):
            enforce_limits()
            client.media_like(post.id)
            print(f"[SUCCESS] Curtiu o post de @{username}")
            hourly_interactions += 1
            daily_interactions += 1
        else:
            print(f"[INFO] Decidiu não curtir o post de @{username} nesta interação.")

        # Decide aleatoriamente se irá seguir o usuário (50% de chance)
        if random.choice([True, False]):
            enforce_limits()
            client.user_follow(user_id)
            print(f"[SUCCESS] Seguiu o usuário @{username}")
            hourly_interactions += 1
            daily_interactions += 1
        else:
            print(f"[INFO] Decidiu não seguir o usuário @{username} nesta interação.")

        # Decide aleatoriamente se irá comentar (50% de chance)
        if random.randint(1, 100) <= 10: 
            enforce_limits()
            comment = random.choice(comments)
            client.media_comment(post.id, comment)
            print(f"[SUCCESS] Comentou no post de @{username}: '{comment}'")
            hourly_interactions += 1
            daily_interactions += 1
        else:
            print(f"[INFO] Decidiu não comentar no post de @{username} nesta interação.")

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
        "brasilmemes", "brincadeiras", "zoeirabr", "comediaengracada", "memesbrasileiros"
    ]

    # Realiza login e salva sessão
    login(USERNAME, PASSWORD)

    # Loop infinito para executar e esperar
    while True:
        interact_with_hashtags(hashtags)
        delay = random.randint(60, 120)
        print(f"[INFO] Ciclo completo. Aguardando {delay} segundos antes do próximo ciclo...")

        time.sleep(delay)  # Aguarda 60-120 segundos antes de executar novamente
