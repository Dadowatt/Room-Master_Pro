from db_connection import get_cursor
from admin import Admin
import bcrypt

class AdminRepo:
    @staticmethod
    def creer_admin(nom_utilisateur, email, mot_de_passe, mot_de_passe_confirmation):
        if mot_de_passe != mot_de_passe_confirmation:
            raise ValueError("Les mots de passe ne correspondent pas")

        mot_de_passe_hache = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "SELECT id FROM admins WHERE nom_utilisateur = %s OR email = %s",
                (nom_utilisateur, email)
            )
            if curseur.fetchone() is not None:
                raise ValueError("Nom d'utilisateur ou email déjà utilisé")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "INSERT INTO admins (nom_utilisateur, email, mot_de_passe) VALUES (%s, %s, %s)",
                (nom_utilisateur, email, mot_de_passe_hache)
            )
            id_admin = curseur.lastrowid

        return Admin(id_admin, nom_utilisateur, email, mot_de_passe_hache)

    @staticmethod
    def login(nom_utilisateur, mot_de_passe):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM admins WHERE nom_utilisateur = %s", (nom_utilisateur,))
            data = curseur.fetchone()
            if not data:
                raise ValueError("Nom d'utilisateur incorrect")
        admin = Admin(data['id'], data['nom_utilisateur'], data['email'], data['mot_de_passe'])
        if not admin.verifier_mot_de_passe(mot_de_passe):
            raise ValueError("Mot de passe incorrect")
        return admin