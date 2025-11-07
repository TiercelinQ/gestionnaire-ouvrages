"""
Gère les opérations de chargement, de lecture et de sauvegarde de la configuration
utilisateur de l'application (chemin de la base de données, thème, nom d'utilisateur, etc.)
dans le fichier config_user.json.
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from app.utils import show_custom_message_box

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Gère le chargement et la sauvegarde de la configuration utilisateur
    (chemin BDD, thème, nom d'utilisateur, etc.) dans le fichier config_user.json.
    """

    CONFIG_FILE = "config_user.json"
    APP_NAME = "MonGestionnaireOuvrages"

    def __init__(self):
        """Initialise le gestionnaire de configuration et charge les données."""
        self._config_data: Dict[str, Any] = self._load_config()

    def _get_app_config_dir(self) -> str:
        """Retourne le chemin du répertoire de configuration de l'application (OS-dépendant)."""
        logger.info("Récupération du chemin du configuration de l'application - En cours")
        if sys.platform == "win32":
            app_data = os.environ.get('APPDATA')
            if app_data:
                logger.info("Récupération du chemin du configuration de l'application - Succès")
                return os.path.join(app_data, self.APP_NAME)
        return os.path.join(os.path.expanduser("~"), f".{self.APP_NAME}")

    def _get_config_path(self) -> str:
        """Retourne le chemin complet du fichier de configuration."""
        config_dir = self._get_app_config_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, self.CONFIG_FILE)

    def _load_config(self) -> Dict[str, Any]:
        """Charge le fichier de configuration existant ou initialise avec des valeurs par défaut."""
        logger.info("Chargement des configurations de l'utilisateur - En cours")
        source_method = "config_manager._load_config"
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    logger.info("Chargement des configurations de l'utilisateur - Succès")
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logger.info("Chargement des configurations de l'utilisateur - Echec")
                logger.error("%s - Erreur: %s",source_method,str(e),exc_info=True)
                show_custom_message_box(
                    None,
                    'ERROR',
                    "Erreur Chargement Config",
                    "Erreur lors du chargement de la configuration de l'utilisateur.",
                    f"(Source: {source_method})"
                )

        default_user_name = os.getlogin() if hasattr(os, 'getlogin') else "Utilisateur"

        return {
            'db_path': None,
            'theme': 'light',
            'user_name': default_user_name
        }

    def save_config(self, key: str, value: Any):
        """Sauvegarde une clé/valeur dans le fichier de configuration
        et met à jour les données en mémoire.
        """
        logger.info("Sauvegarde des configurations de l'utilisateur - En cours")
        source_method = "config_manager.save_config"
        self._config_data[key] = value
        config_path = self._get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4)
                logger.info("Sauvegarde des configurations de l'utilisateur - Succès")
        except IOError as e:
            logger.info("Sauvegarde des configurations de l'utilisateur - Echec")
            logger.error("%s - Erreur: %s",source_method,str(e),exc_info=True)
            show_custom_message_box(
                None,
                'ERROR',
                "Erreur Sauvegarde Config",
                "Erreur lors de la sauvegarde de la configuration de l'utilisateur.",
                f"(Source: {source_method})"
            )

    def get_app_config_dir_path(self) -> str:
        """
        Retourne le chemin du répertoire de configuration de l'application.
        Utilisé par les services externes (comme le logging) pour la centralisation.
        """
        return self._get_app_config_dir()

    def get_db_path(self) -> str | None:
        """Retourne le chemin de la base de données sauvegardé."""
        return self._config_data.get('db_path')

    def set_db_path(self, path: str):
        """Définit et sauvegarde le chemin de la base de données."""
        self.save_config('db_path', path)

    def get_theme(self) -> str:
        """Retourne le nom du thème sauvegardé ou 'dark' par défaut."""
        return self._config_data.get('theme', 'dark')

    def set_theme(self, theme_name: str):
        """Définit et sauvegarde le nom du thème."""
        self.save_config('theme', theme_name)

    def get_user_name(self) -> str:
        """Retourne le nom d'utilisateur sauvegardé ou le nom système par défaut."""
        default_user_name = os.getlogin() if hasattr(os, 'getlogin') else "Utilisateur"
        return self._config_data.get('user_name', default_user_name)

    def set_user_name(self, name: str):
        """Définit et sauvegarde le nom d'utilisateur."""
        self.save_config('user_name', name)

    def get_available_themes(self) -> List[str]:
        """Retourne la liste des noms des thèmes disponibles."""
        return ['dark', 'light']
