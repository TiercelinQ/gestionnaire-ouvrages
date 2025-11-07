"""
Module de gestion de création d'un jeu de données initial (DBInitData).
Gère l'insertion des données des tables: Illustrations, Périodes, Relires, Localisations
dans la base de données.
"""
import logging
import sqlite3
from app.utils import log_event, log_error_connection_database
from app.data_models import DBSchema

logger = logging.getLogger(__name__)

class DBInitData:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def insert_initial_data(self) -> None:
        """
        Insère les données de base (Illustration, Période, Reliure, Localisations)
        si la base de données est vide.
        """
        logger.info("Initialisation / Vérification des données initales - En cours")
        source_method = 'db_manager._insert_initial_data'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return

        initial_data = {
            DBSchema.TABLE_ILLUSTRATIONS: [
                "Aucune", "Visuel(s) N&B", "Visuel(s) Couleurs", "Visuel(s) N&B et Couleurs"
            ],
            DBSchema.TABLE_PERIODES: [
                "1re Guerre Mondiale", "2e Guerre Mondiale", "Antiquité",
                "Classique", "Contemporain", "Guerres Coloniales",
                "Guerres d'Israël", "Moyen-Âge", "Préhistoire",
                "Renaissance", "Révolution / 1er Empire"
            ],
            DBSchema.TABLE_RELIURES: [
                "À Oeillets", "À Vis", "Agrafée",
                "En Spirale", "Dos Carré Collé", "Dos Carré Collé à Rabat",
                "Dos Carré Collé en Coffret", "Dos Carré Collé sous Jaquette",
                "Dos Cousu", "Dos Cousu en Coffret", "Dos Cousu sous Jaquette"
            ],
            DBSchema.TABLE_LOCALISATIONS: [
                "Salon", "Salle à manger", "Bureau", "Cabinet de curiosités", "Chambre"
            ]
        }
        try:
            for table, values in initial_data.items():
                self._insert_if_empty(table, values)
            self.db_manager.connexion.commit()
            logger.info("Initialisation / Vérification des données initales - Succès")
        except sqlite3.Error as e:
            logger.error("Initialisation / Vérification des données initales - Echec - %s - Erreur: %s",source_method,str(e),exc_info=True)
            if self.db_manager.connexion:
                self.db_manager.connexion.rollback()
            log_event(
                db_manager=self,
                level='ERROR',
                source=source_method,
                message="Erreur insertion données initiales.",
                exception=e
            )

    def _insert_if_empty(self, table: str, values: list[str]) -> None:
        """
        Insère les valeurs données dans une table si elle est vide.
        """
        logger.info("Insertion / Vérification des données de la table %s - En Cours",table)
        self.db_manager.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        if self.db_manager.cursor.fetchone()[0] == 0:
            self.db_manager.cursor.executemany(
                f"INSERT INTO {table} (nom) VALUES (?)",
                [(v,) for v in values]
            )
        logger.info("Insertion / Vérification des données de la table %s - Terminée",table)
