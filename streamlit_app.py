import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard IoT", layout="wide")

# Mets BASE dans un secret / variable d'environnement si tu veux (plus propre pour GitHub)
BASE = st.secrets.get("BASE_URL", "https://nodered.gr07mohamedaminafkir.work.gd")

URL_CHAMBRE = f"{BASE}/api/chambre"
URL_CENTRAL = f"{BASE}/api/central"
URL_INF_LIST = f"{BASE}/api/infirmiers"
URL_INF_ADD = f"{BASE}/api/infirmiers"
URL_CENTRAL_CMD = f"{BASE}/api/central/cmd"
URL_TEST_FIRE = f"{BASE}/api/test/fire"

URL_INTERVENTION = f"{BASE}/api/historiqueinterventions"
URL_historique_chambre = f"{BASE}/api/historique"
URL_historique_central = f"{BASE}/api/historiquecentral"

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=2)
def get_json(url, timeout=8):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

def post_json(url, payload, timeout=8):
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return True

def to_df(data):
    if data is None:
        return pd.DataFrame()
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame()

# =========================
# MENU
# =========================
st.sidebar.title("Menu")
page = st.sidebar.radio("Aller à", ["Vue générale", "Comande", "historique", "liste accès"])
st.sidebar.markdown("---")

# =========================
# VUE GENERALE
# =========================
if page == "Vue générale":
    st.title("Dashboard Chambre / Central")
    st_autorefresh(interval=2000, key="refresh_vue_generale")

    try:
        chambre = get_json(URL_CHAMBRE)
    except Exception as e:
        st.error(f"Erreur /api/chambre: {e}")
        chambre = {}

    try:
        central = get_json(URL_CENTRAL)
    except Exception as e:
        st.error(f"Erreur /api/central: {e}")
        central = {}

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.subheader("Chambre")

        k1, k2 = st.columns(2)
        k1.metric("Temp 🌡", f"{chambre.get('temp','-')} °C")
        k2.metric("Hum 💧", f"{chambre.get('hum','-')} %")

        m1, m2 = st.columns(2)
        m1.metric("Lum 💡", f"{chambre.get('lum','-')}")
        m2.metric("MQ2", f"{chambre.get('mq2','-')}")

        t1, t2, t3 = st.columns(3)
        t1.metric("fire", f"{chambre.get('fire','-')}")
        t2.metric("help", f"{chambre.get('help','-')}")
        t3.metric("sos", f"{chambre.get('sos','-')}")

        st.caption(f"Timestamp chambre: {chambre.get('timestamp','-')}")
        st.dataframe(to_df(chambre), use_container_width=True)

    with col_droite:
        st.subheader("Central")

        c1, c2 = st.columns(2)
        c1.metric("Temp 🌡", f"{central.get('temp','-')} °C")
        c2.metric("Hum 💧", f"{central.get('hum','-')} %")

        x1, x2 = st.columns(2)
        x1.metric("Seuil", f"{central.get('seuil','-')}")
        x2.metric("Mode auto", f"{central.get('modauto','-')}")

        st.caption(f"Timestamp central: {central.get('timestamp','-')}")
        st.dataframe(to_df(central), use_container_width=True)

# =========================
# COMMANDE
# =========================
elif page == "Comande":
    st.title("Dashboard Commandes")
    st_autorefresh(interval=1500, key="refresh_cmd")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("Mode AUTO"):
            try:
                post_json(URL_CENTRAL_CMD, {"modauto": 1})
                st.success("AUTO envoyé")
            except Exception as e:
                st.error(f"Erreur AUTO: {e}")

    with c2:
        if st.button("Mode MANU"):
            try:
                post_json(URL_CENTRAL_CMD, {"modauto": 0})
                st.success("MANU envoyé")
            except Exception as e:
                st.error(f"Erreur MANU: {e}")

    with c3:
        if st.button("SOS"):
            try:
                post_json(URL_CENTRAL_CMD, {"sos": 1})
                st.success("SOS envoyé")
            except Exception as e:
                st.error(f"Erreur SOS: {e}")

    with c4:
        if st.button("Test feu"):
            try:
                post_json(URL_TEST_FIRE, {"fire": 1})
                st.success("Test feu envoyé")
            except Exception as e:
                st.error(f"Erreur test feu: {e}")

    with c5:
        if st.button("ACQUITTEMENT"):
            try:
                post_json(URL_CENTRAL_CMD, {"acquit": 1})
                st.success("ACQUIT envoyé")
            except Exception as e:
                st.error(f"Erreur ACQUIT: {e}")

# =========================
# HISTORIQUE (SIMPLE)
# =========================
elif page == "historique":
    st.title("📜 Historique")
    st_autorefresh(interval=5000, key="refresh_hist")

    tab1, tab2, tab3 = st.tabs(["Chambre", "Central", "Interventions"])

    with tab1:
        st.subheader("Historique chambre (brut)")
        try:
            data = get_json(URL_historique_chambre)
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur historique chambre: {e}")

    with tab2:
        st.subheader("Historique central (brut)")
        try:
            data = get_json(URL_historique_central)
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur historique central: {e}")

    with tab3:
        st.subheader("Historique interventions (brut)")
        try:
            data = get_json(URL_INTERVENTION)
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur historique interventions: {e}")

# =========================
# LISTE ACCES
# =========================
elif page == "liste accès":
    st.title("Gestion d'accès (manuel)")

    st.subheader("Ajouter une personne")
    with st.form("add_inf"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        uid = st.text_input("UID (optionnel)")
        submit = st.form_submit_button("Ajouter")

    if submit:
        payload = {"nom": nom.strip(), "prenom": prenom.strip(), "email": email.strip()}
        if uid.strip():
            payload["uid"] = uid.strip()

        try:
            post_json(URL_INF_ADD, payload)
            st.success("✅ Ajout OK")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erreur ajout: {e}")

    st.divider()

    st.subheader("Liste d'accès")
    try:
        infirmiers = get_json(URL_INF_LIST)
        st.dataframe(to_df(infirmiers), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur /api/infirmiers: {e}")
