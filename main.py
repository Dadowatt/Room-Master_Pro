from admin_repo import AdminRepo
from menu import Menu
from db_connection import get_cursor

def setup_initial_admin():
    """Vérifie si au moins un admin existe, sinon en crée un."""
    with get_cursor(dictionary=True) as curseur:
        curseur.execute("SELECT COUNT(*) as nb FROM admins")
        resultat = curseur.fetchone()

    if resultat['nb'] == 0:
        print("Aucun admin trouvé. Créer un nouveau compte")
        nom = input("Nom utilisateur : ")
        email = input("Email : ")
        mdp = input("Mot de passe : ")
        mdp_conf = input("Confirmer mot de passe : ")
        try:
            admin = AdminRepo.creer_admin(nom, email, mdp, mdp_conf)
            print(f"Compte admin {admin.nom_utilisateur} créé avec succès !")
            return admin
        except ValueError as e:
            print(f"Erreur lors de la création de l'admin : {e}")
            return setup_initial_admin() 
    else:
        print("Admin trouvé. Connexion requise.")
        return None  

def login_admin():
    print("=== Connexion Admin ===")
    nom_utilisateur = input("Nom utilisateur : ")
    mot_de_passe = input("Mot de passe : ")
    try:
        admin = AdminRepo.login(nom_utilisateur, mot_de_passe)
        print(f"Bienvenue {admin.nom_utilisateur} !")
        return admin
    except ValueError as e:
        print(f"Erreur : {e}")
        return None

if __name__ == "__main__":
    setup_initial_admin() 
    admin = None
    while admin is None:
        admin = login_admin()
    Menu(admin).afficher_menu()