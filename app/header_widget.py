# pylint: disable=no-name-in-module
"""
Widget d'en-tête de l'application (HeaderWidget).
Affiche les informations clés (état de la connexion à la BDD, nom de l'utilisateur)
et fournit le bouton pour basculer entre les thèmes clair et sombre.
"""
from app import app_info
from typing import Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from app.ui_manager import UIManager
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.utils import show_custom_message_box
from app.app_constants import ICON_BASE_PATH_THEME, ICON_SIZE

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


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

        self.label_about = ClickableLabel("À propos")
        self.label_about.setObjectName("AboutLabel")
        self.label_about.setToolTip("Détails de l'application")
        self.label_about.setCursor(Qt.CursorShape.PointingHandCursor)

        self.label_version_number = QLabel(app_info.VERSION)
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
        info_layout.addWidget(self.label_about)
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
        self.label_about.clicked.connect(self._show_about_dialog)

    def _create_separator(self) -> QLabel:
        """Crée un séparateur visuel discret."""
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #C0C0C0;")
        return separator

    def update_theme_icon(self):
        """
        Met à jour les icônes et infobulles des boutons
        en fonction du thème ACTUEL.
        """
        if not hasattr(self, 'btn_theme'):
            return

        icon_sun = ICON_BASE_PATH_THEME + "sun.svg"
        icon_moon = ICON_BASE_PATH_THEME + "moon.svg"

        if self._current_theme == 'dark':
            iconTheme = QIcon(icon_sun)
            self.btn_theme.setToolTip("Passer au thème clair")
        else:
            iconTheme = QIcon(icon_moon)
            self.btn_theme.setToolTip("Passer au thème sombre")

        self.btn_theme.setText("")
        self.btn_theme.setIcon(iconTheme)
        self.btn_theme.setIconSize(ICON_SIZE)

    def _toggle_theme(self):
        """Bascule entre le thème clair et le thème sombre."""
        new_theme = 'dark' if self._current_theme == 'light' else 'light'
        self.ui_manager.set_theme(new_theme)
        self._current_theme = new_theme
        self.on_theme_change(new_theme)
        self.update_theme_icon()

    def _show_about_dialog(self):
        """Affiche la fenêtre À propos"""
        text = (
            f"<p><b>{app_info.APP_NAME}</b></p>"
            f"<p><b>Version: {app_info.VERSION}</b></p>"
        )
        informative_text = (
            f"<p><b>Auteur :</b> {app_info.AUTHOR}</p>"
            f"<p><b>Description :</b><br>{app_info.DESCRIPTION}</p>"
            f"<p><b>Licence :</b> {app_info.LICENSE}</p>"
        )

        if getattr(app_info, "URL", None):
            informative_text += f'<p><b>Site :</b> <a href="{app_info.URL}" style="color:#4682B4;">{app_info.URL}</a></p>'

        show_custom_message_box(
            parent=self,
            level="INFO",
            title="À propos",
            text=text,
            informative_text=informative_text,
            buttons=QMessageBox.StandardButton.Ok
        )

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
