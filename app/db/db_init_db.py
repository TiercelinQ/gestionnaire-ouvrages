"""
Module de gestion de création de la base de données de l'application (DBInitDataBase).
Gère la création des tables: Iillustrations, Categories, Genres,
Sous-Genres, Periodes, Reliures, Localisations Users, Ouvrages
et Logs dans la base de données.
"""

import logging
import sqlite3
from app.utils import log_error_connection_database
from app.data_models import DBSchema

logger = logging.getLogger(__name__)

class DBInitDataBase:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def initialize_db(self):
        """Exécute tous les schémas SQL pour créer les tables si elles n'existent pas."""
        source_method = "db_manager._initialize_db"
        logger.info("Initialisation / Vérification de la base de données - En cours")
        if self.db_manager.connexion and self.db_manager.cursor:
            for schema in DBSchema.ALL_SCHEMAS:
                try:
                    self.db_manager.cursor.execute(schema)
                except sqlite3.Error as e:
                    log_error_connection_database(self.parent_widget, source_method)
            self.db_manager.connexion.commit()
            logger.info("Initialisation / Vérification de la base de données - Succès")
        else:
            logger.critical("Initialisation / Vérification de la base de données - Echec")
