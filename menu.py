from admin_repo import AdminRepo
from creneau_repo import CreneauRepo
from groupe_repo import GroupeRepo
from reservation_repo import ReservationRepo
from creneau import Creneau
from groupe import Groupe
from reservation import Reservation
from datetime import datetime
from db_connection import get_cursor

class Menu:
    def __init__(self, admin):
        self.admin = admin

    def afficher_menu(self):
        while True:
            print("\n--- MENU ADMIN ---")
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
            print("0. Quitter")
            choix = input("Choisissez une option : ")

            if choix == "0":
                print("Au revoir !")
                break
            elif choix == "1":
                self.lister_creneaux()
            elif choix == "2":
                self.ajouter_creneau()
            elif choix == "3":
                self.lister_groupes()
            elif choix == "4":
                self.ajouter_groupe()
            elif choix == "5":
                self.lister_reservations()
            elif choix == "6":
                self.ajouter_reservation()
            elif choix == "7":
                self.modifier_reservation()
            elif choix == "8":
                self.supprimer_reservation()
            elif choix == "9":
                self.planning_journalier()
            elif choix == "10":
                self.supprimer_creneau()
            else:
                print("Option invalide")

    # --- Créneaux ---
    def lister_creneaux(self):
        print("\n--- Liste des créneaux ---")

        date = input("Date (YYYY-MM-DD) (laisser vide = aujourd'hui) : ")

        if not date:
            date = datetime.today().strftime("%Y-%m-%d")

        creneaux = CreneauRepo.lister_creneaux()

        for c in creneaux:
            reservation = ReservationRepo.get_reservation_par_creneau_et_date(c.id, date)

            if reservation is None:
                print(f"{c.id} | {c.heure_debut} - {c.heure_fin} : [LIBRE]")
            else:
                print(
                    f"{c.id} | {c.heure_debut} - {c.heure_fin} : [OCCUPÉ] "
                    f"Groupe: {reservation['nom']} | "
                    f"Motif: {reservation['motif']} | "
                    f"Responsable: {reservation['responsable']}"
                )

    def ajouter_creneau(self):
        print("\n--- Ajouter un créneau ---")
        debut = input("Heure de début (HH:MM) : ")
        fin = input("Heure de fin (HH:MM) : ")
        try:
            c = CreneauRepo.creer_creneau(debut, fin)
            print(f"Créneau créé : {c.heure_debut} - {c.heure_fin}")
        except Exception as e:
            print(f"Erreur : {e}")

    def supprimer_creneau(self):
        self.lister_creneaux()
        c_id = input("ID du créneau à supprimer : ")
        try:
            msg = CreneauRepo.supprimer_creneau(int(c_id))
            print(msg)
        except Exception as e:
            print(f"Erreur : {e}")

    # --- Groupes ---
    def lister_groupes(self):
        groupes = GroupeRepo.lister_groupes()
        print("\n--- Liste des groupes ---")
        for g in groupes:
            print(f"{g.id} : {g.nom} - Responsable : {g.responsable} - Email : {g.email}")

    def ajouter_groupe(self):
        print("\n--- Ajouter un groupe ---")
        nom = input("Nom du groupe : ")
        resp = input("Responsable : ")
        email = input("Email : ")
        try:
            g = GroupeRepo.creer_groupe(nom, resp, email)
            print(f"Groupe créé : {g.nom} (Responsable : {g.responsable})")
        except Exception as e:
            print(f"Erreur : {e}")

    # --- Réservations ---
    def lister_reservations(self):
        print("\n--- Liste des réservations ---")
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
                print(f"{r['id']} : {r['date']} - {r['motif']} (Groupe: {r['groupe']}, Créneau: {r['heure_debut']}-{r['heure_fin']})")

    def ajouter_reservation(self):
        print("\n--- Ajouter une réservation ---")
        date = input("Date (YYYY-MM-DD) : ")
        motif = input("Motif : ")
        self.lister_groupes()
        groupe_id = int(input("ID du groupe : "))
        self.lister_creneaux()
        creneau_id = int(input("ID du créneau : "))
        try:
            r = ReservationRepo.creer_reservation(date, motif, groupe_id, creneau_id)
            print(f"Réservation créée : {r.date} - {r.motif}")
        except Exception as e:
            print(f"Erreur : {e}")

    def modifier_reservation(self):
        try:
            r_id = int(input("ID de la réservation à modifier : "))
        except ValueError:
            print("Erreur : L'ID de la réservation doit être un nombre.")
            return

        with get_cursor(dictionary=True) as curseur:
            curseur.execute("SELECT * FROM reservations WHERE id=%s", (r_id,))
            if not curseur.fetchone():
                print("Erreur : La réservation n'existe pas.")
                return

        date_str = input("Nouvelle date (YYYY-MM-DD) : ")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < datetime.today().date():
                print("Erreur : Impossible de choisir une date passée.")
                return
        except ValueError:
            print("Erreur : Format de date invalide (YYYY-MM-DD).")
            return

        motif = input("Nouveau motif : ").strip()
        if not motif:
            print("Erreur : Le motif ne peut pas être vide.")
            return

        self.lister_groupes()
        try:
            groupe_id = int(input("Nouvel ID de groupe : "))
        except ValueError:
            print("Erreur : L'ID du groupe doit être un nombre.")
            return

        self.lister_creneaux()
        try:
            creneau_id = int(input("Nouvel ID de créneau : "))
        except ValueError:
            print("Erreur : L'ID du créneau doit être un nombre.")
            return

        try:
            msg = ReservationRepo.modifier_reservation(r_id, date_str, motif, groupe_id, creneau_id)
            print(msg)
        except Exception as e:
            print(f"Erreur : {e}")

    # --- Planning journalier ---
    def planning_journalier(self):
        date = input("Date (YYYY-MM-DD) : ")
        planning = []
        with get_cursor(dictionary=True) as curseur:
            curseur.execute(
                """SELECT creneaux.heure_debut, creneaux.heure_fin, reservations.motif, groupes.nom, groupes.responsable
                   FROM creneaux
                   LEFT JOIN reservations ON creneaux.id = reservations.creneau_id AND reservations.date = %s
                   LEFT JOIN groupes ON reservations.groupe_id = groupes.id
                   ORDER BY creneaux.heure_debut""",
                (date,)
            )
            resultats = curseur.fetchall()
        print(f"\n--- Planning du {date} ---")
        for r in resultats:
            if r['nom'] is None:
                print(f"{r['heure_debut']} - {r['heure_fin']} : [LIBRE]")
            else:
                print(f"{r['heure_debut']} - {r['heure_fin']} : [Occupé] Groupe: {r['nom']}, Motif: {r['motif']}, Responsable: {r['responsable']}")