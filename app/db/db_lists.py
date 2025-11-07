"""
Module de gestion des listes de classification non-hiérarchiques (DBLists).
Contient les méthodes de lecture pour les tables 'illustrations', 'periodes',
'reliures' et 'localisations'.
"""

import logging
import sqlite3
from typing import List, Tuple
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database

logger = logging.getLogger(__name__)

class DBLists:
    """
    Gère toutes les opérations des Lists:
    Illustrations, Périodes, Reliures, Localisation.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def get_all_illustrations(self) -> List[Tuple[int,str]]:
        """Récupère l'ID et le nom de toutes les illustrations."""
        logger.info("Récupération des illustrations - En cours")
        source_method = 'db_lists.get_all_illustrations'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_ILLUSTRATIONS} ORDER BY nom"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des illustrations - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des illustrations - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur récupération illustrations.",
                exception=e)
            return []

    def get_all_periodes(self) -> List[Tuple[int,str]]:
        """Récupère l'ID et le nom de toutes les périodes."""
        logger.info("Récupération des périodes - En cours")
        source_method = 'db_lists.get_all_periodes'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_PERIODES} ORDER BY nom"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des périodes - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des périodes - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur récupération périodes.",
                exception=e)
            return []

    def get_all_reliures(self) -> List[Tuple[int,str]]:
        """Récupère l'ID et le nom de toutes les reliures."""
        source_method = 'db_lists.get_all_reliures'
        logger.info("Récupération des reliures - En cours")
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_RELIURES} ORDER BY nom"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des reliures - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des reliures - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur récupération reliures.",
                exception=e)
            return []

    def get_all_localisations(self) -> List[Tuple[int,str]]:
        """Récupère l'ID et le nom de toutes les localisations."""
        source_method = 'db_lists.get_all_localisations'
        logger.info("Récupération des localisations - En cours")
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_LOCALISATIONS} ORDER BY nom"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des localisations - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des localisations - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur récupération localisations.",
                exception=e)
            return []