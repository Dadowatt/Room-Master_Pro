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
        

    @classmethod
    def planning_journalier(cls, date):
        planning = []
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """
                SELECT creneaux.heure_debut,
                creneaux.heure_fin,
                reservations.motif,
                groupes.nom,
                groupes.responsable
                FROM creneaux
                LEFT JOIN reservations
                ON creneaux.id = reservations.creneau_id
                AND reservations.date = %s
                LEFT JOIN groupes
                ON reservations.groupe_id = groupes.id
                ORDER BY creneaux.heure_debut;

                    """,
                    (date,)
            )
            resultats = curseur.fetchall()
        for r in resultats:
            if r['nom'] is None:
                planning.append({
                    "heure_debut": r['heure_debut'],
                    "heure_fin": r['heure_fin'],
                    "statut": ['LIBRE'],
                })
            else:
                planning.append({
                    "heure_debut": r['heure_debut'],
                    "heure_fin": r['heure_fin'],
                    "statit": ['Occupé'],
                    "groupe": r['nom'],
                    "motif": r['motif'],
                    "responsable": r['responsable'],
                })
        return planning

    @classmethod
    def disponibilites(cls, date):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """
                SELECT 
                    creneaux.id,
                    creneaux.heure_debut,
                    creneaux.heure_fin,
                    reservations.id AS reservation_id
                FROM creneaux
                LEFT JOIN reservations
                    ON creneaux.id = reservations.creneau_id
                    AND reservations.date = %s
                ORDER BY creneaux.heure_debut
                """,
                (date,)
            )
        resultats = curseur.fetchall()
        
        disponibles = []
        for r in resultats:
            if r['reservation_id'] is None:
                disponibles.append({
                "id": r['id'],
                "heure_debut": r['heure_debut'],
                "heure_fin": r['heure_fin'],
                "statut": "[LIBRE]"
            })

        return disponibles
    
    @classmethod
    def vue_globale(cls, date):
        planning = cls.planning_journalier(date)
        disponibles = []
        for p in planning:
            if p['statut'] == "[LIBRE]":
                disponibles.append(p)

        return {
            "planning complet": planning,
            "disponibilites": disponibles,
        }
        