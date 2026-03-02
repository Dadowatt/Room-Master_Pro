from db_connection import get_cursor
from groupe import Groupe

class GroupeRepo:
    @staticmethod
    def lister_groupes():
        groupes = []
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM groupes")
            for r in curseur.fetchall():
                groupes.append(Groupe(r['id'], r['nom'], r['responsable'], r['email']))
        return groupes

    @staticmethod
    def creer_groupe(nom, responsable, email):
        if nom == "" or responsable == "" or email == "":
            raise ValueError("Tous les champs sont obligatoires")

        for lettre in nom:
            if lettre.isdigit():
                raise ValueError("Le nom du groupe ne doit pas contenir de chiffres")

        for lettre in responsable:
            if lettre.isdigit():
                raise ValueError("Le nom du responsable ne doit pas contenir de chiffres")

        if "@" not in email or "." not in email:
            raise ValueError("Email invalide")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "INSERT INTO groupes (nom, responsable, email) VALUES (%s, %s, %s)",
                (nom, responsable, email)
            )
            id_groupe = curseur.lastrowid

        return Groupe(id_groupe, nom, responsable, email)