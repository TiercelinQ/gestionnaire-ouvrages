"""
Module de gestion des exportations de données (DBExporter).
Contient la logique d'extraction et d'exportation de l'ensemble
des données d'ouvrages (y compris les classifications) vers un fichier CSV.
"""

import csv
import sqlite3
import logging
from typing import Tuple
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database

logger = logging.getLogger(__name__)

class DBExporter:
    """
    Gère toutes les opérations d'exportation de données.
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def export_all_ouvrages_to_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        Exporte toutes les données de la table des ouvrages, y compris les noms des classifications
        associées, vers un fichier CSV.
        """
        logger.info("Export des ouvrages en CSV - En cours")
        source_method = 'db_export.db_export.export_all_ouvrages_to_csv'

        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return False, "Connexion BDD non établie."

        sql = f"""
        SELECT
            o.id AS 'ID',
            o.titre AS 'Titre',
            o.sous_titre AS 'Sous-Titre',
            o.auteur AS 'Auteur',
            o.auteur_2 AS 'Auteur 2',
            o.titre_original AS 'Titre Original',
            o.cycle AS 'Cycle',
            o.tome AS 'tome',
            i.nom AS 'Illustration',
            c.nom AS 'Catégorie',
            g.nom AS 'Genre',
            sg.nom AS 'Sous-Genre',
            p.nom AS 'Periode',
            o.edition AS 'Edition',
            o.collection AS 'Collection',
            o.edition_annee AS 'Année Edition',
            o.edition_numero AS 'Numéro Edition',
            o.edition_premiere_annee AS 'Année Première Edition',
            o.isbn AS 'ISBN',
            r.nom AS 'Reliure',
            o.nombre_page AS 'Nombre Page',
            o.dimension AS 'Dimension',
            l.nom AS 'Localisation',
            o.resume AS 'Résumé',
            o.remarques AS 'Remarques',
            o.couverture_premiere_chemin AS 'Première Couverture Chemin',
            o.couverture_premiere_emplacement AS 'Première Couverture Emplacement',
            o.couverture_quatrieme_chemin AS 'Quatrième Couverture Chemin',
            o.couverture_quatrieme_emplacement AS 'Quatrième Couverture Emplacement'
        FROM {DBSchema.TABLE_OUVRAGES} o
        LEFT JOIN {DBSchema.TABLE_ILLUSTRATIONS} i ON o.id_illustration = i.id
        LEFT JOIN {DBSchema.TABLE_CATEGORIES} c ON o.id_categorie = c.id
        LEFT JOIN {DBSchema.TABLE_GENRES} g ON o.id_genre = g.id
        LEFT JOIN {DBSchema.TABLE_SOUS_GENRES} sg ON o.id_sous_genre = sg.id
        LEFT JOIN {DBSchema.TABLE_PERIODES} p ON o.id_periode = p.id
        LEFT JOIN {DBSchema.TABLE_RELIURES} r ON o.id_reliure = r.id
        LEFT JOIN {DBSchema.TABLE_LOCALISATIONS} l ON o.id_localisation = l.id
        ORDER BY o.titre, o.auteur
        """
        try:
            self.db_manager.cursor.execute(sql)
            rows = self.db_manager.cursor.fetchall()
            column_headers = [description[0] for description in self.db_manager.cursor.description]
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=';')
                csv_writer.writerow(column_headers)
                csv_writer.writerows(rows)
            sucess_msg = f"Exportation réussie de {len(rows)} ouvrages vers :\n{file_path}"
            logger.info("Export des ouvrages en CSV - Succès")
            return True, sucess_msg
        except Exception as e:
            logger.info("Export des ouvrages en CSV - Echec")
            error_msg = f"Échec de l'exportation CSV : {e}"
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur export CSV.",
                exception=e)
            return False, error_msg