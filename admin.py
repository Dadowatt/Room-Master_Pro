import bcrypt

class Admin:
    def __init__(self, id, nom_utilisateur, email, mot_de_passe):
        self.id = id
        self.nom_utilisateur = nom_utilisateur
        self.email = email
        self._mot_de_passe = mot_de_passe

    def verifier_mot_de_passe(self, mot_de_passe_saisi):
        return bcrypt.checkpw(mot_de_passe_saisi.encode('utf-8'), self._mot_de_passe.encode('utf-8'))