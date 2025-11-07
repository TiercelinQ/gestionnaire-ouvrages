# pylint: disable=no-name-in-module
"""
Gestionnaire global de l'interface utilisateur (UIManager).
Gère l'application des styles QSS pour les thèmes (clair/sombre) au niveau
de l'application complète et fournit un utilitaire pour la gestion des chemins de ressources.
"""

import os
import sys
import logging
from PyQt6.QtWidgets import QWidget, QApplication
from app.utils import show_custom_message_box

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """
    Retourne le chemin absolu pour la ressource, fonctionne pour le dev et pour PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    if getattr(sys, 'frozen', False):
        return os.path.join(base_path, relative_path)
    else:
        return os.path.join(os.path.dirname(base_path), relative_path)

STYLES_DIR = resource_path(os.path.join('resources', 'styles'))

class UIManager:
    """
    Gère les aspects de l'interface utilisateur, notamment les thèmes Clair/Sombre.
    L'application du style se fait au niveau de l'application complète.
    """
    SETTINGS_FILE = "MonGestionnaireOuvrages"

    def __init__(self, main_window: QWidget):
        """
        Initialise l'UIManager.
        :param main_window: La fenêtre principale (référence nécessaire pour l'accès à l'instance QApplication).
        """
        self.main_window = main_window
        self.themes = {
            'light': os.path.join(STYLES_DIR, 'light_theme.qss'),
            'dark': os.path.join(STYLES_DIR, 'dark_theme.qss')
        }

    def set_theme(self, theme_name: str):
        """
        Charge et applique le fichier de style (.qss) correspondant au thème.
        :param theme_name: 'light' ou 'dark'.
        """
        logger.info("Application du thème - En cours")
        source_method = "ui_manager.set_theme"
        if theme_name not in self.themes:
            error_msg = f"Erreur : Le thème '{theme_name}' n'est pas reconnu. Un log a été créé."
            logger.info("Application du thème - Echec")
            logger.error("%s.",source_method,exc_info=True)
            show_custom_message_box(
                self.main_window,
                'ERROR',
                'Erreur Application Thème',
                error_msg
            )
            return

        style_file_path = self.themes[theme_name]

        if not os.path.exists(style_file_path):
            error_msg = (f"Erreur : Fichier de style '{style_file_path}' non trouvé.\n"
                        "Utilisation du style par défaut.")
            logger.info("Application du thème - Echec")
            logger.error("%s.",source_method,exc_info=True)
            show_custom_message_box(
                self.main_window,
                'ERROR',
                'Erreur Application Thème',
                error_msg
            )
            return

        try:
            with open(style_file_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            QApplication.instance().setStyleSheet(stylesheet)
            logger.info("Application du thème - Succès")
        except IOError as e:
            error_msg = f"Erreur de lecture du fichier QSS '{style_file_path}'."
            logger.info("Application du thème - Echec")
            logger.error("%s - Erreur: %s.",source_method,str(e),exc_info=True)
            show_custom_message_box(
                self.main_window,
                'ERROR',
                'Erreur Application Thème',
                error_msg
            )
