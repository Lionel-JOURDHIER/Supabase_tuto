# Déploiement d'une base de données sur Supabase
**Tutoriel autonome — Configuration, sécurité et mise en ligne**

---

## Prérequis

Avant de commencer ce tutoriel, vous devez avoir en votre possession :

- **Votre MPD finalisé** — le schéma complet de vos tables avec les types PostgreSQL, les clés primaires, les clés étrangères, les index et les contraintes. Sans ce document, vous ne pouvez pas avancer.
- **Votre dataset nettoyé** — les données prêtes à être insérées, dans un format structuré (DataFrame, CSV, JSON). Elles doivent être déjà dédoublonnées, normalisées et filtrées.
- **Un script d'insertion** — le code Python (SQLAlchemy ou supabase-py) capable de lire votre dataset et d'insérer les lignes en base. Ce script doit déjà être écrit et testé localement avant d'attaquer le déploiement.
- **Python installé** avec les bibliothèques `supabase` et/ou `sqlalchemy` selon votre choix d'interface.
- **Un compte Supabase** — gratuit, créé sur [supabase.com](https://supabase.com).

---

## Étape 1 — Créer le projet Supabase

Connectez-vous à Supabase et créez un nouveau projet. Choisissez une région géographiquement proche de votre usage pour minimiser la latence.

Lors de la création, Supabase vous demandera de définir un mot de passe pour la base PostgreSQL. **Notez-le immédiatement** — il ne sera plus affiché ensuite et vous en aurez besoin pour construire votre URI de connexion.

Attendez que le projet soit entièrement initialisé avant de passer à la suite (environ 1 à 2 minutes).

---

## Étape 2 — Créer les tables depuis votre MPD

Une fois le projet prêt, rendez-vous dans le **SQL Editor** de Supabase. C'est ici que vous allez traduire votre MPD en instructions SQL réelles.

Rédigez les instructions de création de tables dans l'ordre suivant : d'abord les tables sans dépendances (sans clés étrangères), ensuite les tables qui en dépendent. Cet ordre est obligatoire — PostgreSQL refusera de créer une clé étrangère vers une table qui n'existe pas encore.

Pour chaque table, vérifiez que :
- Chaque colonne correspond exactement à une colonne de votre MPD
- Les types PostgreSQL utilisés sont cohérents avec vos données (UUID, TEXT, INTEGER, FLOAT, TIMESTAMPTZ, BOOLEAN)
- Les contraintes sont déclarées (NOT NULL, UNIQUE, DEFAULT)
- Les clés étrangères sont correctement reliées

Une fois le SQL exécuté, vérifiez dans le **Table Editor** que toutes vos tables sont bien présentes avec la bonne structure.

> Supabase utilise nativement les UUID comme identifiants. Si votre MPD prévoit des UUID, la fonction `gen_random_uuid()` est disponible nativement comme valeur par défaut.

---

## Étape 3 — Récupérer les clés de connexion

Supabase met à disposition plusieurs clés selon l'usage. Rendez-vous dans **Settings → API** et **Settings → Database**.

**Pour une connexion via SQLAlchemy** (accès direct PostgreSQL depuis un script Python) : utilisez l'URI de connexion disponible dans Settings → Database → Connection string. Cette URI contient l'hôte, le port, le nom de la base et vos identifiants.

**Pour une connexion via supabase-py** (client officiel Python) : utilisez la `Project URL` et la `service_role key`. Cette clé bypasse la RLS et donne un accès total — elle est adaptée à un usage backend comme l'insertion massive de données depuis un pipeline.

Stockez ces informations dans un fichier `.env` ou dans un fichier `secrets.toml` si vous utilisez Streamlit. **Ne les commitez jamais** dans un dépôt Git — ajoutez ces fichiers à votre `.gitignore` immédiatement.

---

## Étape 4 — Activer la Row Level Security

Activez la RLS sur **chacune de vos tables**, même si votre usage est uniquement backend. C'est une bonne pratique de sécurité qui vous protège contre les accès non intentionnels.

Pour chaque table, réfléchissez aux politiques d'accès nécessaires :
- La lecture des données doit-elle être publique ou restreinte ?
- L'écriture doit-elle être limitée à votre pipeline uniquement ?
- La suppression ou la mise à jour doivent-elles être possibles, et par qui ?

Créez vos Policies depuis l'interface Supabase (Authentication → Policies) ou directement depuis le SQL Editor. Gardez à l'esprit que la `service_role key` bypasse la RLS — les Policies s'appliquent uniquement aux connexions utilisant la clé `anon`.

---

## Étape 5 — Insérer les données

Lancez votre script d'insertion en vous assurant que les variables d'environnement ou le fichier de secrets sont bien chargés avant l'exécution.

Pendant l'insertion, surveillez les points suivants :
- Les erreurs de contrainte (doublons sur une colonne UNIQUE, valeurs NULL sur un champ NOT NULL) — elles indiquent un problème dans votre dataset ou dans votre script
- Les erreurs de clé étrangère — elles indiquent un problème d'ordre d'insertion (une table dépendante insérée avant la table parente)
- Les timeouts sur les gros volumes — pensez à insérer par lots (batch insert) plutôt que ligne par ligne

---

## Étape 6 — Vérifier le déploiement

Une fois l'insertion terminée, effectuez les vérifications suivantes depuis le **Table Editor** ou le **SQL Editor** de Supabase :

- Le nombre de lignes dans chaque table correspond à ce que vous attendez
- Les relations entre tables sont cohérentes (pas de clés étrangères orphelines)
- Les types de données sont correctement respectés
- Les doublons ont bien été éliminés

Exécutez quelques requêtes de contrôle manuelles depuis le SQL Editor pour vous assurer que les jointures entre tables fonctionnent comme prévu.

---

## Étape 7 — Exporter et documenter le schéma

Supabase permet d'exporter le SQL de création de votre base via **Settings → Database → Migrations**. Conservez ce fichier dans votre projet — il constitue la version exécutable de votre MPD et permettra de recréer la base à l'identique sur n'importe quel environnement.

Ce fichier fait partie de votre documentation technique au même titre que vos diagrammes Merise.

---

## Résumé des éléments à avoir avant de commencer

| Élément | Pourquoi |
|---|---|
| MPD finalisé | Définit exactement ce que vous allez créer dans Supabase |
| Dataset nettoyé | Les données à insérer, prêtes et validées |
| Script d'insertion | Le code Python qui charge les données en base |
| Compte Supabase | La plateforme d'hébergement |
| Fichier `.env` / `secrets.toml` | Stockage sécurisé des clés de connexion |

## Résumé des actions dans Supabase

| Action | Où dans Supabase |
|---|---|
| Créer les tables | SQL Editor |
| Vérifier la structure | Table Editor |
| Récupérer les clés API | Settings → API |
| Récupérer l'URI PostgreSQL | Settings → Database |
| Activer la RLS | Authentication → Policies |
| Exporter le schéma SQL | Settings → Database → Migrations |
