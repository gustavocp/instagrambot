from instagrapi import Client
import os
import json
import streamlit as st

SESSION_FILE = "session.json"

import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

SESSION_FILE = "session.json"

def login(username, password):
    """
    Login to Instagram using session information or credentials.
    Reuses device UUIDs for consistent logins.
    """
    cl = Client()
    if os.path.exists(SESSION_FILE):
        session = cl.load_settings(SESSION_FILE)
        try:
            cl.set_settings(session)
            cl.login(username, password)

            # Check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                print("[INFO] Sessão inválida, refazendo login com os mesmos UUIDs.")
                old_session = cl.get_settings()

                # Reuse device UUIDs for login
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])
                cl.login(username, password)

            print("[INFO] Login bem-sucedido com sessão.")
            return cl

        except Exception as e:
            print(f"[WARNING] Não foi possível usar a sessão salva: {e}")

    # If session login fails or doesn't exist, login with username/password
    try:
        print("[INFO] Tentando login com usuário e senha.")
        cl.login(username, password)
        print("[INFO] Login bem-sucedido com usuário e senha.")
        cl.dump_settings(SESSION_FILE)
        return cl
    except Exception as e:
        raise Exception(f"[ERROR] Falha ao fazer login: {e}")


# def login(client, username, password):
#     if os.path.exists(SESSION_FILE):
#         st.info("[INFO] Restaurando sessão salva...")
#         client.load_settings(SESSION_FILE)
#     if not client.user_id:
#         st.info("[INFO] Sessão inválida ou expirada. Reautenticando...")
#         client.login(username, password)
#         client.dump_settings(SESSION_FILE)
#         st.success("[INFO] Login bem-sucedido!")
#     else:
#         st.success("[INFO] Sessão carregada com sucesso!")

def ensure_login(client, username, password):
    if not client.user_id:  # Verifica se há um usuário autenticado
        client.login(client, username, password)
        client.dump_settings("session.json")  # Salva a sessão novamente


