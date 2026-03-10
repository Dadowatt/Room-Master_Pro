from db_connection import get_cursor
from creneau import Creneau
from reservation_repo import ReservationRepo
from datetime import datetime

class CreneauRepo:
    """
    Fournit les opérations sur les créneaux horaires dans la base de données.
    Fonctions principales :
    - Lister tous les créneaux.
    - Créer un créneau en vérifiant :
        * le format des heures,
        * que l'heure de fin est après l'heure de début,
        * l'absence de chevauchement avec les créneaux existants.
      Gère la conversion automatique des types (str, time, timedelta) pour compatibilité MySQL/Python.
    - Supprimer un créneau en vérifiant qu'il n'est pas utilisé dans une réservation.
    """
    @staticmethod
    def lister_creneaux():
        liste = []
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM creneaux")
            for r in curseur.fetchall():
                liste.append(Creneau(r['id'], r['heure_debut'], r['heure_fin']))
        return liste

    @staticmethod
    def creer_creneau(heure_debut, heure_fin):
        from datetime import datetime, time

        # Vérification du format
        try:
            h_debut = datetime.strptime(heure_debut, "%H:%M").time()
            h_fin = datetime.strptime(heure_fin, "%H:%M").time()
        except ValueError:
            raise ValueError("Format invalide HH:MM")

        # Vérification que la fin est après le début
        if h_fin <= h_debut:
            raise ValueError("L'heure de fin doit être supérieure à l'heure de début")

        if h_fin > time(23, 59):
            raise ValueError("L'heure de fin ne peut pas dépasser 23:59")

        with get_cursor(dictionary=True) as curseur:

            # Vérification d chevauchement directement en SQL
            curseur.execute("SELECT * FROM creneaux WHERE (%s < heure_fin) AND (%s > heure_debut)",
                             (heure_debut, heure_fin))

            if curseur.fetchone():
                raise ValueError("Ce créneau chevauche un créneau existant")

            curseur.execute(
                "INSERT INTO creneaux (heure_debut, heure_fin) VALUES (%s, %s)",
                (heure_debut, heure_fin)
            )

            id_creneau = curseur.lastrowid

        return Creneau(id_creneau, heure_debut, heure_fin)


    @staticmethod
    def supprimer_creneau(creneau_id):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM creneaux WHERE id = %s", (creneau_id,))
            if not curseur.fetchone():
                raise ValueError("Le créneau n'existe pas")

        if ReservationRepo.compter_reservations_creneau(creneau_id) > 0:
            raise ValueError("Impossible de supprimer ce créneau, il est utilisé dans une réservation")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute("DELETE FROM creneaux WHERE id = %s", (creneau_id,))
        return "Créneau supprimé avec succès"