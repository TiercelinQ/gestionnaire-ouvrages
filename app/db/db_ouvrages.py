"""
Module de gestion des ouvrages (DBOuvrages).
Implémente toutes les opérations CRUD (Création, Lecture, Mise à jour, Suppression)
sur la table principale 'ouvrages' de la base de données.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from app.data_models import DBSchema
from app.utils import log_event, log_error_connection_database, get_datetime

logger = logging.getLogger(__name__)

class DBOuvrages:
    """
    Gère toutes les opérations des Logs.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parent_widget = db_manager.parent_widget

    def get_all_ouvrages(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste complète des ouvrages avec les noms des classifications.
        Utilisé pour le tableau principal.
        """
        logger.info("Récupération de tous les ouvrages - En cours")
        source_method = 'db_ouvrages.get_all_ouvrages_for_display'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []

        sql = f"""
        SELECT
            o.id,
            o.titre,
            o.auteur,
            o.edition,
            o.id_localisation AS id_localisation,
            c.nom AS categorie_nom
        FROM {DBSchema.TABLE_OUVRAGES} o
        LEFT JOIN {DBSchema.TABLE_CATEGORIES} c ON o.id_categorie = c.id
        ORDER BY  o.auteur, o.titre
        """
        try:
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            ouvrages_list = [dict(row) for row in results]
            logger.info("Récupération de tous les ouvrages - Succès")
            return ouvrages_list
        except sqlite3.Error as e:
            logger.info("Récupération de tous les ouvrages - Echec")
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération ouvrages.",
                exception=e)
            return []

    def get_total_ouvrage_count(self) -> int:
        """Retourne le nombre total d'ouvrages enregistrés."""
        logger.info("Calcule du nombre total d'ouvrages - En cours")
        source_method = "db_ouvrages.get_total_ouvrages_count"
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        sql = "SELECT COUNT(id) FROM ouvrages"
        try:
            self.db_manager.cursor.execute(sql)
            logger.info("Calcule du nombre total d'ouvrages - Succès")
            return self.db_manager.cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.info("Calcule du nombre total d'ouvrages - Echec")
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur calcul nombre ouvrages.",
                exception=e)
            return 0

    def get_ouvrage_details(self, ouvrage_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère tous les détails (y compris les IDs) d'un ouvrage par son ID.
        Utilisé pour le chargement du formulaire d'édition.
        """
        logger.info("Récupération des détails de l'ouvrage %s - En cours",ouvrage_id)
        source_method = 'db_ouvrages.get_ouvrage_details'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            sql = f"""
            SELECT
                o.*,
                u.user_name AS cree_par_nom,
                m.user_name AS modifie_par_nom
            FROM {DBSchema.TABLE_OUVRAGES} o
            LEFT JOIN {DBSchema.TABLE_USERS} u ON o.cree_par = u.id
            LEFT JOIN {DBSchema.TABLE_USERS} m ON o.modifie_par = m.id
            WHERE o.id = ?
            """
            self.db_manager.cursor.execute(sql, (ouvrage_id,))
            row = self.db_manager.cursor.fetchone()
            if row:
                logger.info("Récupération des détails de l'ouvrage %s - Succès",ouvrage_id)
                return dict(row)
            else:
                logger.info("Récupération des détails de l'ouvrage %s - Terminée",ouvrage_id)
                return None
        except sqlite3.Error as e:
            logger.info("Récupération des détails de l'ouvrage %s - Echec",ouvrage_id)
            logger.error("%s - Ouvrage: %s - Erreur: %s",source_method,ouvrage_id,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération informations ouvrage {ouvrage_id}.",
                exception=e)
            return None

    def add_ouvrage(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Ajoute un nouvel ouvrage à la base de données.
        :param data: Dictionnaire contenant les données de l'ouvrage.
        :return: (success: bool, message: str)
        """
        logger.info("Ajout d'un nouvel ouvrage - En cours")
        source_method = 'db_ouvrages.add_ouvrage'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None

        user_id = self.db_manager.get_system_user_id()
        now = get_datetime()
        fields = ['titre','sous_titre','auteur','auteur_2',
                  'titre_original','cycle','tome','id_illustration',
                  'id_categorie','id_genre','id_sous_genre','id_periode',
                  'edition','collection','edition_annee','edition_numero','edition_premiere_annee','isbn',
                  'id_reliure','nombre_page','dimension','id_localisation',
                  'resume','remarques','couverture_premiere_chemin','couverture_premiere_emplacement','couverture_quatrieme_chemin','couverture_quatrieme_emplacement']
        values = []
        for field in fields:
            if field in ['id_illustration','id_categorie', 'id_genre', 'id_sous_genre','id_periode','id_reliure','id_localisation']:
                values.append(data.get(field) or None)
            else:
                values.append(data.get(field))
        fields.extend(['date_creation', 'date_modification', 'cree_par', 'modifie_par'])
        values.extend([now, now, user_id, user_id])
        placeholders = ', '.join(['?'] * len(fields))
        fields_str = ', '.join(fields)
        sql = f"INSERT INTO {DBSchema.TABLE_OUVRAGES} ({fields_str}) VALUES ({placeholders})"
        try:
            self.db_manager.cursor.execute(sql, tuple(values))
            self.db_manager.connexion.commit()
            logger.info("Ajout d'un nouvel ouvrage - Succès")
            return True, f"Ouvrage '<b>{data.get('titre')}</b>' ajouté avec succès."
        except sqlite3.Error as e:
            logger.info("Ajout d'un nouvel ouvrage - Echec")
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message="Erreur ajout ouvrage.",
                exception=e)
            return False, "Erreur lors de l'ajout de l'ouvrage. Veuillez consulter le journal d'activités"

    def update_ouvrage(self, ouvrage_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Met à jour un ouvrage existant.
        :param ouvrage_id: ID de l'ouvrage à modifier.
        :param data: Dictionnaire contenant les nouvelles données de l'ouvrage.
        :return: (success: bool, message: str)
        """
        logger.info("Mise à jour de l'ouvrage %s - En cours",ouvrage_id)
        source_method = 'db_ouvrages.update_ouvrage'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        user_id = self.db_manager.current_user_id
        now = get_datetime()
        fields_to_update = {
            'titre': data.get('titre'),
            'sous_titre': data.get('sous_titre'),
            'auteur': data.get('auteur'),
            'auteur_2': data.get('auteur_2'),
            'titre_original': data.get('titre_original'),
            'cycle': data.get('cycle'),
            'tome': data.get('tome'),
            'id_illustration': data.get('id_illustration') or None,
            'id_categorie': data.get('id_categorie') or None,
            'id_genre': data.get('id_genre') or None,
            'id_sous_genre': data.get('id_sous_genre') or None,
            'id_periode': data.get('id_periode') or None,
            'edition': data.get('edition'),
            'collection': data.get('collecton,'),
            'edition_annee': data.get('edition_annee'),
            'edition_numero': data.get('edition_numero'),
            'edition_premiere_annee': data.get('edition_premiere_annee'),
            'isbn': data.get('isbn'),
            'id_reliure': data.get('id_reliure') or None,
            'nombre_page': data.get('nombre_page'),
            'dimension': data.get('dimension'),
            'id_localisation': data.get('id_localisation') or None,
            'localisation_details': data.get('localisation_details') or None,
            'resume': data.get('resume'),
            'remarques': data.get('remarques'),
            'couverture_premiere_chemin': data.get('couverture_premiere_chemin'),
            'couverture_premiere_emplacement': data.get('couverture_premiere_emplacement'),
            'couverture_quatrieme_chemin': data.get('couverture_quatrieme_chemin'),
            'couverture_quatrieme_emplacement': data.get('couverture_quatrieme_emplacement')
        }
        set_clauses = [f"{k} = ?" for k in fields_to_update.keys()]
        values = list(fields_to_update.values())
        set_clauses.extend(["date_modification = ?", "modifie_par = ?"])
        values.extend([now, user_id])
        sql = f"UPDATE {DBSchema.TABLE_OUVRAGES} SET {', '.join(set_clauses)} WHERE id = ?"
        values.append(ouvrage_id)
        try:
            self.db_manager.cursor.execute(sql, tuple(values))
            self.db_manager.connexion.commit()
            if self.db_manager.cursor.rowcount > 0:
                logger.info("Mise à jour de l'ouvrage %s - Succès",ouvrage_id)
                return True, f"Ouvrage '<b>{data.get('titre')}</b>' mis à jour avec succès."
            else:
                logger.info("Mise à jour de l'ouvrage %s - Terminée",ouvrage_id)
                return False, "Aucun ouvrage trouvé avec cet ID."
        except sqlite3.Error as e:
            logger.info("Mise à jour de l'ouvrage %s - Echec",ouvrage_id)
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur mise à jour ouvrage {ouvrage_id}.",
                exception=e)
            return False, f"Erreur lors de la mise à jour de l'ouvrage <b>{ouvrage_id}</b>. Veuillez consulter le journal d'activités."

    def delete_ouvrage(self, ouvrage_id: int) -> Tuple[bool, str]:
        """
        Supprime un ouvrage de la base de données.
        :param ouvrage_id: ID de l'ouvrage à supprimer.
        :return: (success: bool, message: str)
        """
        logger.info("Suppression de l'ouvrage %s - En cours",ouvrage_id)
        source_method = 'db_ouvrages.delete_ouvrage'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return None
        try:
            self.db_manager.cursor.execute(f"DELETE FROM {DBSchema.TABLE_OUVRAGES} WHERE id = ?", (ouvrage_id,))
            self.db_manager.connexion.commit()
            if self.db_manager.cursor.rowcount > 0:
                logger.info("Suppression de l'ouvrage %s - Succès",ouvrage_id)
                return True, "Ouvrage supprimé avec succès."
            else:
                logger.info("Suppression de l'ouvrage %s - Terminée",ouvrage_id)
                return False, "Aucun ouvrage trouvé avec cet ID."
        except sqlite3.Error as e:
            logger.info("Suppression de l'ouvrage %s - Echec",ouvrage_id)
            logger.error("%s - Erreur: %s",source_method,e,exc_info=True)
            if self.db_manager.connexion: self.db_manager.connexion.rollback()
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur suppression ouvrage {ouvrage_id}.",
                exception=e)
            return False, f"Erreur BDD lors de la suppression de l'ouvrage : <b>{ouvrage_id}</b>. Veuillez consulter le journal d'activités."

    # --- Requêtes KPI --- #
    def get_ouvrages_by_location(self) -> dict[str, int]:
        """
        Retourne un dict {localisation_nom: count} avec le nombre d'ouvrages par localisation.
        """
        logger.info("Répartition ouvrages par localisation - En cours")
        source_method = 'db_manager.get_ouvrages_by_location'

        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []

        try:
            sql = f"""
            SELECT COALESCE(loc.nom, 'Non renseignée') AS localisation_nom,
                COUNT(*) AS total
            FROM {DBSchema.TABLE_OUVRAGES} o
            LEFT JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
            GROUP BY COALESCE(loc.nom, 'Non renseignée')
            ORDER BY total DESC;
            """

            self.db_manager.cursor.execute(sql)
            rows = self.db_manager.cursor.fetchall()

            result = {}
            for row in rows:
                loc_nom = row["localisation_nom"] if hasattr(row, "keys") else row[0]
                total = row["total"] if hasattr(row, "keys") else row[1]
                result[loc_nom] = total

            logger.info("Répartition ouvrages par localisation - Succès")
            return result
        except sqlite3.Error as e:
            logger.info("Répartition ouvrages par localisation - Echec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur répartition ouvrages par localisation.",
                exception=e)
            return {}

    def get_cover_completion_stats_by_location(self, column: str, location: str = "Toutes") -> tuple[int, int]:
        """
        Retourne le nombre d'ouvrages avec couverture renseignée vs sans couverture,
        filtré par localisation ("Toutes", "Non renseignée" ou une localisation précise).
        """
        logger.info("Comptage complétion ouvrages - En cours")
        source_method = "db_manager.get_cover_completion_stats_by_location"

        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return 0, 0

        try:
            if column not in ("couverture_premiere_chemin", "couverture_quatrieme_chemin"):
                raise ValueError(f"Colonne non supportée: {column}")

            if location == "Toutes":
                sql_total = f"SELECT COUNT(*) AS total FROM {DBSchema.TABLE_OUVRAGES}"
                sql_with = f"SELECT COUNT(*) AS total FROM {DBSchema.TABLE_OUVRAGES} WHERE {column} IS NOT NULL"
                params_total, params_with = (), ()
            elif location == "Non renseignée":
                sql_total = f"SELECT COUNT(*) AS total FROM {DBSchema.TABLE_OUVRAGES} WHERE id_localisation IS NULL"
                sql_with = f"SELECT COUNT(*) AS total FROM {DBSchema.TABLE_OUVRAGES} WHERE id_localisation IS NULL AND {column} IS NOT NULL"
                params_total, params_with = (), ()
            else:
                sql_total = f"""
                    SELECT COUNT(*) AS total
                    FROM {DBSchema.TABLE_OUVRAGES} o
                    JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
                    WHERE loc.nom = ?
                """
                sql_with = f"""
                    SELECT COUNT(*) AS total
                    FROM {DBSchema.TABLE_OUVRAGES} o
                    JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
                    WHERE loc.nom = ? AND {column} IS NOT NULL
                """
                params_total, params_with = (location,), (location,)

            self.db_manager.cursor.execute(sql_total, params_total)
            total = self.db_manager.cursor.fetchone()["total"]

            if total == 0:
                return 0, 0

            self.db_manager.cursor.execute(sql_with, params_with)
            with_cover = self.db_manager.cursor.fetchone()["total"]

            without_cover = total - with_cover

            logger.info("Comptage complétion ouvrages - Succès")
            return with_cover, without_cover

        except sqlite3.Error as e:
            logger.info("Comptage complétion ouvrages - Échec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level="ERROR",
                source=source_method,
                message="Erreur comptage complétion ouvrages.",
                exception=e,
            )
            return 0, 0

    def get_top_categories_by_location(self, location: str, limit: int = 3) -> list[tuple[str, int]]:
        """
        Retourne les catégories les plus fréquentes pour une localisation donnée.
        - "Toutes" : top catégories globales
        - "Non renseignée" : ouvrages sans localisation
        - localisation précise : ouvrages liés à cette localisation
        """
        logger.info("Récupération top catégorie par localisation - En cours")
        source_method = 'db_ouvrages.get_top_categories_by_localisation'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            if location == "Toutes":
                sql = f"""
                SELECT c.nom AS categorie, COUNT(*) AS total
                FROM {DBSchema.TABLE_OUVRAGES} o
                LEFT JOIN {DBSchema.TABLE_CATEGORIES} c ON o.id_categorie = c.id
                GROUP BY c.nom
                ORDER BY total DESC
                LIMIT ?
                """
                params = (limit,)
            elif location == "Non renseignée":
                sql = f"""
                SELECT c.nom AS categorie, COUNT(*) AS total
                FROM {DBSchema.TABLE_OUVRAGES} o
                LEFT JOIN {DBSchema.TABLE_CATEGORIES} c ON o.id_categorie = c.id
                WHERE o.id_localisation IS NULL
                GROUP BY c.nom
                ORDER BY total DESC
                LIMIT ?
                """
                params = (limit,)

            else:
                sql = f"""
                SELECT c.nom AS categorie, COUNT(*) AS total
                FROM {DBSchema.TABLE_OUVRAGES} o
                JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
                LEFT JOIN {DBSchema.TABLE_CATEGORIES} c ON o.id_categorie = c.id
                WHERE loc.nom = ?
                GROUP BY c.nom
                ORDER BY total DESC
                LIMIT ?
                """
                params = (location, limit)

            self.db_manager.cursor.execute(sql, params)
            rows = self.db_manager.cursor.fetchall()
            logger.info("Récupération top catégorie par localisation - Succès")
            return [(r["categorie"], r["total"]) for r in rows]
        except sqlite3.Error as e:
            logger.info("Récupération top catégorie par localisation - Echec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur Récupération top catégorie par localisation.",
                exception=e)
            return []

    def get_last_books_by_location(self, location: str, limit: int = 5) -> list[dict[str, str]]:
        """
        Retourne les derniers ouvrages créés pour une localisation donnée.
        """
        logger.info("Récupération derniers ouvrages par localisation - En cours")
        source_method = 'db_manager.get_last_books_by_location'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            if location == "Toutes":
                sql = f"""
                SELECT titre, auteur, date_creation
                FROM {DBSchema.TABLE_OUVRAGES}
                ORDER BY date_creation DESC
                LIMIT ?
                """
                params = (limit,)

            elif location == "Non renseignée":
                sql = f"""
                SELECT titre, auteur, date_creation
                FROM {DBSchema.TABLE_OUVRAGES}
                WHERE id_localisation IS NULL
                ORDER BY date_creation DESC
                LIMIT ?
                """
                params = (limit,)
            else:
                sql = f"""
                SELECT o.titre, o.auteur, o.date_creation
                FROM {DBSchema.TABLE_OUVRAGES} o
                JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
                WHERE loc.nom = ?
                ORDER BY o.date_creation DESC
                LIMIT ?
                """
                params = (location, limit)

            self.db_manager.cursor.execute(sql, params)
            rows = self.db_manager.cursor.fetchall()
            logger.info("Récupération derniers ouvrages par localisation - Succès")

            result = []
            for r in rows:
                titre = r["titre"] if hasattr(r, "keys") else r[0]
                auteur = r["auteur"] if hasattr(r, "keys") else r[1]
                raw_date = r["date_creation"] if hasattr(r, "keys") else r[2]

                dt = datetime.strptime(raw_date.split('.')[0], "%Y-%m-%d %H:%M:%S")
                date_fmt = dt.strftime("%d %b. %Y à %H:%M")

                result.append({"titre": titre, "auteur": auteur, "date": date_fmt})
            return result
        except sqlite3.Error as e:
            logger.info("Récupération derniers ouvrages par localisation - Échec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur récupération derniers ouvrages par localisation.",
                exception=e)
            return

    def get_categories_by_location(self) -> dict[str, dict[str, int]]:
        """
        Retourne un dict {localisation: {categorie: count}}.
        Exemple :
        {
            "Salon": {"Roman": 10, "BD": 5},
            "Chambre": {"Essai": 3}
        }
        """
        logger.info("Répartition catégories par localisation - En cours")
        source_method = 'db_manager.get_categories_by_location'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"""
            SELECT COALESCE(loc.nom, 'Non renseignée') AS localisation,
                cat.nom AS categorie,
                COUNT(*) AS total
            FROM {DBSchema.TABLE_OUVRAGES} o
            LEFT JOIN {DBSchema.TABLE_LOCALISATIONS} loc ON o.id_localisation = loc.id
            JOIN {DBSchema.TABLE_CATEGORIES} cat ON o.id_categorie = cat.id
            GROUP BY COALESCE(loc.nom, 'Non renseignée'), cat.nom
            ORDER BY localisation, total DESC;
            """
            self.db_manager.cursor.execute(sql)
            rows = self.db_manager.cursor.fetchall()

            result: dict[str, dict[str, int]] = {}
            for row in rows:
                loc = row["localisation"]
                cat = row["categorie"]
                count = row["total"]
                if loc not in result:
                    result[loc] = {}
                result[loc][cat] = count

            logger.info("Répartition catégories par localisation - Succès")
            return result
        except sqlite3.Error as e:
            logger.info("Répartition catégories par localisation - Echec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur répartition catégories par localisation.",
                exception=e)
            return {}

    def get_periodes_by_location(self) -> dict[str, dict[str, int]]:
        """
        Retourne un dict {localisation: {periode: count}}.
        """
        logger.info("Répartition périodes par localisation - En cours")
        source_method = 'db_manager.get_periodes_by_location'
        if not self.db_manager.connexion:
            log_error_connection_database(self.parent_widget, source_method)
            return []
        try:
            sql = f"""
            SELECT COALESCE(loc.nom, 'Non renseignée') AS localisation_nom,
                COALESCE(per.nom, 'Non renseignée') AS periode,
                COUNT(*) AS total
            FROM ouvrages o
            LEFT JOIN localisations loc ON o.id_localisation = loc.id
            LEFT JOIN periodes per ON o.id_periode = per.id
            GROUP BY COALESCE(loc.nom, 'Non renseignée'), COALESCE(per.nom, 'Non renseignée')
            ORDER BY localisation_nom, total DESC;
            """
            self.db_manager.cursor.execute(sql)
            rows = self.db_manager.cursor.fetchall()

            result: dict[str, dict[str, int]] = {}
            for row in rows:
                loc = row["localisation_nom"]
                per = row["periode"]
                count = row["total"]
                if loc not in result:
                    result[loc] = {}
                result[loc][per] = count

            logger.info("Répartition périodes par localisation - Succès")
            return result
        except sqlite3.Error as e:
            logger.info("Répartition périodes par localisation - Echec")
            logger.error("%s - Erreur: %s", source_method, e, exc_info=True)
            log_event(
                db_manager=self.db_manager,
                level='ERROR',
                source=source_method,
                message=f"Erreur répartition périodes par localisation.",
                exception=e)
            return {}
