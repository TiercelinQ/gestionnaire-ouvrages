"""
Module de gestion des utilisateurs (DBUsers).
Gère l'identification de l'utilisateur système et assure la persistance
(création ou récupération) de son enregistrement dans la table 'users' de la BDD.
"""

import os
import sqlite3
import logging
from typing import Optional
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database, get_datetime

logger = logging.getLogger(__name__)

class DBUsers:
    """
    Gère toutes les opérations des Lists:
    Illustrations, Périodes, Reliures, Localisation.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def get_system_user_name(self) -> str:
        """Tente de récupérer le nom de l'utilisateur du système."""
        try:
            return os.getlogin()
        except Exception:
            return os.environ.get('USERNAME') or os.environ.get('USER') or "Default_User"

    def get_system_user_id(self) -> int:
        """
        Récupère l'ID de l'utilisateur système ou le crée s'il n'existe pas.
        Doit être appelé après l'établissement de la connexion.
        :return: L'ID de l'utilisateur ou 0 si la connexion n'est pas établie.
        """
        current_id = self.db_manager.current_user_id
        if current_id is None and self.db_manager.connexion:
            user_id = self._get_or_create_user(self.get_system_user_name())
            self.db_manager.current_user_id = user_id
            return user_id if user_id is not None else 0
        return current_id if current_id is not None else 0

    def _get_or_create_user(self, system_name: str) -> Optional[int]:
        """
        Cherche un utilisateur par nom; le crée si non trouvé.
        :param system_name: Nom de l'utilisateur à chercher ou créer.
        :return: L'ID de l'utilisateur ou None en cas d'erreur.
        """
        logger.info("Récupération ou création de l'utilisateur %s - En cours",system_name)
        source_method = 'db_users._get_or_create_user'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            user_name = system_name
            self.db_manager.cursor.execute(f"SELECT id FROM {DBSchema.TABLE_USERS} WHERE system_name = ?", (system_name,))
            user = self.db_manager.cursor.fetchone()
            if user:
                logger.info("Récupération ou création de l'utilisateur %s - Succès",system_name)
                return user[0]
            else:
                now = get_datetime()
                sql = f"""
                INSERT INTO {DBSchema.TABLE_USERS} (system_name, user_name, date_creation)
                VALUES (?, ?, ?)
                """
                self.db_manager.cursor.execute(sql, (system_name, user_name, now))
                new_id = self.db_manager.cursor.lastrowid
                self.db_manager.connexion.commit()
                logger.info("Récupération ou création de l'utilisateur %s - Succès",system_name)
                return new_id
        except sqlite3.Error as e:
            logger.info("Récupération ou création de l'utilisateur %s - Echec",system_name)
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération/création utilisateur '{system_name}'.",
                exception=e)
            return None

    def update_user_name(self, user_name: str):
        """
        Mise à jour du nom de l'utilisateur dans la base de donnée.
        :param nom: Nom de l'utilisateur à modifier.
        """
        logger.info("Mise à jour de l'utilisateur %s - En cours",user_name)
        source_method = 'db_users.update_user_name'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            user_id = self.db_manager.current_user_id
            if user_id is None:
                log_event(
                    db_manager=self.db_manager,
                    level='ERROR',
                    source=source_method,
                    message=f"Erreur aucun utilisateur existe '{user_name}'.")
                return False
            sql = f"UPDATE {DBSchema.TABLE_USERS} SET user_name = ? WHERE id = ?"
            self.db_manager.cursor.execute(sql, (user_name, user_id))
            self.db_manager.connexion.commit()
            logger.info("Mise à jour de l'utilisateur %s - Succès",user_name)
            return True
        except sqlite3.Error as e:
            logger.info("Mise à jour de l'utilisateur %s - Echec",user_name)
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur mise à jour utilisateur '{user_name}'.",
                exception=e)
            return False