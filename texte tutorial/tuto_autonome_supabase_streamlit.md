# Mur de Projets — Tutoriel Autonome
**Streamlit + Supabase | Durée estimée : 15 à 20 minutes**

---

## Objectif

Construire une application web permettant à des étudiants de partager leurs idées de projets sur un "mur" commun. Chaque utilisateur peut lire tous les projets, en soumettre un nouveau, et supprimer uniquement les siens.

---

## Ce dont vous avez besoin

- Un compte [supabase.com](https://supabase.com)
- Python installé sur votre machine
- Un éditeur de code (VS Code, PyCharm, etc.)

---

## Étape 1 — Mettre en place Supabase

Commencez par créer un nouveau projet sur Supabase. Une fois le projet prêt, vous devrez créer une table pour stocker les projets de la classe.

Réfléchissez aux informations à stocker pour chaque projet : le nom de l'étudiant, le titre, la catégorie, la description. Pensez également aux colonnes techniques dont vous aurez besoin : un identifiant unique, une date de création, et un identifiant pour savoir quel utilisateur a créé le projet.

Supabase propose plusieurs façons de créer cette table. Choisissez celle qui vous convient : l'éditeur visuel (Table Editor) ou l'éditeur SQL. Les deux mènent au même résultat.

---

## Étape 2 — Sécuriser les données avec la RLS

Une fois la table créée, activez la Row Level Security dessus. Sans cette étape, la table est publique et n'importe qui peut tout lire, modifier ou supprimer.

Une fois la RLS activée, plus personne n'a accès à rien par défaut. Il faut donc créer des politiques (Policies) pour définir précisément qui peut faire quoi.

Pour cette application, réfléchissez à trois règles :
- Qui peut **lire** les projets ? Tout le monde, même sans être connecté ?
- Qui peut **insérer** un projet ? Seulement les utilisateurs connectés ?
- Qui peut **supprimer** un projet ? Seulement la personne qui l'a créé ?

Créez une Policy pour chacune de ces trois actions dans l'interface Supabase. Pour la suppression, vous aurez besoin de comparer l'identifiant de l'utilisateur connecté avec le `user_id` stocké dans la ligne — Supabase met à disposition la fonction `auth.uid()` pour récupérer cet identifiant.

---

## Étape 3 — Récupérer les informations de connexion

Pour que votre application Python puisse communiquer avec Supabase, elle a besoin de deux informations : l'URL de votre projet et une clé d'API.

Ces deux éléments se trouvent dans les paramètres de votre projet Supabase, section API. Utilisez la clé `anon public` (et non la `service_role key`, qui donne un accès total sans restrictions).

---

## Étape 4 — Préparer l'environnement Python

Installez les deux bibliothèques nécessaires : `streamlit` et `supabase`.

Ensuite, créez un fichier de configuration pour stocker vos informations de connexion à Supabase. Streamlit propose un système de "secrets" prévu à cet effet : un fichier `secrets.toml` placé dans un dossier `.streamlit` à la racine de votre projet. Ce fichier contiendra votre URL et votre clé anon.

> ⚠️ Ce fichier contient des informations sensibles. Ne le partagez jamais et ne le commitez pas sur GitHub. Ajoutez-le à votre `.gitignore`.

---

## Étape 5 — Structurer le code

Votre application aura une logique principale en deux grandes parties : ce qui s'affiche quand l'utilisateur **n'est pas connecté**, et ce qui s'affiche quand il **est connecté**.

**Partie non connectée** — Affichez deux onglets : un pour se connecter avec un email et un mot de passe, un autre pour créer un compte. Supabase Auth gère tout le mécanisme de vérification et de création de compte de son côté.

**Partie connectée** — Une fois l'utilisateur authentifié, stockez ses informations dans la session Streamlit (`st.session_state`) pour ne pas perdre son état entre les rechargements de page. Affichez ensuite une barre latérale avec son email et un bouton de déconnexion, ainsi que trois onglets :

- Un onglet pour **lire** tous les projets de la classe, triés du plus récent au plus ancien
- Un onglet pour **soumettre** un nouveau projet via un formulaire
- Un onglet pour **supprimer** ses propres projets

---

## Étape 6 — Points d'attention importants

**La session utilisateur** — Streamlit recharge le script entier à chaque interaction. Pensez à vérifier si une session Supabase existe déjà au démarrage pour éviter que l'utilisateur soit déconnecté à chaque action.

**Le `user_id`** — Lors de l'insertion d'un projet, vous devrez associer la ligne à l'utilisateur connecté. C'est ce lien qui permettra ensuite à la Policy de supression de fonctionner correctement.

**Les clés de boutons** — Si vous affichez plusieurs boutons "Supprimer" dans une boucle, Streamlit a besoin que chacun ait une clé unique pour les distinguer.

**Le rechargement** — Après une insertion ou une suppression, pensez à forcer le rechargement de l'interface pour que les changements apparaissent immédiatement.

---

## Étape 7 — Lancer et tester

Lancez votre application avec la commande Streamlit habituelle et ouvrez-la dans votre navigateur.

Testez les scénarios suivants pour vérifier que tout fonctionne :
- Créer un compte et se connecter
- Soumettre un projet et vérifier qu'il apparaît dans le mur
- Se connecter avec un deuxième compte et vérifier qu'on ne peut pas supprimer les projets de l'autre
- Se déconnecter et vérifier que les projets sont toujours visibles

---

## Aide-mémoire des concepts clés

| Concept | Ce que ça fait |
|---|---|
| Supabase Auth | Gère l'inscription, la connexion et les tokens JWT |
| Row Level Security | Filtre les données directement dans la base selon l'utilisateur |
| Policy | Règle SQL qui définit qui peut faire quelle action sur quelle ligne |
| `auth.uid()` | Fonction Supabase qui retourne l'ID de l'utilisateur connecté |
| `st.session_state` | Mémoire temporaire de Streamlit entre les rechargements |
| `st.rerun()` | Force le rechargement complet de l'interface |
| `secrets.toml` | Fichier de configuration sécurisé pour les variables sensibles |
