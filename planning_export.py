import csv
from reservation_repo import ReservationRepo
from datetime import timedelta
from openpyxl import Workbook


def format_heure(h):
    if isinstance(h, timedelta):
        total_seconds = int(h.total_seconds())
        heures = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{heures:02d}:{minutes:02d}"
    else:
        return str(h)[:5]


def exporter_planning_csv(date, nom_fichier):
    """
    Exporte le planning d'une date donnée dans un fichier CSV.
    La fonction récupère tous les créneaux et les réservations pour la date,
    puis écrit un fichier CSV listant chaque créneau avec son statut 
    ([LIBRE] ou [OCCUPÉ]) ainsi que le groupe, le motif et le responsable si occupé.
    un fichier Excel (.xlsx) est également généré automatiquement
    avec le même contenu, pour une visualisation plus pratique dans Excel.
    """
    creneaux = ReservationRepo.get_creneaux_et_reservations(date)
    
    with open(nom_fichier, mode="w", newline="", encoding="utf-8") as fichier:
        writer = csv.writer(fichier, delimiter=',')
        
        writer.writerow([
            "Heure début",
            "Heure fin",
            "Statut",
            "Groupe",
            "Motif",
            "Responsable"
        ])
        
        for c in creneaux:
            debut = format_heure(c['heure_debut'])
            fin = format_heure(c['heure_fin'])

            if c['nom'] is None:
                writer.writerow([debut, fin, "LIBRE", "-", "-", "-"])
            else:
                writer.writerow([
                    debut,
                    fin,
                    "OCCUPÉ",
                    c['nom'],
                    c['motif'],
                    c['responsable']
                ])

    print(f"Planning exporté avec succès dans {nom_fichier}")

    # -------- EXCEL BONUS --------
    nom_excel = nom_fichier.replace(".csv", ".xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Planning"

    ws.append(["Heure début","Heure fin","Statut","Groupe","Motif","Responsable"])

    for c in creneaux:

        debut = format_heure(c['heure_debut'])
        fin = format_heure(c['heure_fin'])

        if c['nom'] is None:
            ws.append([debut, fin, "LIBRE", "-", "-", "-"])
        else:
            ws.append([
                debut,
                fin,
                "OCCUPÉ",
                c['nom'],
                c['motif'],
                c['responsable']
            ])

    wb.save(nom_excel)

    print(f"(Bonus) Planning aussi exporté en Excel : {nom_excel}")
    