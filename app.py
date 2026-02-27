import streamlit as st
import supabase
from supabase import create_client, Client

# Configuration de la page
st.set_page_config(page_title="Mur de Projets", layout="wide")

# Connexion à Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

# 3. Interface (UI)
def main():
    supabase = init_connection()

    if "user" not in st.session_state or st.session_state.user is None:
        try:
            session = supabase.auth.get_session()
            if session:
                st.session_state.user = session.user
        except:
            pass

    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Connexion", "Création de compte"])

        with tab2:
            with st.form("signup"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("S'inscrire"):
                    try:
                        res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        st.success("Compte créé ! Veuillez confirmer votre adresse mail.")
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        with tab1:
            with st.form("login"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Se connecter"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        st.error("Identifiants incorrects")
    else:
        st.sidebar.write(f"Connecté en tant que : {st.session_state.user.email}")
        if st.sidebar.button("Déconnexion"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        st.header("Soumettre une idée")
        tab1, tab2, tab3 = st.tabs(["Lecture des projets","Inserer un projet", "Supprimer un projet"])

        with tab2:
            nom = st.text_input("Votre Nom/Pseudo")
            titre = st.text_input("Titre du projet")
            cat = st.selectbox("Catégorie", ["Web", "IA", "Data", "Scripting"])
            desc = st.text_area("Description courte")
            if st.button("Envoyer au mur "):
                if nom and titre:
                    data = {
                        "etudiant_nom": nom,
                        "titre_projet": titre,
                        "categorie": cat,
                        "description": desc
                    }
                    supabase.table("projets_classe").insert(data).execute()
                    st.success("Projet ajouté !")
                    st.rerun()
                else:
                    st.error("Nom et Titre requis !")

        with tab1:
            st.subheader("Idées partagées par la classe")

            # Récupération des données
            response = supabase.table("projets_classe").select("*").order("created_at", desc=True).execute()
            projets = response.data

            if not projets:
                st.info("Le mur est vide pour l'instant. Soyez le premier à contribuer !")
            else:
                # Affichage sous forme de colonnes pour un rendu "Dashboard"
                for idx, p in enumerate(projets):
                    col_text, col_name = st.columns([0.8, 0.2])
                    col_text.write(p['titre_projet'])
                    col_name.write(f"Par **{p['etudiant_nom']}** • {p['categorie']}")
        with tab3:
            st.subheader("Mes publications")
            st.write("Ici, vous ne pouvez voir et supprimer que les projets que vous avez créés.")
            
            # On ne récupère que les projets de l'utilisateur actuel
            mes_projets = supabase.table("projets_classe").select("*").eq("user_id", st.session_state.user.id).execute().data
            
            if not mes_projets:
                st.write("Vous n'avez posté aucun projet.")
            else:
                for p in mes_projets:
                    col_text, col_btn = st.columns([0.8, 0.2])
                    col_text.write(f"**{p['titre_projet']}** ({p['created_at'][:10]})")
                    if col_btn.button("Supprimer", key=f"del_{p['id']}", type="primary"):
                        supabase.table("projets_classe").delete().eq("id", p['id']).execute()
                        st.success("Supprimé !")
                        st.rerun()

if __name__ == "__main__":
    main()