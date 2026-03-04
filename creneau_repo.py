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
        from datetime import time, timedelta

        try:
            h_debut = datetime.strptime(heure_debut, "%H:%M").time()
            h_fin = datetime.strptime(heure_fin, "%H:%M").time()
        except ValueError:
            raise ValueError("Format invalide HH:MM")

        if h_fin <= h_debut:
            raise ValueError("L'heure de fin doit être supérieure à l'heure de début")

        creneaux_existants = CreneauRepo.lister_creneaux()

        for c in creneaux_existants:
            c_debut = c.heure_debut
            c_fin = c.heure_fin

            if isinstance(c_debut, timedelta):
                total_seconds = c_debut.total_seconds()
                c_debut = time(hour=int(total_seconds//3600), minute=int((total_seconds%3600)//60))
            if isinstance(c_fin, timedelta):
                total_seconds = c_fin.total_seconds()
                c_fin = time(hour=int(total_seconds//3600), minute=int((total_seconds%3600)//60))

            if isinstance(c_debut, str):
                c_debut = datetime.strptime(c_debut, "%H:%M:%S").time()
            if isinstance(c_fin, str):
                c_fin = datetime.strptime(c_fin, "%H:%M:%S").time()

            if h_debut < c_fin and h_fin > c_debut:
                raise ValueError(f"Chevauchement avec le créneau existant {c.heure_debut} - {c.heure_fin}")

        with get_cursor(dictionary=True) as curseur:
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