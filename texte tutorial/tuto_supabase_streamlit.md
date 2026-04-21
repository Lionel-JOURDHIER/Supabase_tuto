# Tuto — Mur de Projets avec Streamlit & Supabase
**Durée estimée : 15 minutes**

---

## Ce que l'on va construire

Une application web avec :
- Inscription / Connexion utilisateur (Supabase Auth)
- Lecture de tous les projets partagés par la classe
- Insertion d'un nouveau projet
- Suppression de ses propres projets (RLS)

---

## Étape 1 — Créer le projet Supabase (3 min)

1. Aller sur [supabase.com](https://supabase.com) et créer un compte
2. Cliquer sur **New Project**
3. Choisir un nom, un mot de passe, une région → **Create Project**
4. Attendre 1 à 2 minutes que le projet soit prêt

---

## Étape 2 — Créer la table `projets_classe` (2 min)

Dans le menu de gauche → **SQL Editor** → coller et exécuter ce code :

```sql
CREATE TABLE projets_classe (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id),
  etudiant_nom TEXT NOT NULL,
  titre_projet TEXT NOT NULL,
  categorie TEXT,
  description TEXT
);
```

Puis activer la sécurité et créer les politiques d'accès :

```sql
-- Activer la RLS
ALTER TABLE projets_classe ENABLE ROW LEVEL SECURITY;

-- Tout le monde peut lire
CREATE POLICY "lecture publique"
ON projets_classe FOR SELECT
USING (true);

-- Seul un utilisateur connecté peut insérer
CREATE POLICY "insertion authentifiée"
ON projets_classe FOR INSERT
WITH CHECK (auth.uid() IS NOT NULL);

-- Seul l'auteur peut supprimer son propre projet
CREATE POLICY "suppression par auteur"
ON projets_classe FOR DELETE
USING (auth.uid() = user_id);
```

---

## Étape 3 — Récupérer les clés API (30 sec)

Dans le menu de gauche → **Settings** → **API**

Copier :
- `Project URL` → c'est votre `SUPABASE_URL`
- `anon public` → c'est votre `SUPABASE_ANON_KEY`

> ⚠️ Ne jamais utiliser la `service_role key` côté client.

---

## Étape 4 — Configurer le projet Python (2 min)

### Installation des dépendances

```bash
pip install streamlit supabase
```

### Fichier `secrets.toml`

Créer le dossier `.streamlit/` à la racine du projet, puis le fichier `secrets.toml` :

```toml
SUPABASE_URL = "https://<VOTRE_ID>.supabase.co"
SUPABASE_ANON_KEY = "<votre_cle_anon>"
```

> Ce fichier ne doit jamais être commité. Ajouter `.streamlit/secrets.toml` dans votre `.gitignore`.

---

## Étape 5 — Le code complet expliqué (5 min)

Créer un fichier `app.py` et y coller le code suivant :

```python
import streamlit as st
from supabase import create_client, Client

# Configuration de la page
st.set_page_config(page_title="Mur de Projets", layout="wide")

# Connexion à Supabase — mise en cache pour ne pas recréer le client à chaque rerun
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)
```

> `@st.cache_resource` : le client Supabase est créé une seule fois et réutilisé.

---

### Bloc Auth — Vérification de session

```python
def main():
    supabase = init_connection()

    # Vérifie si une session active existe déjà (ex : rechargement de page)
    if "user" not in st.session_state or st.session_state.user is None:
        try:
            session = supabase.auth.get_session()
            if session:
                st.session_state.user = session.user
        except:
            pass
```

> `st.session_state` : stocke des variables entre les reruns Streamlit.

---

### Bloc Auth — Formulaires Connexion / Inscription

```python
    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Connexion", "Création de compte"])

        with tab2:
            with st.form("signup"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("S'inscrire"):
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_password})
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
                    except:
                        st.error("Identifiants incorrects")
```

---

### Bloc Principal — Sidebar + 3 onglets

```python
    else:
        # Sidebar : info utilisateur + déconnexion
        st.sidebar.write(f"Connecté en tant que : {st.session_state.user.email}")
        if st.sidebar.button("Déconnexion"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["Lecture des projets", "Insérer un projet", "Supprimer un projet"])
```

---

### Onglet 2 — Insérer un projet

```python
        with tab2:
            nom = st.text_input("Votre Nom/Pseudo")
            titre = st.text_input("Titre du projet")
            cat = st.selectbox("Catégorie", ["Web", "IA", "Data", "Scripting"])
            desc = st.text_area("Description courte")
            if st.button("Envoyer au mur"):
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
```

> Le champ `user_id` n'est pas envoyé manuellement : il sera géré par la Policy RLS via `auth.uid()`.

---

### Onglet 1 — Lire les projets

```python
        with tab1:
            st.subheader("Idées partagées par la classe")
            response = supabase.table("projets_classe").select("*").order("created_at", desc=True).execute()
            projets = response.data

            if not projets:
                st.info("Le mur est vide pour l'instant.")
            else:
                for p in projets:
                    col_text, col_name = st.columns([0.8, 0.2])
                    col_text.write(p['titre_projet'])
                    col_name.write(f"Par **{p['etudiant_nom']}** • {p['categorie']}")
```

---

### Onglet 3 — Supprimer ses projets

```python
        with tab3:
            st.subheader("Mes publications")
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
```

> La Policy RLS `suppression par auteur` garantit qu'un utilisateur ne peut supprimer que ses propres lignes, même si quelqu'un manipule la requête.

---

## Étape 6 — Lancer l'application (30 sec)

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

---

## Résumé des fichiers

```
mon_projet/
├── app.py
└── .streamlit/
    └── secrets.toml   ← ne jamais commiter ce fichier
```

---

## Points clés à retenir

| Concept | Rôle |
|---|---|
| `@st.cache_resource` | Crée le client Supabase une seule fois |
| `st.session_state.user` | Garde l'utilisateur en mémoire entre les reruns |
| `st.rerun()` | Force le rechargement de l'interface après une action |
| `ANON_KEY` | Clé publique, soumise au RLS — safe côté client |
| RLS Policy | La base de données filtre les données selon l'utilisateur connecté |
