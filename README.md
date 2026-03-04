## Room-Master Pro

Room-Master Pro est une application de gestion de salles et de réservations. Elle permet à un administrateur de gérer les créneaux, les groupes et les réservations de manière simple et intuitive.

---

## Fonctionnalités

- Gestion des **administrateurs**
  - Création de compte admin
  - Connexion sécurisée avec mot de passe hashé

- Gestion des **créneaux**
  - Lister les créneaux
  - Ajouter un créneau
    - Vérification des chevauchements
    - Validation des horaires (HH:MM)
  - Supprimer un créneau (si aucune réservation ne l’utilise)
  - Affichage des créneaux libres ou occupés pour la journée
  - Option de création flexible de créneaux lors d’une réservation

- Gestion des **groupes**
  - Lister les groupes
  - Ajouter un groupe
    - Validation des champs pour éviter les saisies vides ou incorrectes
    - Nom et responsable sans chiffres, email valide
  - Supprimer un groupe
    - Vérification que le groupe n’est utilisé dans aucune réservation avant suppression

- Gestion des **réservations**
  - Lister les réservations existantes
  - Ajouter une réservation
    - Choix d’un créneau existant ou création d’un nouveau
    - Validation de la date (interdit les dates passées)
    - Validation du motif (lettres, chiffres, tirets, apostrophes)
    - Vérification de la disponibilité du créneau
  - Modifier une réservation
    - Même validations que pour l’ajout
  - Supprimer une réservation
  - Affichage du planning journalier
  - Export du planning en fichier CSV

---

## Installation

1. Assurez-vous d’avoir **Python 3.10+** installé sur votre machine.  
2. Cloner le projet ou télécharger les fichiers.  
3. Installer les dépendances nécessaires :
   ```bash
   pip install mysql-connector-python bcrypt

## Configurer le fichier .env avec les informations de connexion à votre base de données MySQL :

DB_HOST=localhost
DB_PORT=3306
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
DB_NAME=nom_de_la_base

## Lancer l’application :
python main.py