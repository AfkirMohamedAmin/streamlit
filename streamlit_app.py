import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard IoT", layout="wide")

BASE = "https://nodered.gr07mohamedaminafkir.work.gd"

URL_CHAMBRE = f"{BASE}/api/chambre"
URL_CENTRAL = f"{BASE}/api/central"
URL_INF_LIST = f"{BASE}/api/infirmiers"
URL_INF_ADD = f"{BASE}/api/infirmiers"
URL_APPELS = f"{BASE}/api/appel_en_cours"
URL_CENTRAL_CMD = f"{BASE}/api/central/cmd"
URL_TEST_FIRE = f"{BASE}/api/test/fire"


URL_INTERVENTION = f"{BASE}/api/historiqueinterventions"
URL_historique_chambre = f"{BASE}/api/historique"
URL_historique_central = f"{BASE}/api/historiquecentral"


@st.cache_data(ttl=2, show_spinner=False)
def get_json(url: str, timeout: int = 2):
    r = requests.get(url, timeout=timeout, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()
    return r.json()

def get_json_stable(key, url):
    if key not in st.session_state:
        st.session_state[key] = {}

    try:
        data = get_json(url)
        st.session_state[key] = data
        return data
    except Exception:
        return st.session_state[key]

def refresh_now():
    get_json.clear()  
    st.rerun()


def post_json(url, payload, timeout=8):
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return True


def to_df(data):
    if data is None:
        return pd.DataFrame()
    if isinstance(data, list):
        return pd.DataFrame(data)
    return pd.DataFrame([data])


st.sidebar.title("Menu")
page = st.sidebar.radio("Aller à", ["Vue générale", "historique", "liste accès"])
st.sidebar.markdown("---")

if page == "Vue générale":
    b1, b2 = st.columns([1, 4])
    with b1:
        if st.button("🔄 Rafraîchir maintenant"):
            refresh_now()

    st.title("Dashboard Chambre / Central ")
    st_autorefresh(interval=10000, key="refresh_vue_generale")

    try:
        chambre = get_json_stable("chambre_last", URL_CHAMBRE)
    except Exception as e:
        st.error(f"Erreur /api/chambre: {e}")
        chambre = {}

    try:
        central = get_json_stable("central_last", URL_CENTRAL)
    except Exception as e:
        st.error(f"Erreur /api/central: {e}")
        central = {}

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.subheader(" Chambre")

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

        
    with col_droite:
        st.subheader("Central")

        c1, c2 = st.columns(2)
        c1.metric("Temp 🌡", f"{central.get('temp','-')} °C")
        c2.metric("Hum 💧", f"{central.get('hum','-')} %")

        x1, x2 = st.columns(2)
        x1.metric("Seuil", f"{central.get('seuil','-')}")
        x2.metric("Mode auto", f"{central.get('modauto','-')}")

        
    
    st.subheader("Commandes")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("Mode AUTO"):
            try:
                post_json(URL_CENTRAL_CMD, {"modauto": 1})
                st.success("AUTO envoyé")
                refresh_now()
            except Exception as e:
                st.error(f"Erreur AUTO: {e}")

    with c2:
        if st.button("Mode MANU"):
            try:
                post_json(URL_CENTRAL_CMD, {"modauto": 0})
                st.success("MANU envoyé")
                refresh_now()
                
            except Exception as e:
                st.error(f"Erreur MANU: {e}")

    with c3:
        if st.button("SOS"):
            try:
                post_json(URL_CENTRAL_CMD, {"sos": 1})
                st.success("SOS envoyé")
                refresh_now()
            except Exception as e:
                st.error(f"Erreur SOS: {e}")

    with c4:
        if st.button("test feu"):
            try:
                post_json(URL_TEST_FIRE, {"fire": 1})
                st.success("Test feu envoyé ")
                refresh_now()
            except Exception as e:
                st.error(f"Erreur test feu: {e}")

    with c5:
        if st.button("ACQUITTEMENT"):
            try:
                post_json(URL_CENTRAL_CMD, {"acquit": 1})
                st.success("ACQUIT envoyé")
                refresh_now()
            except Exception as e:
                st.error(f"Erreur ACQUIT: {e}")


    try:
        appel = get_json_stable("appel_last", URL_APPELS)

    except Exception as e:
        st.error(f"Erreur appel en cours: {e}")
        appel = {}

    if not appel:
            st.info("✅ Aucun alerte en cours.")
    else:
        st.subheader("📞 Alerte en cours")


        a1, a2, a3, a4, a5 = st.columns(5)
        a1.metric("Chambre", f"{appel.get('chambre','-')}")
        a2.metric("Type alerte", f"{appel.get('type_alerte','-')}")
        a3.metric("Date prise", f"{appel.get('date_prise','-')}")
        a4.metric("Infirmier UID", f"{appel.get('infirmier_uid','-')}")
        a5.metric("Infirmier nom", f"{appel.get('infirmier_nom','-')}")

elif page == "historique":
    st.title("Historique des données")

    
    st_autorefresh(interval=5000, key="refresh_hist")
    i1, i2 = st.columns(2)
    with i1:
        st.subheader("Historique central")
        try:
            data = get_json_stable("hist_central_last", URL_historique_central)
 
            df = pd.DataFrame(data)                  
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur historique: {e}")
    
    with i2:
        st.subheader("Historique chambre")
        try:
            data = get_json_stable("hist_chambre_last", URL_historique_chambre)
# ex: /api/historique
            df = pd.DataFrame(data)                  # transforme liste JSON -> tableau
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur historique: {e}")

    st.subheader("Historique interventions")
    try:
            data = get_json_stable("hist_interv_last", URL_INTERVENTION)

            df = pd.DataFrame(data)                  # transforme liste JSON -> tableau
            st.dataframe(df, use_container_width=True)
    except Exception as e:
            st.error(f"Erreur historique: {e}")
    
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
            payload = {
                "nom": nom.strip(),
                "prenom": prenom.strip(),
                "email": email.strip(),
            }
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
                data  = get_json_stable("inf_list_last", URL_INF_LIST)

                df = pd.DataFrame(data)                  # transforme liste JSON -> tableau
                st.dataframe(df, use_container_width=True)
    except Exception as e:
            st.error(f"Erreur historique: {e}")
