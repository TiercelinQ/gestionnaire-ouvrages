# pylint: disable=no-name-in-module
"""
Point d'entrée principal de l'interface utilisateur.
Contient la classe GestionnaireOuvrageApp (QMainWindow) qui gère la structure
globale de l'application, l'initialisation des managers (Config, DB, UI)
et les fonctionnalités de gestion de thème et de redémarrage.
"""

import os
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QApplication, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication, Qt, QTimer
import resources_rc # pylint: disable=unused-import
from app.ui_manager import UIManager
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.header_widget import HeaderWidget
from app.dashboard_widget import DashboardWidget
from app.search_ouvrage_widget import SearchOuvrageWidget
from app.parameters_widget import ParametersWidget
from app.utils import show_custom_message_box

logger = logging.getLogger(__name__)

class GestionnaireOuvrageApp(QMainWindow):
    """
    Application Principale de gestion d'ouvrages
    """
    def __init__(self):
        super().__init__()
        # --- Configuration de la fenêtre ---
        app_icon = QIcon(":/global_icons/iconBookInventoryApp.png")
        self.setWindowIcon(app_icon)
        self.setWindowTitle("Gestionnaire d'Ouvrages")
        self.setMinimumSize(1280, 720)

        # --- Gestionnaires principaux ---
        self.config_manager = ConfigManager()
        self.db_manager = DBManager(parent_widget=self)
        self.ui_manager = UIManager(self)

        # --- Thème initial ---
        self._apply_initial_theme()

        # --- Initialisation de la base de données ---
        if not self._initialize_database():
            logger.error("Initialisation Base de Données - Echec")
            logger.critical("Fermeture de l'application")
            return

        self._setup_ui()
        self.db_manager.get_system_user_id()
        self.center_window()

    def center_window(self):
        """Centre la fenêtre principale sur l'écran."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    # --- Gestion BDD ---
    def _initialize_database(self) -> bool:
        """
        Initialise la connexion à la base de données :
        - Utilise le chemin configuré si disponible
        - Vérifie si 'db_storage' est présent dans la config, sinon l'ajoute
        - Sinon propose à l'utilisateur de créer/ouvrir une base
        Retourne True si la connexion est réussie, False sinon.
        """
        logger.info("Identification Base de Données - En Cours")
        db_path = self.config_manager.get_db_path()

        if db_path and os.path.exists(db_path):
            logger.info("Identification Base de Données - Succès")
            logger.info("Identification Stockage Base de Données - En Cours")
            if not self.config_manager.get_db_storage():
                self.config_manager.update_db_storage(db_path)
                logger.info("Identification Stockage Base de Données - Succès")
            return self.db_manager.connect_db(db_path, parent_widget=self)
        logger.info("Identification Base de Données - Terminée")
        logger.info("Identification Base de Données - Création ou Ouverture d'une BDD")
        return self._select_or_create_db()

    def _select_or_create_db(self) -> bool:
        """
        Propose à l'utilisateur d'ouvrir une base existante ou d'en créer une nouvelle.
        Enregistre le chemin choisi et avertit si la base est sur un service Cloud.
        """
        choice_box = QMessageBox(self)
        choice_box.setWindowTitle("Gestion Base de Données")
        choice_box.setIcon(QMessageBox.Icon.Question)
        choice_box.setText("Souhaitez-vous ouvrir une base existante ou créer une nouvelle base ?")
        choice_box.setInformativeText(
            "Cliquez sur 'Ouvrir' pour sélectionner un fichier existant, "
            "ou sur 'Créer' pour définir un nouveau fichier."
        )

        btn_open = choice_box.addButton("Ouvrir", QMessageBox.ButtonRole.AcceptRole)
        btn_create = choice_box.addButton("Créer", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = choice_box.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)

        choice_box.exec()
        selected_button = choice_box.clickedButton()

        if selected_button == btn_cancel:
            show_custom_message_box(
                self,
                'INFO',
                "Gestion Base de Données",
                "Aucune base de données sélectionnée.",
                "L'application ne peut pas démarrer sans fichier de base de données."
            )
            return False

        db_path = None
        if selected_button == btn_open:
            db_path, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un Fichier de Base de Données",
                os.path.expanduser("~"),
                "Fichiers de base de données (*.db)"
            )
        elif selected_button == btn_create:
            db_path, _ = QFileDialog.getSaveFileName(
                self,
                "Créer un Nouveau Fichier de Base de Données",
                os.path.join(os.path.expanduser("~"), "MonGestionnaireOuvrages.db"),
                "Fichiers de base de données (*.db)"
            )

        if db_path:
            self.config_manager.set_db_path(db_path)
            self.config_manager.update_db_storage(db_path)

            # Si c'est du cloud, avertir l'utilisateur
            if self.config_manager.get_db_storage() == 'cloud':
                show_custom_message_box(
                    self,
                    level="WARNING",
                    title="Base sur Cloud détectée",
                    text="La base est stockée sur un service Cloud.",
                    informative_text="<b>Attention</b> : les écritures simultanées peuvent provoquer des erreurs "
                                    "ou une corruption de la base.\n\n"
                                    "Évitez d'utiliser l'application à deux en même temps.",
                    buttons=["Ok"]
                )

            return self.db_manager.connect_db(db_path, parent_widget=self)

        return False

    # --- Gestion du Thème ---
    def _apply_initial_theme(self):
        """Applique le thème initial sauvegardé dans la configuration."""
        initial_theme = self.config_manager.get_theme()
        self.ui_manager.set_theme(initial_theme)

    def _handle_theme_change(self, theme_name: str):
        """Gère le changement de thème et sauvegarde le choix dans la configuration."""
        self.config_manager.save_config('theme', theme_name)
        self._force_full_style_update(theme_name)
        if hasattr(self, 'search_ouvrage_widget'):
            self.search_ouvrage_widget.update_icons(theme_name)
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.refresh_theme(theme_name)

    def _force_full_style_update(self, theme_name: str):
        """
        Réapplique le QSS en cours et force le rafraîchissement du style
        sur les widgets spécifiques pour garantir que tous les sélecteurs sont pris en compte.
        """
        self.ui_manager.set_theme(theme_name)

        widgets_to_polish = []
        if hasattr(self, 'header_widget'):
            widgets_to_polish.append(self.header_widget)
        if hasattr(self, 'parameter_widget'):
            widgets_to_polish.append(self.parameter_widget)
        if hasattr(self, 'search_ouvrage_widget'):
            widgets_to_polish.append(self.search_ouvrage_widget)

        def _recursive_polish(widget):
            if widget is None:
                return

            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)

            for child in widget.findChildren(QWidget):
                if child != self:
                    child.style().unpolish(child)
                    child.style().polish(child)

            if hasattr(widget, 'table_view') and hasattr(widget.table_view, 'horizontalHeader'):
                header = widget.table_view.horizontalHeader()
                header.style().unpolish(header)
                header.style().polish(header)

        for widget in widgets_to_polish:
            _recursive_polish(widget)

        if hasattr(self, 'header_widget'):
            self.header_widget.update_theme_icon()

        self.style().unpolish(self)
        self.style().polish(self)

    # --- Construction de l'UI ---
    def _setup_ui(self):
        """Met en place la structure principale de l'interface utilisateur (Header + Tabs)."""
        initial_theme_name = self.config_manager.get_theme()
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 1. Header (Utilisateur, BDD, Thème)
        self.header_widget = HeaderWidget(
            self.config_manager,
            self.ui_manager,
            self.db_manager,
            on_theme_change=self._handle_theme_change,
            initial_theme=initial_theme_name
        )
        main_layout.addWidget(self.header_widget)

        # 2. Zone des Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("MainTabWidget")
        # --- Onglet 1 : Tableau de bord ---
        self.dashboard_widget = DashboardWidget(self.db_manager, self.config_manager)
        self.tab_widget.addTab(self.dashboard_widget, "Tableau de bord")
        # --- Onglet 2 : Gestion des Ouvrages ---
        self.search_ouvrage_widget = SearchOuvrageWidget(self.db_manager, self.config_manager, initial_theme=initial_theme_name)
        self.tab_widget.addTab(self.search_ouvrage_widget, "Ouvrages")
        # --- Onglet 3 : Gestion des Paramètres ---
        self.parameter_widget = ParametersWidget(self.db_manager, self.config_manager)
        self.parameter_widget.setObjectName("ParametersPage")
        self.tab_widget.addTab(self.parameter_widget, "Paramètres")

        # Connexions des signaux
        if hasattr(self, '_handle_tab_change'):
            self.tab_widget.currentChanged.connect(self._handle_tab_change)

        if hasattr(self.parameter_widget, 'configuration_updated'):
            if hasattr(self.search_ouvrage_widget, 'load_ouvrages'):
                self.parameter_widget.configuration_updated.connect(self.search_ouvrage_widget.load_ouvrages)

        user_settings_widget = getattr(self.parameter_widget, 'user_settings_widget', None)
        if user_settings_widget and hasattr(user_settings_widget, 'restart_requested'):
            user_settings_widget.restart_requested.connect(self._restart_application)

        if hasattr(self.parameter_widget, 'user_settings_widget'):
            self.parameter_widget.user_settings_widget.username_changed.connect(self.header_widget.update_user_name_info)

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(main_container)

        self.search_ouvrage_widget.load_ouvrages()
        self.header_widget.update_db_info()

        current_theme = self.config_manager.get_theme()
        self._force_full_style_update(current_theme)

    def _handle_tab_change(self, index: int):
        """Gère les actions nécessaires lorsque l'onglet change."""

        if index == 0:
            self.search_ouvrage_widget.load_ouvrages()
        elif index == 1:
            self.parameter_widget.refresh_classifications()

    # --- Gestion fermeture application --- #
    def closeEvent(self, event): # pylint: disable=invalid-name
        """Événement appelé lors de la fermeture de la fenêtre. Ferme la connexion à la BDD."""
        self.db_manager.close_db()
        QApplication.quit()
        logger.info("Fermeture Application")
        event.accept()

    # --- Gestion redémarage application (uniquement avec le fichier .exe de l'application) ---
    def _execute_restart(self):
        """
        Fonction interne appelée par QTimer pour exécuter le redémarrage réel.
        Utilise os.execv pour une relance plus robuste que os.execl.
        """
        source_method = "main_app._execute_restart"
        python_executable = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        QCoreApplication.quit()
        try:
            os.execv(python_executable, (python_executable, script_path))
        except OSError as e:
            logger.critical("%s - Statut: Echec - Erreur: %s",source_method,str(e),exc_info=True)

    def _restart_application(self):
        """
        Déclenche le redémarrage différé sans utiliser de QMessageBox modale bloquante.
        """
        QTimer.singleShot(50, self._execute_restart)
