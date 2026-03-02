from datetime import datetime

class Creneau:
    def __init__(self, id, heure_debut, heure_fin):
        self.id = id
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin