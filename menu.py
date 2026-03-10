from admin_repo import AdminRepo
from creneau_repo import CreneauRepo
from groupe_repo import GroupeRepo
from reservation_repo import ReservationRepo
from creneau import Creneau
from groupe import Groupe
from reservation import Reservation
from datetime import datetime
from db_connection import get_cursor
from planning_export import exporter_planning_csv
import re

class Menu:
    """
        Classe qui gère l'interface du menu administratif.
        Chaque méthode correspond à une option du menu et interagit avec
        les repos AdminRepo, CreneauRepo, GroupeRepo, ReservationRepo, 
        pour effectuer les actions demandées par l'utilisateur :
        - Lister, ajouter ou supprimer des créneaux et des groupes.
        - Lister, créer, modifier ou supprimer des réservations.
        - Afficher le planning journalier.
        - Exporter le planning en CSV.
    """
    def __init__(self, admin):
        self.admin = admin

    def afficher_menu(self):
        while True:
            print("\n=== MENU ADMIN ===")
            print("1. Lister les créneaux")
            print("2. Ajouter un créneau")
            print("3. Lister les groupes")
            print("4. Ajouter un groupe")
            print("5. Lister les réservations")
            print("6. Ajouter une réservation")
            print("7. Modifier une réservation")
            print("8. Supprimer une réservation")
            print("9. Planning journalier")
            print("10. Supprimer un créneau")
            print("11. Exporter planning en CSV")
            print("12. Supprimer un groupe")
            print("0. Quitter")
            choix = input("Choisissez une option : ")

            match choix:
                case "1":
                    self.lister_creneaux()
                case "2":
                    self.ajouter_creneau()
                case "3":
                    self.lister_groupes()
                case "4":
                    self.ajouter_groupe()
                case "5":
                    self.lister_reservations()
                case "6":
                    self.ajouter_reservation()
                case "7":
                    self.modifier_reservation()
                case "8":
                    self.supprimer_reservation()
                case "9":
                    self.planning_journalier()
                case "10":
                    self.supprimer_creneau()
                case "11":
                    date = input("Date (YYYY-MM-DD) : ")
                    try:
                        nom_fichier = f"planning_{date}.csv"
                        exporter_planning_csv(date, nom_fichier)
                        print(f"Planning exporté dans {nom_fichier}")
                    except Exception as e:
                        print(f"Erreur lors de l'export : {e}")

                case "12":
                    self.supprimer_groupe()
                case "0":
                    print("Au revoir !")
                    break
                case _:
                    print("Option invalide")


    def lister_creneaux(self, date=None):
        """Affiche tous les créneaux avec leur statut [LIBRE] ou [OCCUPÉ] pour une date donnée."""
        print("\n=== Liste des créneaux ===")
        if date is None:
            date = input("Date (YYYY-MM-DD) (laisser vide = aujourd'hui) : ").strip()

        if date == "":
            date = datetime.today().strftime("%Y-%m-%d")

        creneaux = CreneauRepo.lister_creneaux()
        for c in creneaux:
            reservation = ReservationRepo.get_reservation_par_creneau_et_date(c.id, date)
            if reservation is None:
                print(f"{c.id} | {c.heure_debut} - {c.heure_fin} : [LIBRE]")
            else:
                print(f"{c.id} | {c.heure_debut} - {c.heure_fin} : [OCCUPÉ] "
                      f"Groupe: {reservation['nom']} | Motif: {reservation['motif']} | Responsable: {reservation['responsable']}")


    def ajouter_creneau(self):
        """Permet de créer un nouveau créneau horaire après saisie de l'heure de début et de fin."""
        print("\n=== Ajouter un créneau ===")
        heure_debut = input("Heure début (HH:MM) : ").strip()
        heure_fin = input("Heure fin (HH:MM) : ").strip()
        try:
            c = CreneauRepo.creer_creneau(heure_debut, heure_fin)
            print(f"Créneau créé : {c.heure_debut} - {c.heure_fin}")
        except Exception as e:
            print(f"Erreur : {e}")


    def supprimer_creneau(self):
        """Supprime un créneau existant si celui-ci n'est pas utilisé dans une réservation."""
        self.lister_creneaux()
        try:
            c_id = int(input("ID du créneau à supprimer : "))
        except ValueError:
            print("Erreur : L'ID doit être un nombre.")
            return
        try:
            msg = CreneauRepo.supprimer_creneau(c_id)
            print(msg)
        except Exception as e:
            print(f"Erreur : {e}")


    def ajouter_groupe(self):
        """Permet de créer un nouveau groupe après validation des champs."""
        print("\n=== Ajouter un groupe ===")
        while True:
            nom = input("Nom du groupe : ").strip()
            if not nom:
                print("Erreur : le nom ne peut pas être vide.")
                continue
            if any(char.isdigit() for char in nom):
                print("Erreur : le nom du groupe ne doit pas contenir de chiffres.")
                continue
            break

        while True:
            resp = input("Responsable : ").strip()
            if not resp:
                print("Erreur : le nom du responsable ne peut pas être vide.")
                continue
            if any(char.isdigit() for char in resp):
                print("Erreur : le nom du responsable ne doit pas contenir de chiffres.")
                continue
            break

        while True:
            email = input("Email : ").strip()
            if not email:
                print("Erreur : l'email ne peut pas être vide.")
                continue
            if "@" not in email or "." not in email:
                print("Erreur : format d'email invalide.")
                continue
            break

        try:
            g = GroupeRepo.creer_groupe(nom, resp, email)
            print(f"Groupe créé : {g.nom} (Responsable : {g.responsable})")
        except Exception as e:
            print(f"Erreur : {e}")


    def lister_groupes(self):
        """Affiche tous les groupes enregistrés avec leur responsable et email."""
        groupes = GroupeRepo.lister_groupes()
        print("\n=== Liste des groupes ===")
        for g in groupes:
            print(f"{g.id} | Nom groupe: {g.nom} | Responsable : {g.responsable} | Email : {g.email}")


    def supprimer_groupe(self):
        """Supprime un groupe si celui-ci n'est pas utilisé dans une réservation."""
        print("\n=== Supprimer un groupe ===")
        groupes = GroupeRepo.lister_groupes()
        if not groupes:
            print("Aucun groupe disponible.")
            return

        for g in groupes:
            print(f"{g.id} | Nom groupe: {g.nom} | Responsable : {g.responsable} | Email : {g.email}")

        try:
            groupe_id = int(input("ID du groupe à supprimer : "))
        except ValueError:
            print("Erreur : l'ID doit être un nombre.")
            return

        if groupe_id not in [g.id for g in groupes]:
            print("Erreur : ce groupe n'existe pas.")
            return

        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT COUNT(*) AS nb FROM reservations WHERE groupe_id = %s", (groupe_id,))
            if curseur.fetchone()['nb'] > 0:
                print("Impossible de supprimer ce groupe : il est utilisé dans une réservation.")
                return

        try:
            GroupeRepo.supprimer_groupe(groupe_id)
            print("Groupe supprimé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")
    

    def lister_reservations(self):
        """Affiche la liste des réservations avec date, motif, groupe et créneau."""
        print("\n=== Liste des réservations ===")
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT r.id, r.date, r.motif, g.nom AS groupe, c.heure_debut, c.heure_fin
                   FROM reservations r
                   JOIN groupes g ON r.groupe_id = g.id
                   JOIN creneaux c ON r.creneau_id = c.id
                   ORDER BY r.date"""
            )
            res = curseur.fetchall()
            if not res:
                print("Aucune réservation trouvée.")
                return
            for r in res:
                print(f"{r['id']} | Date: {r['date']} | Motif: {r['motif']} |"
                      f"Groupe: {r['groupe']} | Créneau: {r['heure_debut']}-{r['heure_fin']}")

    def ajouter_reservation(self):
        """Crée une réservation en vérifiant la date, le motif, le groupe et le créneau."""
        print("\n=== Ajouter une réservation ===")
        date_str = input("Date (YYYY-MM-DD) : ").strip()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < datetime.today().date():
                print("Erreur : impossible de réserver une date passée.")
                return
        except ValueError:
            print("Erreur : format de date invalide (YYYY-MM-DD).")
            return

        motif = input("Motif : ").strip()
        if not motif:
            print("Erreur : le motif ne peut pas être vide.")
            return
        if not motif.replace(" ", "").isalpha():
            print("Erreur : le motif contient des caractères non autorisés.")
            return

        self.lister_groupes()
        try:
            groupe_id = int(input("ID du groupe : "))
        except ValueError:
            print("Erreur : l'ID du groupe doit être un nombre.")
            return

        groupes = [g.id for g in GroupeRepo.lister_groupes()]
        if groupe_id not in groupes:
            print("Erreur : ce groupe n'existe pas.")
            return

        self.lister_creneaux()
        print("Vous pouvez choisir un créneau existant ou en créer un nouveau flexible.")
        choix = input("Voulez-vous créer un nouveau créneau ? (o/n) : ").lower()

        if choix == "o":
            heure_debut = input("Heure début (HH:MM) : ").strip()
            heure_fin = input("Heure fin (HH:MM) : ").strip()
            try:
                c = CreneauRepo.creer_creneau(heure_debut, heure_fin)
                creneau_id = c.id
                print(f"Créneau créé : {c.heure_debut} - {c.heure_fin}")
            except Exception as e:
                print(f"Erreur création créneau : {e}")
                return
        elif choix == "n":
            try:
                creneau_id = int(input("ID du créneau : "))
            except ValueError:
                print("Erreur : L'ID du créneau doit être un nombre.")
                return
        else:
            print("Erreur : veuillez répondre uniquement par 'o' ou 'n'.")
            return

        if not ReservationRepo.est_disponible(creneau_id, date_str):
            print("Erreur : ce créneau est déjà réservé pour cette date.")
            return

        try:
            r = ReservationRepo.creer_reservation(date_str, motif, groupe_id, creneau_id)
            print(f"Réservation créée : {r.date} - {r.motif} (Groupe ID {groupe_id})")
        except Exception as e:
            print(f"Erreur lors de la création de la réservation : {e}")


    def modifier_reservation(self):
        """Modifie une réservation existante après vérification de la disponibilité du créneau."""
        print("\n=== Modifier une réservation ===")

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT r.id, r.date, r.motif, g.nom AS groupe, c.heure_debut, c.heure_fin
                FROM reservations r
                JOIN groupes g ON r.groupe_id = g.id
                JOIN creneaux c ON r.creneau_id = c.id
                ORDER BY r.date"""
            )
            reservations = curseur.fetchall()
            if not reservations:
                print("Aucune réservation trouvée.")
                return 

        for r in reservations:
            print(f"{r['id']} : {r['date']} - {r['motif']} "
                f"(Groupe: {r['groupe']}, Créneau: {r['heure_debut']}-{r['heure_fin']})")

        try:
            r_id = int(input("ID de la réservation à modifier : "))
        except ValueError:
            print("Erreur : L'ID doit être un nombre.")
            return

        if not any(r['id'] == r_id for r in reservations):
            print("Erreur : La réservation n'existe pas.")
            return

        date_str = input("Nouvelle date (YYYY-MM-DD) : ").strip()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < datetime.today().date():
                print("Erreur : impossible de choisir une date passée.")
                return
        except ValueError:
            print("Erreur : format de date invalide (YYYY-MM-DD).")
            return

        motif = input("Nouveau motif : ").strip()
        if not motif:
            print("Erreur : le motif ne peut pas être vide.")
            return

        self.lister_groupes()
        try:
            groupe_id = int(input("Nouvel ID de groupe : "))
        except ValueError:
            print("Erreur : L'ID du groupe doit être un nombre.")
            return

        while True:
            self.lister_creneaux(date_str) 
            print("Vous pouvez choisir un créneau existant ou en créer un nouveau flexible.")
            choix = input("Voulez-vous créer un nouveau créneau ? (o/n) : ").lower().strip()
            if choix in ("o", "n"):
                break
            print("Erreur : veuillez saisir 'o' pour oui ou 'n' pour non.")

        if choix == "o":
            heure_debut = input("Heure début (HH:MM) : ").strip()
            heure_fin = input("Heure fin (HH:MM) : ").strip()
            try:
                c = CreneauRepo.creer_creneau(heure_debut, heure_fin)
                creneau_id = c.id
                print(f"Créneau créé : {c.heure_debut} - {c.heure_fin}")
            except Exception as e:
                print(f"Erreur création créneau : {e}")
                return
        else:
            try:
                creneau_id = int(input("ID du créneau : "))
            except ValueError:
                print("Erreur : L'ID du créneau doit être un nombre.")
                return
        try:
            msg = ReservationRepo.modifier_reservation(r_id, date_str, motif, groupe_id, creneau_id)
            print(msg)
        except Exception as e:
            print(f"Erreur : {e}")


    def supprimer_reservation(self):
        """Supprime une réservation existante."""
        print("\n=== Supprimer une réservation ===")
        self.lister_reservations()
        try:
            r_id = int(input("ID de la réservation à supprimer : "))
        except ValueError:
            print("Erreur : L'ID doit être un nombre.")
            return
        try:
            msg = ReservationRepo.supprimer_reservation(r_id)
            print(msg)
        except Exception as e:
            print(f"Erreur : {e}")


    def planning_journalier(self):
        """Affiche le planning journalier d'une date donnée avec l'état des créneaux."""
        date = input("Date (YYYY-MM-DD) : ").strip()
        
        if not date:
            print("Erreur : vous devez saisir une date.")
            return 

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Erreur : format de date invalide (YYYY-MM-DD).")
            return

        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT creneaux.heure_debut,
                        creneaux.heure_fin,
                        reservations.motif,
                        groupes.nom,
                        groupes.responsable
                FROM creneaux
                LEFT JOIN reservations ON creneaux.id = reservations.creneau_id 
                        AND reservations.date = %s
                LEFT JOIN groupes ON reservations.groupe_id = groupes.id
                ORDER BY creneaux.heure_debut""",
                (date,)
            )
            resultats = curseur.fetchall()

        print(f"\n=== Planning du {date} ===")
        for r in resultats:
            if r['nom'] is None:
                print(f"{r['heure_debut']} - {r['heure_fin']} : [LIBRE]")
            else:
                print(f"{r['heure_debut']} - {r['heure_fin']} : [OCCUPÉ] Groupe: {r['nom']}, Motif: {r['motif']}, Responsable: {r['responsable']}")