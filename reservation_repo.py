from db_connection import get_cursor
from reservation import Reservation
from mysql.connector import IntegrityError
from datetime import datetime

class ReservationRepo:
    @staticmethod
    def est_disponible(creneau_id, date_reservation, reservation_id=None):
        """Vérifie si le créneau est libre à une date donnée.
        reservation_id : optionnel, pour exclure la réservation actuelle lors de la modification
        """
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
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Format de date invalide (YYYY-MM-DD)")
        if date_obj < datetime.today().date():
            raise ValueError("Impossible de modifier une réservation vers une date passée")

        # Vérifie que la réservation existe
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM reservations WHERE id=%s", (reservation_id,))
            if not curseur.fetchone():
                raise ValueError("La réservation n'existe pas")

        # Vérifie disponibilité
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
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM reservations WHERE id=%s", (reservation_id,))
            if not curseur.fetchone():
                raise ValueError("La réservation n'existe pas")
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("DELETE FROM reservations WHERE id=%s", (reservation_id,))
        return "Réservation supprimée avec succès"


    @staticmethod
    def compter_reservations_creneau(creneau_id):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT COUNT(*) as nb FROM reservations WHERE creneau_id=%s", (creneau_id,))
            return curseur.fetchone()['nb']
        

    @staticmethod
    def get_reservation_par_creneau_et_date(creneau_id, date):
        """Retourne les infos de réservation pour un créneau à une date donnée"""
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT r.motif, g.nom, g.responsable
                   FROM reservations r
                   JOIN groupes g ON r.groupe_id = g.id
                   WHERE r.creneau_id = %s AND r.date = %s""",
                (creneau_id, date)
            )
            return curseur.fetchone()