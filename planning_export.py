import csv
from reservation_repo import ReservationRepo

def exporter_planning_csv(date, nom_fichier):
    """
    Exporte le planning d'une date donnée dans un fichier CSV.
    La fonction récupère tous les créneaux et les réservations pour la date,
    puis écrit un fichier CSV listant chaque créneau avec son statut 
    ([LIBRE] ou [OCCUPÉ]) ainsi que le groupe, le motif et le responsable si occupé.
    """
    creneaux = ReservationRepo.get_creneaux_et_reservations(date)
    
    with open(nom_fichier, mode="w", newline="", encoding="utf-8") as fichier:
        writer = csv.writer(fichier, delimiter=',')
        
        # Écriture de l'entête
        writer.writerow([
            "Heure début",
            "Heure fin",
            "Statut",
            "Groupe",
            "Motif",
            "Responsable"
        ])
        
        # Écriture du planning
        for c in creneaux:
            debut = c['heure_debut'][:5]
            fin = c['heure_fin'][:5]
            
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