# pylint: disable=no-name-in-module
"""
Module contenant la classe UserSettingsWidget.

Ce widget permet à l'utilisateur de visualiser et de modifier les paramètres
de configuration de l'application, y compris le chemin d'accès au fichier
de base de données (BDD) et le nom d'utilisateur. Il interagit avec le
ConfigManager pour lire et écrire les paramètres dans le fichier config_user.json
et émet des signaux pour notifier les changements critiques.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QFileDialog, QGroupBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import pyqtSignal, Qt, QUrl
from app.config_manager import ConfigManager
from app.db_manager import DBManager
from app.utils import show_custom_message_box

class UserSettingsWidget(QWidget):
    """
    Widget affichant et permettant de modifier les paramètres utilisateur
    stockés dans config_user.json (chemin BDD, thème, nom d'utilisateur).
    """
    theme_changed = pyqtSignal(str)
    db_path_changed = pyqtSignal(str)
    username_changed = pyqtSignal(str)
    restart_requested = pyqtSignal()

    def __init__(self, config_manager: ConfigManager, db_manager: DBManager):
        super().__init__()
        self.config_manager = config_manager
        self.db_manager = db_manager
        self._setup_ui()

    def _setup_ui(self):
        """Génère le container principal du widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(QLabel("<h2>Mes Paramètres</h2>"))
        main_layout.addWidget(self._create_settings_group())
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _create_settings_group(self) -> QGroupBox:
        """Crée la section pour la gestion du chemin de la base de données
        et du nom de l'utilisateur."""
        group_container = QGroupBox()
        vertical_layout = QVBoxLayout(group_container)

        db_path_label = QLabel(f"Chemin de la Base de Données")
        db_path_label.setObjectName("GroupBoxCustomTitle")
        vertical_layout.addWidget(db_path_label)
        current_db_path = self.config_manager.get_db_path() or "Non configuré"
        self.label_db_path = QLabel(f"Chemin actuel: {current_db_path}")
        self.label_db_path.setObjectName("InstructionLabel")
        vertical_layout.addWidget(self.label_db_path)
        horizontal_db_layout = QHBoxLayout()
        self.input_db_path = QLineEdit(current_db_path if current_db_path != "Non configuré" else "")
        self.input_db_path.setPlaceholderText("Sélectionnez le fichier .db...")
        self.input_db_path.setReadOnly(True)
        horizontal_db_layout.addWidget(self.input_db_path)
        btn_browse = QPushButton("Parcourir...")
        btn_browse.setObjectName("FilesActionButton")
        btn_browse.clicked.connect(self._browse_db_file)
        horizontal_db_layout.addWidget(btn_browse)
        vertical_layout.addLayout(horizontal_db_layout)

        vertical_layout.addSpacing(10)

        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        vertical_layout.addWidget(separator1)

        vertical_layout.addSpacing(10)

        user_name_title_label = QLabel("Nom d'Utilisateur")
        user_name_title_label.setObjectName("GroupBoxCustomTitle")
        vertical_layout.addWidget(user_name_title_label)
        system_username = QLabel("Par défaut, c'est le nom d'utilisateur système.")
        system_username.setObjectName("InstructionLabel")
        vertical_layout.addWidget(system_username)
        horizontal_user_layout = QHBoxLayout()
        self.input_username = QLineEdit(self.config_manager.get_user_name())
        self.input_username.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.input_username.returnPressed.connect(self._handle_user_name_change)
        btn_save_user = QPushButton("Enregistrer")
        btn_save_user.setObjectName("PrimaryActionButton")
        btn_save_user.clicked.connect(self._handle_user_name_change)
        horizontal_user_layout.addWidget(self.input_username)
        horizontal_user_layout.addWidget(btn_save_user)
        vertical_layout.addLayout(horizontal_user_layout)

        vertical_layout.addSpacing(10)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        vertical_layout.addWidget(separator2)

        vertical_layout.addSpacing(10)

        app_title_label = QLabel("Gestion des fichiers applicatifs")
        app_title_label.setObjectName("GroupBoxCustomTitle")
        vertical_layout.addWidget(app_title_label)
        app_instructions = QLabel('Accès au dossiers de l\'application, ainsi qu\'au fichier de configuration (format JSON) et au dossier "Logs".')
        app_instructions.setObjectName("InstructionLabel")
        vertical_layout.addWidget(app_instructions)
        horizontal_app_layout = QHBoxLayout()
        btn_open_app_dir = QPushButton("Dossier Application")
        btn_open_app_dir.setObjectName("PrimaryActionButton")
        btn_open_app_dir.clicked.connect(self._open_app_config_dir)
        horizontal_app_layout.addWidget(btn_open_app_dir, stretch=1)
        btn_open_config = QPushButton("config_user.json")
        btn_open_config.setObjectName("PrimaryActionButton")
        btn_open_config.clicked.connect(self._open_config_file)
        horizontal_app_layout.addWidget(btn_open_config, stretch=1)
        btn_open_logs = QPushButton('Dossier des "Logs"')
        btn_open_logs.setObjectName("PrimaryActionButton")
        btn_open_logs.clicked.connect(self._open_logs_folder)
        horizontal_app_layout.addWidget(btn_open_logs, stretch=1)
        vertical_layout.addLayout(horizontal_app_layout)

        return group_container

    def _browse_db_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le chemin du fichier BDD."""
        current_path = self.config_manager.get_db_path()
        start_dir = current_path if current_path and os.path.exists(current_path) else os.path.expanduser("~")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier de Base de Données (.db)",
            start_dir,
            "Fichiers de Base de Données (*.db)"
        )

        if file_path and file_path != self.config_manager.get_db_path():
            self.config_manager.set_db_path(file_path)
            self.input_db_path.setText(file_path)
            self.label_db_path.setText(f"Chemin actuel: {file_path}")
            self.db_path_changed.emit(file_path)
            result = show_custom_message_box(
                    self,
                    'INFO',
                    "Mise à Jour Base de Données",
                    "Le nouveau chemin de la Base de Données a été enregistré.",
                    "Voulez-vous redémarrer l'application maintenant pour appliquer ce changement ?",
                    buttons=['Restart', 'Later']
                )
            if result == QMessageBox.StandardButton.Yes:
                self.restart_requested.emit()
            elif result == QMessageBox.StandardButton.RestoreDefaults:
                self.restart_requested.emit()

            if result == QMessageBox.StandardButton.Yes:
                 self.restart_requested.emit()

    def _handle_user_name_change(self):
        """Met à jour et enregistre le nom d'utilisateur."""
        new_username = self.input_username.text().strip()
        if not new_username:
            show_custom_message_box(
                self,
                'WARNING',
                "Règle de Validation",
                "Le nom d\'utilisateur ne peut pas être vide.",
                buttons=['Ok']
            )
            return

        if new_username != self.config_manager.get_user_name():
            self.config_manager.set_user_name(new_username)
            self.username_changed.emit(new_username)
            success = self.db_manager.update_user_name(new_username)
            if success:
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Sauvegarde Nom Utilisateur Réussie",
                    f"Votre nouveau nom d'utilisateur '{new_username}' a été enregistré.",
                    buttons=['Ok']
                )
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Erreur Sauvegarde Nom Utilisateur",
                    f"Une erreur est survenue lors de la mise à jour de votre nom d'utilisateur '{new_username}'.",
                    "Veuiller regarder le journal d'activité pour plus d\'information.",
                    buttons=['Ok']
                )
        else:
            show_custom_message_box(
                self,
                'INFO',
                "Aucune Modification",
                "Le nom d\'utilisateur est identique à l'existant.",
                buttons=['Ok']
            )

    def _open_app_config_dir(self):
        app_dir = self.config_manager.get_app_config_dir_path()
        if os.path.exists(app_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(app_dir))
        else:
            show_custom_message_box(self, 'ERROR', "Dossier introuvable",
                                    "Le dossier de l'application n'existe pas.",
                                    f"Chemin attendu: {app_dir}", buttons=['Ok'])

    def _open_config_file(self):
        """Ouvre directement le fichier config_user.json."""
        config_path = os.path.join(self.config_manager.get_app_config_dir_path(),
                                self.config_manager.CONFIG_FILE)
        if os.path.exists(config_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(config_path))
        else:
            show_custom_message_box(
                self,
                'ERROR',
                "Fichier introuvable",
                "Le fichier config_user.json n'existe pas.",
                f"Chemin attendu: {config_path}",
                buttons=['Ok']
            )

    def _open_logs_folder(self):
        """Ouvre le dossier des logs dans l'explorateur."""
        logs_path = os.path.join(self.config_manager.get_app_config_dir_path(), "Logs")
        if os.path.exists(logs_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(logs_path))
        else:
            show_custom_message_box(
                self,
                'ERROR',
                "Dossier introuvable",
                "Le dossier des logs n'existe pas.",
                f"Chemin attendu: {logs_path}",
                buttons=['Ok']
            )