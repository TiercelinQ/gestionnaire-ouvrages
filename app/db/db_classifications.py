"""
Module de gestion des classifications hiérarchiques.
Gère toutes les opérations CRUD (Création, Lecture, Mise à jour, Suppression) sur
les tables 'categories', 'genres' et 'sous_genres' de la base de données.
"""

import sqlite3
import logging
from typing import List, Tuple, Optional
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database

logger = logging.getLogger(__name__)

class DBClassifications:
    """
    Gère toutes les opérations de la classification: Catégorie, Genre et Sous-Genres.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def get_all_categories(self) -> List[Tuple[int, str]]:
        """
        Récupère toutes les catégories (id, nom) avec gestion des logs.
        """
        logger.info("Récupération des catégories - En cours")
        source_method = 'db_classifications.get_all_categories'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_CATEGORIES} ORDER BY nom"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des catégories - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des catégories - Echec")
            log_event(
                db_manager=self.db_manager.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur récupération catégories.",
                exception=e)
            return []

    def get_genres_by_category_id(self, category_id: int) -> List[Tuple[int, str]]:
        """Récupère les genres associés à un ID de catégorie."""
        logger.info("Récupération des genres par catégorie - En cours")
        source_method = 'db_classifications.get_genres_by_category_id'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_GENRES} WHERE id_categorie = ? ORDER BY nom"
            params = (category_id,)
            self.db_manager.cursor.execute(sql, params)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des genres par catégorie - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des genres par catégorie - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération genre pour catégorie '{category_id}'.",
                exception=e)
            return []

    def get_subgenres_by_genre_id(self, genre_id: int) -> List[Tuple[int, str]]:
        """Récupère les sous-genres associés à un ID de genre."""
        logger.info("Récupération des sous-genres par genre - En cours")
        source_method = 'db_classifications.get_subgenres_by_genre_id'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"SELECT id, nom FROM {DBSchema.TABLE_SOUS_GENRES} WHERE id_genre = ? ORDER BY nom"
            params = (genre_id,)
            self.db_manager.cursor.execute(sql, params)
            results = self.db_manager.cursor.fetchall()
            logger.info("Récupération des sous-genres par genre - Succès")
            return results
        except sqlite3.Error as e:
            logger.info("Récupération des sous-genres par genre - Echec")
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération sous-genre pour genre '{genre_id}'.",
                exception=e)
            return []

    def add_classification_item(self, table_name: str, nom: str, parent_id: Optional[int] = None) -> Optional[int]:
        """
        Ajoute un nouvel élément de classification (Catégorie, Genre, Sous-genre).
        Retourne l'ID de l'élément inséré (clé primaire). Retire le commit prématuré.
        """
        logger.info("Ajout d'un item dans la table %s - En cours",table_name)
        source_method = 'db_classifications.add_classification_item'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            sql = None
            params = None
            if table_name not in [DBSchema.TABLE_GENRES, DBSchema.TABLE_SOUS_GENRES]:
                sql = f"INSERT INTO {table_name} (nom) VALUES (?)"
                params = (nom,)
            elif table_name in [DBSchema.TABLE_GENRES, DBSchema.TABLE_SOUS_GENRES]:
                if parent_id is None:
                    logger.info("Ajout d'un item dans la table %s - Echec",table_name)
                    log_event(
                        db_manager=self.db_manager,
                        level='ERROR',
                        source=source_method,
                        message=f"ID parent manquant ajout élément '{nom}' dans table '{table_name}'.")
                    return None
                parent_col = 'id_categorie' if table_name == DBSchema.TABLE_GENRES else 'id_genre'
                sql = f"INSERT INTO {table_name} (nom, {parent_col}) VALUES (?, ?)"
                params = (nom, parent_id)
            else:
                logger.info("Ajout d'un item dans la table %s - Echec",table_name)
                log_event(
                    db_manager=self.db_manager,
                    level='ERROR',
                    source=source_method,
                    message=f"Table classification inconnue ou non prise en charge: '{table_name}'")
                return None
            self.db_manager.cursor.execute(sql, params)
            new_id = self.db_manager.cursor.lastrowid
            logger.info("Ajout d'un item dans la table %s - Succès",table_name)
            return new_id
        except sqlite3.IntegrityError as e:
            logger.info("Ajout d'un item dans la table %s - Echec",table_name)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='WARNING',
                source=source_method,
                message=f"Doublon identifié: '{nom}' existe déjà dans '{table_name}'.",
                exception=e)
            return None
        except sqlite3.Error as e:
            logger.info("Ajout d'un item dans la table %s - Echec",table_name)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur ajout item '{nom}' dans '{table_name}'.",
                exception=e)
            return None

    def update_classification_item(self, table_name: str, item_id: int, nom: str) -> bool:
        """Met à jour le nom d'un élément de classification avec gestion des logs."""
        logger.info("Mise à jour d'un item dans la table %s - En cours",table_name)
        source_method = 'db_classifications.update_classification_item'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return False
        try:
            sql = f"UPDATE {table_name} SET nom = ? WHERE id = ?"
            self.db_manager.cursor.execute(sql, (nom, item_id))
            if self.db_manager.cursor.rowcount == 0:
                logger.info("Mise à jour d'un item dans la table %s - Echec",table_name)
                log_event(
                    db_manager=self.db_manager,
                    level='INFO',
                    source=source_method,
                    message=f"Mise à jour ignorée dans '{table_name}': Aucun élément pour '{item_id}'.")
                return False
            self.db_manager.connexion.commit()
            logger.info("Mise à jour d'un item dans la table %s - Succès",table_name)
            return True
        except sqlite3.IntegrityError as e:
            logger.info("Mise à jour d'un item dans la table %s - Echec",table_name)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='WARNING',
                source=source_method,
                message=f"Doublon identifié: '{nom}' existe déjà dans '{table_name}'.",
                exception=e)
            return False
        except sqlite3.Error as e:
            logger.info("Mise à jour d'un item dans la table %s - Echec",table_name)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur mise à jour item {item_id} dans '{table_name}'.",
                exception=e)
            return False

    def delete_classification_item(self, table_name: str, item_id: int) -> bool:
        """Supprime un élément de classification. ON DELETE CASCADE gère les dépendances."""
        logger.info("Suppression d'un item dans la table %s - En cours",table_name)
        source_method = 'db_classifications.delete_classification_item'
        if not self.db_manager.connexion or not table_name:
            log_error_connection_database(self.parent_widget, source_method)
            return False
        try:
            sql = f"DELETE FROM {table_name} WHERE id = ?"
            self.db_manager.cursor.execute(sql, (item_id,))
            if self.db_manager.cursor.rowcount == 0:
                logger.info("Suppression d'un item dans la table %s - Echec",table_name)
                log_event(
                    db_manager=self.db_manager,
                    level='INFO',
                    source=source_method,
                    message=f"Suppression ignoée dans '{table_name}': Aucun élément pour '{item_id}'.")
                return False
            self.db_manager.connexion.commit()
            logger.info("Suppression d'un item dans la table %s - Succès",table_name)
            return True
        except sqlite3.Error as e:
            logger.info("Suppression d'un item dans la table %s - Echec",table_name)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                source=source_method,
                message=f"Erreur suppression item {item_id} dans '{table_name}'",
                exception=e)
            return False
