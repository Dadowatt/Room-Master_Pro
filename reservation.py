from db_connection import get_cursor
from mysql.connector import IntegrityError

class Reservation:
    @classmethod
    def est_disponible(cls, creneau_id, date_reservation):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "SELECT COUNT(*) as nb FROM reservations WHERE creneau_id = %s AND date = %s",
                (creneau_id, date_reservation,)
            )
            resultat = curseur.fetchone()
        nb = resultat['nb']
        return nb == 0

    @classmethod
    def creer_reservation(cls,date, motif, groupe_id, creneau_id):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "SELECT id FROM creneaux WHERE id = %s", (creneau_id,)
                )
            if curseur.fetchone() is None:
                raise ValueError("créneau inexistant")
          
            curseur.execute(
                    "SELECT id from groupes WHERE id = %s", (groupe_id,)
                )
            if curseur.fetchone() is None:
                raise ValueError("groupe inexistant")
            
        if not cls.est_disponible(creneau_id, date):
            raise ValueError("ce créneau est déjà reservé pour cette date")
        
        try:
            with get_cursor(dictionary=True) as curseur:
                curseur.execute(
                    "INSERT INTO reservations (date, motif, groupe_id, creneau_id) VALUES (%s, %s, %s, %s)",
                    (date, motif, groupe_id, creneau_id)
                )
                id_reservation = curseur.lastrowid
            return cls(id_reservation, date, motif, groupe_id, creneau_id)
        except IntegrityError:
            raise ValueError("créneau déjà pris pour cette date")

        