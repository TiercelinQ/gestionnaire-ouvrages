# pylint: disable=no-name-in-module
"""
Widget d'en-tête de l'application (HeaderWidget).
Affiche les informations clés (état de la connexion à la BDD, nom de l'utilisateur)
et fournit le bouton pour basculer entre les thèmes clair et sombre.
"""

from typing import Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from app.ui_manager import UIManager
from app.db_manager import DBManager
from app.config_manager import ConfigManager

ICON_BASE_PATH = ":/theme_icons/"
ICON_SIZE = QSize(30, 30)

class HeaderWidget(QWidget):
    """
    Widget d'en-tête (Header) contenant les informations clés (Utilisateur, BDD)
    et le bouton de sélection du Thème.
    """
    def __init__(self, config_manager: ConfigManager, ui_manager: UIManager, db_manager: DBManager, on_theme_change: Callable[[str], None], initial_theme: str):
        """
        :param ui_manager: Le gestionnaire d'UI pour appliquer les thèmes.
        :param db_manager: Le gestionnaire de BDD pour récupérer les informations.
        :param on_theme_change: Fonction de rappel (callback) appelée lors du changement de thème pour la sauvegarde.
        """
        super().__init__()
        self.config_manager = config_manager
        self.ui_manager = ui_manager
        self.db_manager = db_manager
        self.on_theme_change = on_theme_change
        self.setObjectName("HeaderWidget")

        self._current_theme = initial_theme

        self._setup_ui()
        self._setup_connections()

        self.update_theme_icon()

    def _setup_ui(self):
        """Initialise la structure et les composants visuels du Header."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.label_version_number = QLabel("1.0.3")
        self.label_version_number.setObjectName("UserName")

        name = self.config_manager.get_user_name()
        self.label_user_name = QLabel(f"{name}")
        self.label_user_name.setObjectName("UserName")

        self.data_base = QLabel("")
        self.data_base.setObjectName("DataBase")

        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("ThemeToggleButton")
        self.btn_theme.setFixedSize(QSize(32, 32))

        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(QLabel("Version: "))
        info_layout.addWidget(self.label_version_number)
        info_layout.addWidget(self._create_separator())
        info_layout.addWidget(QLabel("Utilisateur: "))
        info_layout.addWidget(self.label_user_name)
        info_layout.addWidget(self._create_separator())
        info_layout.addWidget(QLabel("Base de données: "))
        info_layout.addWidget(self.data_base)
        info_layout.addStretch(1)
        main_layout.addWidget(info_widget)
        main_layout.addWidget(self.btn_theme)

    def _setup_connections(self):
        """Connecte les signaux aux slots appropriés."""
        self.btn_theme.clicked.connect(self._toggle_theme)

    def _create_separator(self) -> QLabel:
        """Crée un séparateur visuel discret."""
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #C0C0C0;")
        return separator

    def update_theme_icon(self):
        """
        Met à jour l'icône et l'infobulle du bouton de thème
        en fonction du thème ACTUEL.
        """
        if not hasattr(self, 'btn_theme'):
            return
        icon_sun = ICON_BASE_PATH + "sun.svg"
        icon_moon = ICON_BASE_PATH + "moon.svg"

        if self._current_theme == 'dark':
            icon = QIcon(icon_sun)
            self.btn_theme.setToolTip("Passer au thème clair")
        else:
            icon = QIcon(icon_moon)
            self.btn_theme.setToolTip("Passer au thème sombre")

        self.btn_theme.setText("")
        self.btn_theme.setIcon(icon)
        self.btn_theme.setIconSize(ICON_SIZE)

    def _toggle_theme(self):
        """Bascule entre le thème clair et le thème sombre."""
        new_theme = 'dark' if self._current_theme == 'light' else 'light'
        self.ui_manager.set_theme(new_theme)
        self._current_theme = new_theme
        self.on_theme_change(new_theme)
        self.update_theme_icon()

    def update_db_info(self):
        """Met à jour le QLabel affichant le chemin de la BDD après la connexion."""
        full_db_path = self.db_manager.db_path

        if full_db_path:
            max_path_length = 50

            if len(full_db_path) > max_path_length:
                truncate_point = max_path_length - 3
                display_path = "..." + full_db_path[-truncate_point:]
            else:
                display_path = full_db_path

            self.data_base.setText(f"{display_path}")
            self.data_base.setToolTip(full_db_path)
        else:
            self.data_base.setText("Base de données: Non connectée")

    def update_user_name_info(self, new_username: str):
        """
        Met à jour le QLabel affichant le nom de l'utilisateur.
        Cette méthode est appelée (slot) lorsque le signal 'username_changed' est émis.
        """
        self.label_user_name.setText(f"{new_username}")
