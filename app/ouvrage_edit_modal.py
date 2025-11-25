# pylint: disable=no-name-in-module
"""
Contient la modale (OuvrageEditModal) permettant d'éditer les informations
d'un ouvrage existant. Gère le pré-remplissage des champs, la modification
des données et la validation.
Refactoré pour utiliser le mixin partagé sans aucune régression.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox,
    QGroupBox, QFormLayout, QLabel
)
from PyQt6.QtCore import pyqtSignal
import resources_rc # pylint: disable=unused-import
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.utils import show_custom_message_box, CoverPathManager
from app.ouvrage_form_common import OuvrageFormMixin

class OuvrageEditModal(QDialog, OuvrageFormMixin):
    """
    Modale pour l'édition et la suppression d'un ouvrage existant.
    """
    ouvrage_updated = pyqtSignal()
    ouvrage_deleted = pyqtSignal()

    def __init__(self, db_manager: DBManager, config_manager: ConfigManager, ouvrage_id: int, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.ouvrage_id_to_edit = ouvrage_id
        self.original_ouvrage_data: Dict[str, Any] = {}

        self.ouvrage_data = self.db_manager.get_ouvrage_details(ouvrage_id)
        if not self.ouvrage_data:
            show_custom_message_box(
                self,
                'ERROR',
                'Erreur Récupération Ouvrage',
                'Ouvrage introuvable dans la base de données.'
            )
            self.reject()
            return

        self.setWindowTitle(f"Édition: {self.ouvrage_data.get('titre', f'ID: {ouvrage_id}')}")
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
        # content_layout.addWidget(self._create_left_column(), 1)

        left_column = self._create_left_column()
        left_layout = left_column.layout()
        group_system = QGroupBox()
        group_system.setObjectName("GroupBoxModal")
        title_system = QLabel("Informations système")
        title_system.setObjectName("GroupBoxCustomTitleSystem")
        layout_system = QFormLayout(group_system)
        self.label_date_creation = QLabel()
        self.label_cree_par_nom = QLabel()
        self.label_date_modification = QLabel()
        self.label_modifie_par_nom = QLabel()
        layout_system.addRow(title_system)
        layout_system.addRow("Date de création :", self.label_date_creation)
        layout_system.addRow("Créé par :", self.label_cree_par_nom)
        layout_system.addRow("Date de modification :", self.label_date_modification)
        layout_system.addRow("Modifié par :", self.label_modifie_par_nom)
        left_layout.addWidget(group_system)

        content_layout.addWidget(left_column, 1)
        content_layout.addWidget(self._create_middle_column(), 1)
        content_layout.addWidget(self._create_right_column(), 2)

        main_layout.addLayout(content_layout)

        # Footer spécifique (édition + suppression)
        self._setup_footer(main_layout)

        # Connexions communes + spécifiques
        self._setup_common_connections()

        # Chargement initial des listes déroulantes
        self._load_classifications_data()
        self._load_illustration()
        self._load_periodes()
        self._load_reliures()
        self._load_localisations()

        # Chargement des données de l'ouvrage (y compris sélection combos)
        self._load_ouvrage_data()

        # Aperçus couverture initiaux
        self._load_cover_preview(False)
        self._load_cover_preview(True)

        self.adjustSize()

    def _setup_footer(self, main_layout: QVBoxLayout):
        """Met en place la barre de boutons d'action (Enregistrer, Supprimer)."""
        self.btn_save = QPushButton("Enregistrer les modifications")
        self.btn_save.setObjectName("EditActionButton")

        self.btn_delete = QPushButton("Supprimer cet Ouvrage")
        self.btn_delete.setObjectName("DangerActionButton")

        footer_content_layout = QHBoxLayout()
        footer_content_layout.setContentsMargins(0, 0, 0, 0)
        footer_content_layout.setSpacing(15)
        footer_content_layout.addStretch(1)
        footer_content_layout.addWidget(self.btn_save)
        footer_content_layout.addWidget(self.btn_delete)
        footer_content_layout.addStretch(1)

        footer_widget = QWidget()
        footer_widget.setLayout(footer_content_layout)

        main_layout.addSpacing(15)
        main_layout.addWidget(footer_widget)

        # Connexions spécifiques
        self.btn_save.clicked.connect(self._handle_save_ouvrage)
        self.btn_delete.clicked.connect(self._handle_delete_ouvrage)

    # --- Chargement des données de l'ouvrage ---

    def _load_ouvrage_data(self):
        """
        Charge les données de l'ouvrage pour l'édition et sélectionne les valeurs
        correctes dans les listes déroulantes (y compris les dépendances).
        """
        data = self.ouvrage_data
        self.original_ouvrage_data = data

        # --- Colonne gauche ---
        self.input_auteur.setText(data.get('auteur', ''))
        self.input_auteur_2.setText(data.get('auteur_2', ''))
        self.input_titre.setText(data.get('titre', ''))
        self.input_sous_titre.setText(data.get('sous_titre', ''))
        self.input_titre_original.setText(data.get('titre_original', ''))
        self.input_cycle.setText(data.get('cycle', ''))
        self.input_tome.setText(str(data.get('tome', '')) if data.get('tome') else '')
        # 1. Illustration: Sélectionne l'illustration et force le chargement des genres
        self._set_combo_value(self.combo_illustration, data.get('id_illustration'))
        if data.get('id_illustration') is not None and self.combo_illustration.currentIndex() > 0:
            self._handle_categorie_change(self.combo_illustration.currentIndex())

        # --- Colonne milieu ---
        # 1. Catégorie: Sélectionne la catégorie et force le chargement des genres
        self._set_combo_value(self.combo_categorie, data.get('id_categorie'))
        if data.get('id_categorie') is not None and self.combo_categorie.currentIndex() > 0:
            self._handle_categorie_change(self.combo_categorie.currentIndex())

        # 2. Genre: Sélectionne le genre et force le chargement des sous-genres
        self._set_combo_value(self.combo_genre, data.get('id_genre'))
        if data.get('id_genre') is not None and self.combo_genre.currentIndex() > 0:
            self._handle_genre_change(self.combo_genre.currentIndex())

        # 3. Sous-genre: Sélectionne le sous-genre
        self._set_combo_value(self.combo_sous_genre, data.get('id_sous_genre'))

        # Autres Combos
        self._set_combo_value(self.combo_periode, data.get('id_periode'))

        self.input_edition.setText(data.get('edition', ''))
        self.input_collection.setText(data.get('collection', ''))
        self.input_edition_annee.setText(data.get('edition_annee', ''))
        self.input_edition_numero.setText(data.get('edition_numero', ''))
        self.input_edition_premiere_annee.setText(data.get('edition_premiere_annee', ''))
        self.input_isbn.setText(data.get('isbn', ''))

        self._set_combo_value(self.combo_reliure, data.get('id_reliure'))
        self.input_nombre_page.setText(str(data.get('nombre_page', '')) if data.get('nombre_page') else '')
        self.input_dimensions.setText(data.get('dimension', ''))
        self._set_combo_value(self.combo_localisation, data.get('id_localisation'))
        self.input_localisation_details.setText(data.get('localisation_details', ''))

        # --- Colonne droite ---
        self.input_resume.setText(data.get('resume', ''))
        self.input_remarques.setText(data.get('remarques', ''))

        # Couvertures
        self.input_couv_prem_chemin.setText(
            CoverPathManager.normalize(data.get('couverture_premiere_chemin', ''), self.config_manager.get_db_path())
        )
        self.input_couv_prem_location.setText(data.get('couverture_premiere_emplacement', ''))
        self.input_couv_quat_chemin.setText(
            CoverPathManager.normalize(data.get('couverture_quatrieme_chemin', ''), self.config_manager.get_db_path())
        )
        self.input_couv_quat_location.setText(data.get('couverture_quatrieme_emplacement', ''))

        # Informations système
        self.label_date_creation.setText(data.get('date_creation', ''))
        self.label_cree_par_nom.setText(data.get('cree_par_nom', ''))
        self.label_date_modification.setText(data.get('date_modification', ''))
        self.label_modifie_par_nom.setText(data.get('modifie_par_nom', ''))

    def _handle_save_ouvrage(self):
        """Appelle la méthode de mise à jour du DBManager."""
        data = self._collect_data()
        if data is None:
            return

        success, message = self.db_manager.update_ouvrage(self.ouvrage_id_to_edit, data)

        if success:
            show_custom_message_box(
                self,
                'SUCCESS',
                'Mise à jour Ouvrage Réussie',
                message
            )
            self.ouvrage_updated.emit()
            self.accept()
        else:
            show_custom_message_box(
                self,
                'ERROR',
                'Erreur Mise à jour Ouvrage',
                message
            )

    def _handle_delete_ouvrage(self):
        """Gère la suppression de l'ouvrage sélectionné."""
        titre = self.input_titre.text()

        reply = QMessageBox.question(
            self, "Confirmation Suppression",
            f"Êtes-vous sûr de vouloir supprimer définitivement l'ouvrage '<b>{titre}</b>' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_ouvrage(self.ouvrage_id_to_edit)

            if success:
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    'Suppression Ouvrage Réussie',
                    message
                )
                self.ouvrage_deleted.emit()
                self.accept()
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    'Erreur Suppression Ouvrage',
                    message
                )
