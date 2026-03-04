from db_connection import get_cursor
from reservation import Reservation
from mysql.connector import IntegrityError
from datetime import datetime

class ReservationRepo:
    class ReservationRepo:
        """
        Gère toutes les opérations liées aux réservations dans le programme.
        Fonctions principales :
        - Vérifier si un créneau est disponible pour une date donnée.
        - Créer, modifier ou supprimer une réservation.
        - Compter le nombre de réservations pour un créneau.
        - Récupérer les réservations pour un créneau ou pour tous les créneaux d'une date.
    """
    @staticmethod
    def est_disponible(creneau_id, date_reservation, reservation_id=None):
        """Retourne True si le créneau est libre à la date donnée, False sinon."""
        with get_cursor(dictionary=True) as curseur:
            if reservation_id:
                curseur.execute(
                    "SELECT COUNT(*) as nb FROM reservations WHERE creneau_id=%s AND date=%s AND id != %s",
                    (creneau_id, date_reservation, reservation_id)
                )
            else:
                curseur.execute(
                    "SELECT COUNT(*) as nb FROM reservations WHERE creneau_id=%s AND date=%s",
                    (creneau_id, date_reservation)
                )
            return curseur.fetchone()['nb'] == 0

    @staticmethod
    def creer_reservation(date, motif, groupe_id, creneau_id):
        """Crée une nouvelle réservation si le créneau est libre et la date valide."""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Format de date invalide (YYYY-MM-DD)")
        if date_obj < datetime.today().date():
            raise ValueError("Impossible de créer une réservation pour une date passée")
        if not ReservationRepo.est_disponible(creneau_id, date):
            raise ValueError("Ce créneau est déjà réservé pour cette date")
        try:
            with get_cursor(dictionary=True) as curseur:
                curseur.execute(
                    "INSERT INTO reservations (date, motif, groupe_id, creneau_id) VALUES (%s,%s,%s,%s)",
                    (date, motif, groupe_id, creneau_id)
                )
                id_reservation = curseur.lastrowid
            return Reservation(id_reservation, date, motif, groupe_id, creneau_id)
        except IntegrityError:
            raise ValueError("Créneau déjà pris pour cette date")

    @staticmethod
    def modifier_reservation(reservation_id, date, motif, groupe_id, creneau_id):
        """Modifie une réservation existante en vérifiant la disponibilité du créneau."""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Format de date invalide (YYYY-MM-DD)")
        if date_obj < datetime.today().date():
            raise ValueError("Impossible de modifier une réservation vers une date passée")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM reservations WHERE id=%s", (reservation_id,))
            if not curseur.fetchone():
                raise ValueError("La réservation n'existe pas")

        if not ReservationRepo.est_disponible(creneau_id, date, reservation_id):
            raise ValueError("Ce créneau est déjà réservé pour cette date")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "UPDATE reservations SET date=%s, motif=%s, groupe_id=%s, creneau_id=%s WHERE id=%s",
                (date, motif, groupe_id, creneau_id, reservation_id)
            )
        return "Réservation modifiée avec succès"

    @staticmethod
    def supprimer_reservation(reservation_id):
        """Supprime une réservation existante."""
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM reservations WHERE id=%s", (reservation_id,))
            if not curseur.fetchone():
                raise ValueError("La réservation n'existe pas")
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("DELETE FROM reservations WHERE id=%s", (reservation_id,))
        return "Réservation supprimée avec succès"


    @staticmethod
    def compter_reservations_creneau(creneau_id):
        """Retourne le nombre de réservations existantes pour un créneau donné."""
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT COUNT(*) as nb FROM reservations WHERE creneau_id=%s", (creneau_id,))
            return curseur.fetchone()['nb']
        

    @staticmethod
    def get_reservation_par_creneau_et_date(creneau_id, date):
        """Retourne les informations de la réservation pour un créneau et une date précis."""
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT r.motif, g.nom, g.responsable
                   FROM reservations r
                   JOIN groupes g ON r.groupe_id = g.id
                   WHERE r.creneau_id = %s AND r.date = %s""",
                (creneau_id, date)
            )
            return curseur.fetchone()
        
    @staticmethod
    def get_creneaux_et_reservations(date):
        """Retourne la liste des créneaux d'une date avec l'état [LIBRE]/[OCCUPÉ] et les infos du groupe si occupé."""
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT creneaux.heure_debut, creneaux.heure_fin,
                        reservations.motif, groupes.nom, groupes.responsable
                FROM creneaux
                LEFT JOIN reservations 
                    ON creneaux.id = reservations.creneau_id AND reservations.date = %s
                LEFT JOIN groupes 
                    ON reservations.groupe_id = groupes.id
                ORDER BY creneaux.heure_debut""",
                (date,)
            )
            return curseur.fetchall()