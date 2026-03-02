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
  - Supprimer un créneau (si aucune réservation ne l’utilise)
  - Affichage des créneaux libres ou occupés pour la journée

- Gestion des **groupes**
  - Lister les groupes
  - Ajouter un groupe
  - Validation des champs pour éviter les saisies vides ou incorrectes

- Gestion des **réservations**
  - Lister les réservations existantes
  - Ajouter une réservation
  - Modifier une réservation
  - Supprimer une réservation
  - Vérification de la disponibilité des créneaux
  - Contrôle de la date (interdit les dates passées)
  - Affichage du planning journalier

---

## Installation

1. Assurez-vous d’avoir **Python 3.10+** installé sur votre machine.
2. Cloner le projet ou télécharger les fichiers.
3. Installer les dépendances nécessaires :
   ```bash
   pip install mysql-connector-python bcrypt