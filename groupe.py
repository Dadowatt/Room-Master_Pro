from db_connection import get_cursor

class Groupe:
    def __init__(self, id, nom, responsable, email, telephone):
        self.id = id
        self.nom = nom
        self.responsable = responsable
        self.email = email
        self.telephone = telephone
        
    @classmethod
    def lister_groupe(cls):
        liste_groupes = []

        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM groupes")
            resultats = curseur.fetchall()
        for r in resultats:
            groupe = cls(r['id'], r['nom'], r['responsable'], r['email'], r['telephone'])
            liste_groupes.append(groupe)
        return liste_groupes
    
    @classmethod
    def creer_groupe(cls, nom, responsable, email, telephone):
        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT id FROM groupes WHERE email = %s",(email))
            if curseur.fetchone() is not None:
                raise ValueError("cet email est déjà utilisé pour un autre groupe")
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                "INSERT INTO groupes (nom, responsable, email, telephone) VALUES (%s, %s, %s, %s)",
                (nom, responsable, email, telephone)
            )
            id_groupe = curseur.lastrowid
        return cls(id_groupe, nom, responsable, email, telephone)
