# Exercices pratiques — Supabase

> **Prérequis :** avoir suivi la présentation et créé un compte sur [supabase.com](https://supabase.com).  
> **Niveau :** débutant à intermédiaire.

---

## Module 1 — Prise en main du Dashboard

### Exercice 1.1 — Créer son premier projet

**Objectif :** se familiariser avec l'interface Supabase et créer un projet fonctionnel.

**Instructions :**

1. Connectez-vous sur [supabase.com](https://supabase.com) et créez un compte.
2. Créez un nouveau projet nommé `mon-premier-projet`.
3. Choisissez la région **West EU (Paris)** et définissez un mot de passe de base de données sécurisé.
4. Une fois le projet créé, rendez-vous dans **Settings > Data API** et notez :
   - Votre `Project URL`
5. Une fois le projet créé, rendez-vous dans **Settings > API keys** et notez :
   - Votre `Publishable key`
   - Votre `anon (public) key`
6. Explorez chaque section du Dashboard (Table Editor, SQL Editor, Auth, Storage, Edge Functions) et décrivez en une phrase à quoi sert chacune.

**Livrable :** un fichier `.env` avec vos clés et vos descriptions de sections.

```
SUPABASE_URL=https://votre-id.supabase.co
SUPABASE_ANON_KEY=votre_cle_anon
```

---

### Exercice 1.2 — Créer une table via l'interface

**Objectif :** créer une table sans écrire de SQL, via le Table Editor.

**Instructions :**

1. Allez dans **Table Editor > New Table**.
2. Créez une table `livres` avec les colonnes suivantes :

| Nom de la colonne | Type | Contraintes |
|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` |
| `titre` | `text` | Not Null |
| `auteur` | `text` | Not Null |
| `annee_publication` | `int4` | — |
| `disponible` | `bool` | Default: `true` |
| `created_at` | `timestamptz` | Default: `now()` |

3. Laissez **RLS désactivé** pour l'instant.
4. Insérez 3 livres manuellement depuis l'interface (bouton **Insert row**).

**Question :** Quelle URL d'API a été automatiquement créée pour cette table ? (cherchez dans la documentation auto-générée de votre projet)

**Tips :**
- Il y a un assistant IA disponible sur le site si vous avez des questions, il est à jour sur la structure du site.
- Vous pouvez observer l'onglet intégration.

**Note :** Attention en production il ne faut pas laisser le RLS désactivé ou la base de données est consultable sans authentification.

---

### Exercice 1.3 — Explorer le SQL Editor

**Objectif :** exécuter des requêtes SQL directement dans Supabase.

**Instructions :**

Ouvrez le **SQL Editor** et exécutez les requêtes suivantes une par une :

```sql
-- 1. Lister tous les livres disponibles
SELECT * FROM livres WHERE disponible = true;

-- 2. Compter les livres par auteur
SELECT auteur, COUNT(*) AS nb_livres
FROM livres
GROUP BY auteur
ORDER BY nb_livres DESC;

-- 3. Ajouter une colonne "genre"
ALTER TABLE livres ADD COLUMN genre text;

-- 4. Mettre à jour un livre (remplacez l'id par un vrai id de votre table)
UPDATE livres SET genre = 'Roman' WHERE id = 'votre-uuid-ici';
```

**Question :** Que se passe-t-il si vous exécutez `DROP TABLE livres;` ? Essayez, puis recréez la table.

**Tips :** Bien vérifiez le nom de la table et attention à la suppression.

---

## Module 2 — Base de données et relations

### Exercice 2.1 — Schéma relationnel complet

**Objectif :** créer un schéma de base de données avec des relations entre tables.

**Contexte :** vous construisez une application de gestion de bibliothèque.

**Instructions :**

Exécutez ce script SQL dans le SQL Editor pour créer l'ensemble du schéma :

```sql
-- Table des membres
CREATE TABLE membres (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  nom         text NOT NULL,
  email       text NOT NULL UNIQUE,
  created_at  timestamptz DEFAULT now()
);

-- Table des livres
CREATE TABLE livres (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  titre       text NOT NULL,
  auteur      text NOT NULL,
  isbn        text UNIQUE,
  stock       int4 DEFAULT 1,
  created_at  timestamptz DEFAULT now()
);

-- Table des emprunts (relation many-to-many)
CREATE TABLE emprunts (
  id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  membre_id     uuid NOT NULL REFERENCES membres(id) ON DELETE CASCADE,
  livre_id      uuid NOT NULL REFERENCES livres(id) ON DELETE CASCADE,
  date_emprunt  timestamptz DEFAULT now(),
  date_retour   timestamptz,
  rendu         bool DEFAULT false
);

-- Index pour les requêtes fréquentes
CREATE INDEX idx_emprunts_membre ON emprunts(membre_id);
CREATE INDEX idx_emprunts_livre  ON emprunts(livre_id);
```

**Vérifications :**

1. Insérez 2 membres, 3 livres et 2 emprunts via le SQL Editor.
2. Exécutez cette requête de jointure et décrivez ce qu'elle retourne :

```sql
SELECT
  m.nom AS membre,
  l.titre AS livre,
  e.date_emprunt,
  e.rendu
FROM emprunts e
JOIN membres m ON m.id = e.membre_id
JOIN livres  l ON l.id = e.livre_id
ORDER BY e.date_emprunt DESC;
```

---

## Module 3 — Authentification

### Exercice 3.1 — Inscription et connexion

**Objectif :** implémenter un flux d'authentification basique en Python.

**Instructions :**

Installez la bibliothèque officielle :

```bash
pip install supabase
```

Créez un fichier `auth.py` avec les fonctions suivantes :

```python
import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

# Inscription
def inscription(email: str, password: str):
    res = supabase.auth.sign_up({"email": email, "password": password})
    print("Utilisateur créé :", res.user.id)
    return res.user

# Connexion
def connexion(email: str, password: str):
    # TODO
    pass

# Déconnexion
def deconnexion():
    # TODO
    pass

# Récupérer l'utilisateur connecté
def moi():
    # TODO : utiliser get_user()
    pass
```

1. Testez l'inscription avec un email valide.
2. Vérifiez dans **Authentication > Users** du Dashboard que l'utilisateur a bien été créé.
3. Connectez-vous avec cet utilisateur et affichez son `id` dans la console.

---

## Module 5 — Row Level Security

### Exercice 5.1 — Activer et tester le RLS

**Objectif :** comprendre l'impact du RLS sur les requêtes.

**Instructions :**

**Étape 1 — Avant RLS**

Depuis votre script Python, affichez le nombre de livres retournés par `select()`. Notez le résultat.

```python
response = supabase.table("livres").select("*").execute()
print(f"Nombre de livres : {len(response.data)}")
```

**Étape 2 — Activer RLS**

```sql
ALTER TABLE livres ENABLE ROW LEVEL SECURITY;
```

Relancez la même requête Python. Que se passe-t-il ? Combien de livres obtenez-vous ?

**Étape 3 — Ajouter une politique de lecture publique**

```sql
CREATE POLICY "lecture publique livres"
ON livres FOR SELECT
USING (true);
```

Relancez la requête. Le résultat a-t-il changé ?

**Question :** Que se passerait-il si vous activiez RLS sur `livres` sans ajouter aucune politique, et qu'un utilisateur connecté essayait d'insérer un nouveau livre ?

---

## Module 6 — Realtime

### Exercice 6.1 — Écouter les changements en temps réel

**Objectif :** mettre en place un abonnement Realtime sur une table.

**Instructions :**

Créez un fichier `realtime.py` :

```python
import time
from supabase import create_client
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def handle_changes(payload):
    print("Changement détecté :", payload["type"])
    print("Données :", payload.get("new") or payload.get("old"))

channel = (
    supabase
    .channel("emprunts-live")
    .on_postgres_changes(
        event="*",
        schema="public",
        table="emprunts",
        callback=handle_changes
    )
    .subscribe()
)

print("En écoute sur la table emprunts... (Ctrl+C pour arrêter)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    supabase.remove_channel(channel)
```

1. Lancez ce script dans un terminal.
2. Dans un second terminal (ou depuis le Dashboard), insérez un nouvel emprunt.
3. Observez les logs dans le premier terminal.

**Questions :**
- Quel est le `type` affiché dans le payload lors d'un INSERT ? D'un DELETE ?
- Quelle clé du payload contient les nouvelles données ? Les anciennes ?

---

*Exercices rédigés pour accompagner la présentation Supabase — niveau débutant à intermédiaire.*
