"""
Module de gestion des importations de données (DBImporter).
Gère la lecture et l'insertion des données de classification (Catégories, Genres, Sous-Genres)
dans la base de données à partir d'un fichier au format JSON.
"""

import sqlite3
import logging
from typing import Optional, Tuple
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database
from app.db.db_classifications import DBClassifications

logger = logging.getLogger(__name__)

class DBImporter:
    """
    Gère toutes les opérations d'importation de données.
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget
        self.classification_manager = DBClassifications(db_manager)

    def _get_classification_id(self, table_name: str, nom: str, parent_id: Optional[int] = None) -> Optional[int]:
        """
        Récupère l'ID d'une classification par son nom et, si nécessaire, son parent.
        Ajoute l'élément s'il n'existe pas.
        """
        logger.info("Récupération de l'ID de la table %s - En cours",table_name)
        source_method = 'db_import._get_classification_id'
        if not self.db_manager.cursor:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            sql = None
            params = None
            if table_name == DBSchema.TABLE_CATEGORIES:
                sql = f"SELECT id FROM {table_name} WHERE nom = ?"
                params = (nom,)
            elif table_name in [DBSchema.TABLE_GENRES, DBSchema.TABLE_SOUS_GENRES]:
                if parent_id is None:
                    logger.info("Récupération de l'ID de la table %s - Echec",table_name)
                    log_event(
                        db_manager=self.db_manager,
                        level='ERROR',
                        source=source_method,
                        message=f"Parent ID manquant recherche item '{nom}' dans '{table_name}'."
                    )
                    return None
                parent_col = 'id_categorie' if table_name == DBSchema.TABLE_GENRES else 'id_genre'
                sql = f"SELECT id FROM {table_name} WHERE nom = ? AND {parent_col} = ?"
                params = (nom, parent_id)
            else:
                logger.info("Récupération de l'ID de la table %s - Echec",table_name)
                log_event(
                    db_manager=self.db_manager,
                    level='ERROR',
                    source=source_method,
                    message=f"Table classification inconnue: '{table_name}'")
                return None
            self.db_manager.cursor.execute(sql, params)
            result = self.db_manager.cursor.fetchone()
            if result:
                logger.info("Récupération de l'ID de la table %s - Succès",table_name)
                return result[0]
            new_id = self.classification_manager.add_classification_item(table_name, nom, parent_id)
            return new_id
        except sqlite3.Error as e:
            logger.info("Récupération de l'ID de la table %s - Echec",table_name)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur vérification/insertion item '{nom}' dans '{table_name}'.",
                exception=e)
            return None

    def insert_classification_data(self, json_data: dict) -> Tuple[int, int, int, Optional[str]]:
        """
        Méthode récursive pour insérer les données de classification (catégories, genres, sous-genres).
        Gère les relations parent-enfant, avec gestion des logs.

        Retourne: (cats_added, genres_added, subgenres_added, error_msg)
        """
        logger.info("Insertion des données de classification (catégories, genres et sous-genres) - En cours")
        source_method = 'db_import._insert_classification_data'
        cats_added, genres_added, subgenres_added = 0, 0, 0
        error_msg = None
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return (0, 0, 0, "Connexion BDD non établie.")
        try:
            for cat_name, cat_data in json_data.get('categories', {}).items():
                cat_id = self._get_classification_id(DBSchema.TABLE_CATEGORIES, cat_name)
                if cat_id is None:
                    logger.info("Insertion des données de classification (catégories) - Echec")
                    error_msg = f"Erreur ajouter catégorie '{cat_name}'."
                    log_event(
                        db_manager=self.db_manager,
                        level='ERROR',
                        source=source_method,
                        message=error_msg)
                    continue
                cats_added += 1
                for genre_name, genre_data in cat_data.get('genres', {}).items():
                    genre_id = self._get_classification_id(DBSchema.TABLE_GENRES, genre_name, cat_id)
                    if genre_id is None:
                        logger.info("Insertion des données de classification (genres) - Echec")
                        error_msg = f"Erreur ajout genre '{genre_name}' (Cat: '{cat_name}')."
                        log_event(
                            db_manager=self.db_manager,
                            level='ERROR',
                            source=source_method,
                            message=error_msg)
                        continue
                    genres_added += 1
                    for subgenre_item in genre_data.get('sous_genres', []):
                        subgenre_name = str(subgenre_item)
                        subgenre_id = self._get_classification_id(DBSchema.TABLE_SOUS_GENRES, subgenre_name, genre_id)
                        if subgenre_id is None:
                            logger.info("Insertion des données de classification (sous-genres) - Echec")
                            error_msg = f"Erreur ajoutsous-genre '{subgenre_name}' (Genre: '{genre_name}')."
                            log_event(
                                db_manager=self.db_manager,
                                level='ERROR',
                                source=source_method,
                                message=error_msg)
                            continue
                        subgenres_added += 1
            self.db_manager.connexion.commit()
            logger.info("Insertion des données de classification (catégories, genres et sous-genres) - Succès")
            return (cats_added, genres_added, subgenres_added, error_msg)
        except Exception as e:
            logger.info("Insertion des données de classification (catégories, genres et sous-genres) - Echec")
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            error_msg = f"Erreur importation de classification. Veuillez consulter le journal d'activités."
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur importation classification.",
                exception=e)
            return (0, 0, 0, error_msg)

    def import_classification_from_json(self, json_data: dict) -> Tuple[bool, str]:
        """
        Point d'entrée public pour l'importation de classifications depuis un dictionnaire JSON.
        Gère la vérification initiale et les exceptions globales.
        :return: (success: bool, message: str)
        """
        logger.info("Insertion des données de classification depuis JSON - En cours")
        source_method = 'db_import.import_classification_from_json'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return False, "Connexion BDD non établie."

        if not isinstance(json_data, dict) or 'categories' not in json_data:
            logger.info("Insertion des données de classification depuis JSON - Echec")
            message = "Le dictionnaire n'est pas au format de classification attendu."
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=message)
            return False, message

        try:
            cats, genres, subgenres, error_msg = self.insert_classification_data(json_data)
            if error_msg and (cats == 0 and genres == 0 and subgenres == 0):
                logger.info("Insertion des données de classification depuis JSON - Echec")
                return False, f"Importation complètement échouée. Raison: {error_msg}"
            message = (f"Importation terminée !\n"
                        f"Catégories ajoutées : {cats}\n"
                        f"Genres ajoutés : {genres}\n"
                        f"Sous-genres ajoutés : {subgenres}")
            if error_msg:
                logger.info("Insertion des données de classification depuis JSON - Echec")
                log_event(
                    db_manager=self.db_manager,
                    level='WARNING',
                    source=source_method,
                    message=f"Importation terminée / erreurs partielles. Bilan: '{cats}'c, '{genres}'g, '{subgenres}'s.")
                message += f"\n\nAvertissement: Des erreurs ont été rencontrées (voir les logs ou la console pour les détails)."
            return True, message
        except Exception as e:
            logger.info("Insertion des données de classification depuis JSON - Echec")
            error_message = f"Une erreur inattendue est survenue. Veuillez consulter le journal d'activités."
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur lors de l'appel à _insert_classification_data.",
                exception=e)
            return False, error_message