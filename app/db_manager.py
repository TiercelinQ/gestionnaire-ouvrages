# pylint: disable=no-name-in-module
"""
Gestionnaire principal de la base de données (DBManager).
Initialise la connexion SQLite, crée le schéma BDD et sert de façade pour
toutes les opérations (CRUD sur les ouvrages, gestion des listes, logs, etc.)
en déléguant aux modules spécialisés.
"""

import os
import sqlite3
import logging
from typing import Optional, Any, Dict, Tuple, List
from PyQt6.QtWidgets import QWidget
from app.utils import log_error_connection_database, is_cloud_path
from app.db.db_init_db import DBInitDataBase
from app.db.db_init_data import DBInitData
from app.db.db_classifications import DBClassifications
from app.db.db_export import DBExporter
from app.db.db_import import DBImporter
from app.db.db_lists import DBLists
from app.db.db_logs import DBLoggers
from app.db.db_ouvrages import DBOuvrages
from app.db.db_users import DBUsers

logger = logging.getLogger(__name__)

class DBManager:
    """
    Gestionnaire de la connexion et des opérations avec la base de données SQLite.
    Centralise la logique d'accès aux données, de manipulation du schéma et l'audit.
    """
    def __init__(self, parent_widget: QWidget):
        self.parent_widget = parent_widget
        self.db_path: Optional[str] = None
        self.connexion: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.current_user_id: Optional[int] = None

        # --- Initialisation des gestionnaires spécialisés (Délégation) ---
        # 'self est en paramètre pour que les modules aient accès aux méthodes de DBManager
        self.init_db = DBInitDataBase(self)
        self.init_data = DBInitData(self)
        self.classification = DBClassifications(self)
        self.exporter = DBExporter(self)
        self.importer = DBImporter(self)
        self.lists = DBLists(self)
        self.logger = DBLoggers(self)
        self.ouvrages = DBOuvrages(self)
        self.users = DBUsers(self)

    # --------------------------------------------------
    # GESTION CONNEXION DATABASE
    # --------------------------------------------------

    def connect_db(self, db_path: str, parent_widget: QWidget = None) -> bool:
        """
        Établit la connexion à la base de données et initialise le schéma si nécessaire.
        Si la base de données est stockée en local, alors PRAGMA journal_mode=WAL
        Si la base de données est stockée dans un Cloud, alors PRAGMA journal_mode=DELETE
        :param db_path: Chemin complet du fichier SQLite.
        :param parent_widget: Widget parent pour l'affichage des messages d'erreur.
        :return: True si la connexion et l'initialisation réussissent, False sinon.
        """
        logger.info("Connexion Base de Données - En cours")
        self.db_path = db_path
        source_method = "db_manager.connect_db"
        try:
            self.connexion = sqlite3.connect(self.db_path, timeout=10)
            self.connexion.row_factory = sqlite3.Row
            self.cursor = self.connexion.cursor()

            if is_cloud_path(db_path):
                logger.warning("Base de données détectée sur un service cloud : WAL désactivé")
                self.cursor.execute("PRAGMA journal_mode=DELETE;")
            else:
                try:
                    logger.info("Base de données locale détectée : tentative WAL")
                    self.cursor.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.OperationalError:
                    logger.warning("WAL non supporté, bascule en DELETE")
                    self.cursor.execute("PRAGMA journal_mode=DELETE;")

            self.connexion.commit()
            self._initialize_db()
            self._initialize_data()
            logger.info("Connexion Base de Données - Succès")
            return True
        except sqlite3.Error as e:
            logger.info("Connexion Base de Données - Echec")
            logger.critical("%s - Erreur: %s.",source_method,str(e),exc_info=True)
            if parent_widget:
                log_error_connection_database(parent_widget, source_method)
            self.connexion = None
            self.cursor = None
            self.db_path = None
            return False

    def close_db(self):
        """Ferme la connexion à la base de données si elle est ouverte."""
        logger.info("Déconnexion Base de Données - En cours")
        if self.connexion:
            self.connexion.close()
            self.connexion = None
            self.cursor = None
            logger.info("Déconnexion Base de Données - Succès")

    # --------------------------------------------------
    # METHODES DE DELEGATION
    # --------------------------------------------------

    # --- Gestion de la base de données à l'initialisation ---
    def _initialize_db(self):
        """Exécute tous les schémas SQL pour créer les tables si elles n'existent pas."""
        return self.init_db.initialize_db()
    def _initialize_data(self):
        """Exécute tous les schémas SQL pour créer les tables si elles n'existent pas."""
        return self.init_data.insert_initial_data()

    # --- Gestion des utilisateurs ---
    def get_system_user_name(self) -> str:
        """
        Récupère le nom d'utilisateur du système d'exploitation actuel.
        Cette méthode est un proxy vers DBUsers.
        """
        return self.users.get_system_user_name()
    def get_system_user_id(self) -> int:
        """
        Récupère l'ID de l'utilisateur système dans la base de données.
        Cette méthode est un proxy vers DBUsers.
        """
        return self.users.get_system_user_id()
    def update_user_name(self, user_name: str):
        """
        Met à jour le nom de l'utilisateur système dans la base de données.
        Cette méthode est un proxy vers DBUsers.
        """
        return self.users.update_user_name(user_name)

    # --- Gestion de la classification ---
    def get_all_categories(self) -> List[Tuple[int, str]]:
        """
        Récupère toutes les catégories de la base de données.
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.get_all_categories()
    def get_genres_by_category_id(self, category_id: int) -> List[Tuple[int, str]]:
        """
        Récupère tous les genres associés à un ID de catégorie spécifique.
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.get_genres_by_category_id(category_id)
    def get_subgenres_by_genre_id(self, genre_id: int) -> List[Tuple[int, str]]:
        """
        Récupère tous les sous-genres associés à un ID de genre spécifique.
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.get_subgenres_by_genre_id(genre_id)
    def add_classification_item(self, table_name: str, nom: str, parent_id: Optional[int] = None) -> Optional[int]:
        """
        Ajoute un nouvel élément de classification (Catégorie, Genre ou Sous-genre) à une table.
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.add_classification_item(table_name, nom, parent_id)
    def update_classification_item(self, table_name: str, item_id: int, nom: str) -> bool:
        """
        Modifie le nom d'un élément de classification existant dans la table.
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.update_classification_item(table_name, item_id, nom)
    def delete_classification_item(self, table_name: str, item_id: int) -> bool:
        """
        Supprime un élément de classification (et les références associées dans 'ouvrages').
        Cette méthode est un proxy vers DBClassifications.
        """
        return self.classification.delete_classification_item(table_name, item_id)

    # --- Gestion des listes (Illustrations, Périodes, Reliures, Localisaion) ---
    def get_all_illustrations(self) -> List[Tuple[int,str]]:
        """
        Récupère toutes les options d'illustrations (id, nom) de la base de données.
        Cette méthode est un proxy vers DBLists.
        """
        return self.lists.get_all_illustrations()
    def get_all_periodes(self) -> List[Tuple[int,str]]:
        """
        Récupère toutes les périodes (id, nom) de la base de données.
        Cette méthode est un proxy vers DBLists.
        """
        return self.lists.get_all_periodes()
    def get_all_reliures(self) -> List[Tuple[int,str]]:
        """
        Récupère toutes les options de reliures (id, nom) de la base de données.
        Cette méthode est un proxy vers DBLists.
        """
        return self.lists.get_all_reliures()
    def get_all_localisations(self) -> List[Tuple[int,str]]:
        """
        Récupère toutes les localisations (id, nom) de la base de données.
        Cette méthode est un proxy vers DBLists.
        """
        return self.lists.get_all_localisations()

    # ---  Gestion des ouvrages ---
    def get_all_ouvrages(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les ouvrages de la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.get_all_ouvrages()
    def get_total_ouvrage_count(self) -> int:
        """
        Récupère le nombre total d'ouvrages de la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.get_total_ouvrage_count()
    def get_ouvrage_details(self, ouvrage_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère toutes données liées à un ouvrage de la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.get_ouvrage_details(ouvrage_id)
    def add_ouvrage(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Ajoute un ouvrage dans la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.add_ouvrage(data)
    def update_ouvrage(self, ouvrage_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Mets à jour un ouvrage dans la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.update_ouvrage(ouvrage_id, data)
    def delete_ouvrage(self, ouvrage_id: int) -> Tuple[bool, str]:
        """
        Supprime un ouvrage dans la base de données.
        Cette méthode est un proxy vers DBOuvrages.
        """
        return self.ouvrages.delete_ouvrage(ouvrage_id)

    # --- Gestion du journal d'activité ---
    def get_activity_log(self, filters: Optional[dict] = None) -> List[Tuple]:
        """
        Récupère les entrées du journal d'activité (logs) de la base de données.
        Cette méthode est un proxy vers DBLoggers.
        """
        return self.logger.get_activity_log(filters)
    def get_distinct_log_values(self, column_name: str) -> List[str]:
        """
        Récupère les valeurs distinctes d'une colonne spécifique dans la table des logs.
        Utilisé pour peupler les filtres de l'interface utilisateur.
        Cette méthode est un proxy vers DBLoggers.
        """
        return self.logger.get_distinct_log_values(column_name)

    # --- Gestion de l'import ---
    def import_classification_from_json(self, json_data: dict) -> Tuple[bool, str]:
        """
        Importe les données de classification (Catégories, Genres, Sous-genres) à partir d'un dictionnaire JSON.
        Cette méthode est un proxy vers DBImporter.
        """
        return self.importer.import_classification_from_json(json_data)

    # --- Gestion de l'export ---
    def export_all_ouvrages_to_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        Exporte l'ensemble des données des ouvrages et de leurs classifications associées vers un fichier CSV.
        Cette méthode est un proxy vers DBExporter.
        """
        return self.exporter.export_all_ouvrages_to_csv(file_path)
