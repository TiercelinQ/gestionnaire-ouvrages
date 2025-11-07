"""
Module de gestion du journal d'activité (DBLoggers).
Contient les méthodes pour l'insertion, la lecture et le filtrage des entrées
de logs stockées dans la table 'logs' de la base de données.
"""

import sqlite3
import logging
from typing import List, Tuple, Optional
from app.utils import log_event, log_error_connection_database

logger = logging.getLogger(__name__)

class DBLoggers:
    """
    Gère toutes les opérations des Logs.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def get_activity_log(self, filters: Optional[dict] = None) -> List[Tuple]:
        """
        Récupère les entrées de logs, en appliquant des filtres optionnels, et en joignant le nom de l'utilisateur.

        :param filters: Dictionnaire de filtres (ex: {'level': 'ERROR', 'source_module': 'DBManager'})
        """
        logger.info("Récupération des logs - En cours")
        source_method = 'db_logs.get_activity_log'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        sql = """
        SELECT
            l.id, l.timestamp, l.level, l.source_module, l.error_type, l.message, u.system_name
        FROM
            logs l
        LEFT JOIN
            users u ON l.user_id = u.id
        """
        where_clauses = []
        params = {}
        if filters:
            for column, value in filters.items():
                if value and column in ['level', 'source_module', 'error_type']:
                    where_clauses.append(f"l.{column} = :{column}")
                    params[column] = value
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY l.timestamp DESC;"

        try:
            self.db_manager.cursor.execute(sql, params)
            logger.info("Récupération des logs - Succès")
            return self.db_manager.cursor.fetchall()
        except sqlite3.Error as e:
            logger.info("Récupération des logs - Echec")
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur chargement log avec filtres: {e}",
                exception=e)
            return []

    def get_distinct_log_values(self, column_name: str) -> List[str]:
        """
        Récupère toutes les valeurs distinctes pour une colonne donnée dans la table 'log'.
        """
        logger.info("Récupération des valeurs distincts des logs - En cours")
        source_method = 'db_logs.get_distinct_log_values'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        if column_name not in ['level', 'source_module', 'error_type']:
            return []

        sql = f"SELECT DISTINCT {column_name} FROM logs ORDER BY {column_name} ASC;"

        try:
            self.db_manager.cursor.execute(sql)
            logger.info("Récupération des valeurs distincts des logs - Succès")
            return [row[0] for row in self.db_manager.cursor.fetchall() if row[0] is not None and row[0] != '']
        except sqlite3.Error as e:
            logger.info("Récupération des valeurs distincts des logs - Echec")
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération valeurs distinctes pour {column_name}",
                exception=e)
            return []
