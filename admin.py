from db_connection import get_cursor
import bcrypt

class Admin:
    def __init__(self, id, nom_utilisateur, email, mot_de_passe):
        self.id = id
        self.nom_utilisateur = nom_utilisateur
        self.email = email
        self._mot_de_passe = mot_de_passe

    @classmethod
    def creer_admin(cls, nom_utilisateur, email, mot_de_passe, mot_de_passe_confirmation):
        if mot_de_passe != mot_de_passe_confirmation:
            raise ValueError("les mot de passe ne corresponde pas")
        
        mot_de_passe_bytes = mot_de_passe.encode('utf-8')
        hashed_password = bcrypt.hashpw(mot_de_passe_bytes, bcrypt.gensalt())

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "SELECT id FROM admins WHERE nom_utilisateur = %s OR email = %s",
                (nom_utilisateur, email)
            )
            if curseur.fetchone() is not None:
                raise ValueError("nom d'utilisateur ou email déjà utilisé")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "INSERT INTO admins (nom_utilisateur, email, mot_de_passe) VALUES (%s, %s, %s)",
                (nom_utilisateur, email, hashed_password.decode('utf-8'))
            )
            id_admin = curseur.lastrowid
            #retourner un objet Admin
        return cls(id_admin, nom_utilisateur, email, hashed_password.decode('utf-8'))
    
    
    def verifier_mot_de_passe(self, mot_de_passe_saisi):
        mot_de_passe_bytes = mot_de_passe_saisi.encode('utf-8')
        hash_bytes = self._mot_de_passe.encode('utf-8')
        return bcrypt.checkpw(mot_de_passe_bytes, hash_bytes)
    
    @classmethod
    def login(cls, nom_utilisateur, mot_de_passe_saisi):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "SELECT * FROM admins WHERE nom_utilisateur = %s",
                (nom_utilisateur,)
            )
            admin = curseur.fetchone()
        if admin is None:
            raise ValueError("nom d'utilisateur incorrect")
        if not bcrypt.checkpw(mot_de_passe_saisi.encode('utf-8'), admin['mot_de_passe'].encode('utf-8')):
            raise ValueError("mot de passe incorrect")
        
        return cls(admin['id'], admin['nom_utilisateur'], admin['email'], admin['mot_de_passe'])

        