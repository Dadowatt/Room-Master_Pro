import csv
from reservation import Reservation

def exporter_planning_csv(date, nom_fichier):
    donnees = Reservation.vue_globale(date)
    planning = donnees["planning_complet"]

    with open(nom_fichier, mode="w", newline="", encoding="utf-8") as fichier:
        writer = csv.writer(fichier)

        writer.writerow([
            "Heure début",
            "Heure fin",
            "Statut",
            "Groupe",
            "Motif",
            "Responsable"
        ])

        for p in planning:
            if p["statut"] == "[LIBRE]":
                writer.writerow([
                    p["heure_debut"],
                    p["heure_fin"],
                    p["statut"],
                    "",
                    "",
                    ""
                ])
            else:
                writer.writerow([
                    p["heure_debut"],
                    p["heure_fin"],
                    p["statut"],
                    p["groupe"],
                    p["motif"],
                    p["responsable"]
                ])