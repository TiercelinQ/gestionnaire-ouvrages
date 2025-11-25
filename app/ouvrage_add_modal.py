# pylint: disable=no-name-in-module
"""
Contient la modale (OuvrageAddModal) permettant à l'utilisateur d'ajouter un nouvel ouvrage.
Gère la saisie de tous les champs, la validation des données et l'aperçu des images de couverture.
Refactoré pour utiliser le mixin partagé sans aucune régression d'UI ou de comportement.
"""


from typing import Optional
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
import resources_rc # pylint: disable=unused-import
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.utils import show_custom_message_box
from app.ouvrage_form_common import OuvrageFormMixin

class OuvrageAddModal(QDialog, OuvrageFormMixin):
    """
    Modale pour l'ajout d'un nouvel ouvrage.
    """
    ouvrage_updated = pyqtSignal()

    def __init__(self, db_manager: DBManager, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config_manager = config_manager

        self.setWindowTitle("Ajouter un Nouvel Ouvrage")
        self.setModal(True)
        self.setObjectName("OuvrageModal")
        self.adjustSize()
        screen = self.screen().availableGeometry()
        self.setMaximumSize(int(screen.width() * 0.9), int(screen.height() * 0.9))

        main_layout = QVBoxLayout(self)

        # Champs et colonnes
        self._create_input_fields()

        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        content_layout.addWidget(self._create_left_column(), 1)
        content_layout.addWidget(self._create_middle_column(), 1)
        content_layout.addWidget(self._create_right_column(), 2)
        main_layout.addLayout(content_layout)

        # Footer spécifique (ajout)
        self._setup_footer(main_layout)

        # Connexions communes
        self._setup_common_connections()

        # Chargement des données des listes (combos)
        self._load_classifications_data()
        self._load_illustration()
        self._load_periodes()
        self._load_reliures()
        self._load_localisations()

        # Aperçus couverture initiaux
        self._load_cover_preview(False)
        self._load_cover_preview(True)

        self.adjustSize()

    def _setup_footer(self, main_layout: QVBoxLayout):
        """Met en place la barre de boutons d'action (Enregistrer / Annuler)."""
        self.btn_save = QPushButton("Ajouter l'Ouvrage")
        self.btn_save.setObjectName("EditActionButton")

        footer_content_layout = QHBoxLayout()
        footer_content_layout.setContentsMargins(0, 0, 0, 0)
        footer_content_layout.setSpacing(15)
        footer_content_layout.addStretch(1)
        footer_content_layout.addWidget(self.btn_save)
        footer_content_layout.addStretch(1)

        footer_widget = QWidget()
        footer_widget.setLayout(footer_content_layout)

        main_layout.addSpacing(15)
        main_layout.addWidget(footer_widget)

        # Connexion du bouton de sauvegarde
        self.btn_save.clicked.connect(self._handle_save_ouvrage)

    def _handle_save_ouvrage(self):
        """Appelle la méthode d'ajout du DBManager."""
        data = self._collect_data()
        if data is None:
            return

        success, message = self.db_manager.add_ouvrage(data)

        if success:
            show_custom_message_box(
                self,
                'SUCCESS',
                'Enregistrement Ouvrage Réussi',
                message
            )
            self.ouvrage_updated.emit()
            self.accept()
        else:
            show_custom_message_box(
                self,
                'ERROR',
                'Erreur Enregistrement Ouvrage',
                message
            )
