from db_connection import get_cursor
from datetime import datetime

class Creneau:
    def __init__(self, id, heure_debut, heure_fin):
        self.id = id
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin

    
    @classmethod
    def lister_creneau(cls):
        liste_creneaux = []
        
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM creneaux")
            resultats = curseur.fetchall()

        for r in resultats:
            creneau = cls(r['id'], r['heure_debut'], r['heure_fin'])
            liste_creneaux.append(creneau)
        return liste_creneaux
    
    @classmethod
    def creer_creneau(cls, heure_debut, heure_fin):
        heure_debut_obj = datetime.strptime(heure_debut, "%H:%M").time()
        heure_fin_obj = datetime.strptime(heure_fin, "%H:%M").time()

        if heure_fin_obj <= heure_debut_obj:
            raise ValueError("L'heure de fin doit être supérieure à l'heure de début.")
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "INSERT INTO creneaux (heure_debut, heure_fin) VALUES (%s, %s)",
                (heure_debut, heure_fin)
                )
            id_creneau= curseur.lastrowid
            return cls(id_creneau, heure_debut, heure_fin)