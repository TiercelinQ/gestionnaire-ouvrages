# pylint: disable=no-name-in-module
"""
Logique et widgets partagés entre les modales d'ajout et d'édition des ouvrages.
Conserve strictement la mise en page, les widgets, les placeholders, tooltips, validators,
et comportements, afin d'éviter toute régression.
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFileDialog,
    QComboBox, QPushButton, QFormLayout, QGroupBox, QFrame,
    QTextEdit, QSizePolicy, QWidget, QApplication
)
from PyQt6.QtCore import Qt, QDateTime, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent, QIntValidator
import resources_rc # pylint: disable=unused-import
from app.db_manager import DBManager
from app.utils import show_custom_message_box, make_relative_cover_path

PREVIEW_MAX_SIZE = QSize(150, 250)
INITIAL_MIN_WIDTH = 150
INITIAL_MIN_HEIGHT = 200

class ClickableLabel(QLabel):
    """Un QLabel qui émet un signal au clic. Utilisé pour l'aperçu de la couverture."""
    clicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent): # pylint: disable=invalid-name
        """Émet le signal au clic de la souris."""
        self.clicked.emit()
        super().mousePressEvent(event)


class CoverPreviewModal(QDialog):
    """
    Modale simple pour afficher une image en grand format, tout en respectant son ratio.
    """
    def __init__(self, image_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Aperçu de la Couverture")
        self.setModal(True)
        self.setMinimumSize(400, 600)

        main_layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.image_label)

        self.image_path = image_path
        self.load_image()

    def load_image(self):
        """Charge l'image à partir du chemin et l'adapte à la taille de la modale."""
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                screen_size = QApplication.primaryScreen().size()
                max_width = screen_size.width() * 0.8
                max_height = screen_size.height() * 0.8

                scaled_pixmap = pixmap.scaled(
                    int(max_width), int(max_height),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.resize(scaled_pixmap.size() + QSize(20, 20))
            else:
                self.image_label.setText("Erreur: Fichier image invalide.")
        else:
            self.image_label.setText("Erreur: Fichier image non trouvé.")


class PlainTextEdit(QTextEdit):
    """PlainTextEdit qui n'accepte que du texte brut lors du collage."""
    def insertFromMimeData(self, source):
        # On ignore tout formatage et on insère uniquement le texte brut
        self.insertPlainText(source.text())


class OuvrageFormMixin:
    """
    Mixin contenant toute la logique et les widgets communs
    aux modales d'ajout et d'édition, pour éviter toute duplication.
    Les classes concrètes doivent:
      - définir self.db_manager dans __init__
      - créer un main_layout et y intégrer les colonnes
      - définir un footer spécifique (boutons d'action)
    """

    # Champs du formulaire (initialisés dans _create_input_fields)
    input_auteur: QLineEdit
    input_auteur_2: QLineEdit
    input_titre: QLineEdit
    input_sous_titre: QLineEdit
    input_titre_original: QLineEdit
    input_cycle: QLineEdit
    input_tome: QLineEdit
    combo_illustration: QComboBox
    combo_categorie: QComboBox
    combo_genre: QComboBox
    combo_sous_genre: QComboBox
    combo_periode: QComboBox
    input_edition: QLineEdit
    input_collection: QLineEdit
    input_edition_annee: QLineEdit
    input_edition_numero: QLineEdit
    input_edition_premiere_annee: QLineEdit
    input_isbn: QLineEdit
    combo_reliure: QComboBox
    input_nombre_page: QLineEdit
    input_dimensions: QLineEdit
    combo_localisation: QComboBox
    input_localisation_details: QLineEdit
    input_resume: PlainTextEdit
    input_remarques: PlainTextEdit
    input_couv_prem_chemin: QLineEdit
    label_couv_prem_preview: ClickableLabel
    input_couv_prem_location: QLineEdit
    input_couv_quat_chemin: QLineEdit
    label_couv_quat_preview: ClickableLabel
    input_couv_quat_location: QLineEdit

    db_manager: DBManager

    def _create_input_fields(self):
        """Initialise tous les champs de saisie (LineEdit, ComboBox, TextEdit) avec les mêmes validators, tooltips et placeholders."""
        annee_courante = QDateTime.currentDateTime().date().year()
        min_annee = 0
        max_annee = annee_courante + 1

        # Colonne 1
        self.input_auteur = QLineEdit()
        self.input_auteur_2 = QLineEdit()
        self.input_titre = QLineEdit()
        self.input_sous_titre = QLineEdit()
        self.input_titre_original = QLineEdit()
        self.input_cycle = QLineEdit()
        self.input_tome = QLineEdit()
        tome_validator = QIntValidator(0, 999, self.input_tome)
        self.input_tome.setValidator(tome_validator)
        self.input_tome.setMaxLength(3)
        self.input_tome.setPlaceholderText("0 à 999 (Vide si Volume Unique)")
        self.combo_illustration = QComboBox()

        # Colonne 2
        self.combo_categorie = QComboBox()
        self.combo_genre = QComboBox()
        self.combo_sous_genre = QComboBox()
        self.combo_periode = QComboBox()

        self.input_edition = QLineEdit()
        self.input_collection = QLineEdit()

        self.input_edition_annee = QLineEdit()
        edition_annee_validator = QIntValidator(min_annee, max_annee, self.input_edition_annee)
        self.input_edition_annee.setValidator(edition_annee_validator)
        self.input_edition_annee.setMaxLength(4)
        self.input_edition_annee.setPlaceholderText(f"Ex: {annee_courante}")
        self.input_edition_annee.setToolTip(
            f"Veuillez saisir une année comprise entre entre {min_annee} et {max_annee}."
        )

        self.input_edition_numero = QLineEdit()

        self.input_edition_premiere_annee = QLineEdit()
        edition_premiere_annee_validator = QIntValidator(min_annee, max_annee, self.input_edition_premiere_annee)
        self.input_edition_premiere_annee.setValidator(edition_premiere_annee_validator)
        self.input_edition_premiere_annee.setMaxLength(4)
        self.input_edition_premiere_annee.setPlaceholderText(f"Ex: {annee_courante}")
        self.input_edition_premiere_annee.setToolTip(
            f"Veuillez saisir une année comprise entre entre {min_annee} et {max_annee}."
        )

        self.input_isbn = QLineEdit()

        self.combo_reliure = QComboBox()

        self.input_nombre_page = QLineEdit()
        nombre_page_validator = QIntValidator(0, 16000, self.input_nombre_page)
        self.input_nombre_page.setValidator(nombre_page_validator)
        self.input_nombre_page.setMaxLength(5)
        self.input_nombre_page.setPlaceholderText("Ex: 320")
        self.input_nombre_page.setToolTip("Veuillez saisir un nombre compris entre 0 et 16000.")

        self.input_dimensions = QLineEdit()
        self.combo_localisation = QComboBox()
        self.input_localisation_details = QLineEdit()
        self.input_localisation_details.setPlaceholderText("Etagère 1...")

        # Colonne 3
        self.input_resume = PlainTextEdit()
        self.input_resume.setFixedHeight(100)

        self.input_remarques = PlainTextEdit()
        self.input_remarques.setFixedHeight(100)

        # Couvertures (avant)
        self.input_couv_prem_chemin = QLineEdit()
        self.input_couv_prem_chemin.setReadOnly(True)
        self.input_couv_prem_chemin.setHidden(True)

        self.label_couv_prem_preview = ClickableLabel("Aperçu")
        self.label_couv_prem_preview.setFixedSize(INITIAL_MIN_WIDTH, INITIAL_MIN_HEIGHT)
        self.label_couv_prem_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_couv_prem_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label_couv_prem_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.label_couv_prem_preview.setFrameShadow(QFrame.Shadow.Sunken)

        self.input_couv_prem_location = QLineEdit()
        self.input_couv_prem_location.setHidden(True)

        # Couvertures (arrière)
        self.input_couv_quat_chemin = QLineEdit()
        self.input_couv_quat_chemin.setReadOnly(True)
        self.input_couv_quat_chemin.setHidden(True)

        self.label_couv_quat_preview = ClickableLabel("Aperçu")
        self.label_couv_quat_preview.setFixedSize(INITIAL_MIN_WIDTH, INITIAL_MIN_HEIGHT)
        self.label_couv_quat_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_couv_quat_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label_couv_quat_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.label_couv_quat_preview.setFrameShadow(QFrame.Shadow.Sunken)

        self.input_couv_quat_location = QLineEdit()
        self.input_couv_quat_location.setHidden(True)

    @staticmethod
    def make_required_label(text: str) -> QLabel:
        return QLabel(f"{text} <span style='color:red; font-weight:bold;'>*</span>")

    def _create_left_column(self) -> QWidget:
        """Crée le widget de la colonne de gauche (Infos Générales & Caractéristique)."""
        target_min_width = 400
        left_column_widget = QWidget()
        left_column_widget.setMinimumWidth(target_min_width)
        left_layout = QVBoxLayout(left_column_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        group_info = QGroupBox()
        group_info.setObjectName("GroupBoxModal")
        title_info = QLabel("Informations Générales")
        title_info.setObjectName("GroupBoxCustomTitle")
        layout_info = QFormLayout(group_info)
        layout_info.addRow(title_info)
        label_auteur = self.make_required_label("Auteur")
        layout_info.addRow(label_auteur, self.input_auteur)
        label_auteur_2 = QLabel("Auteur 2:")
        layout_info.addRow(label_auteur_2, self.input_auteur_2)
        label_titre = self.make_required_label("Titre")
        layout_info.addRow(label_titre, self.input_titre)
        label_sous_titre = QLabel("Sous-Titre:")
        layout_info.addRow(label_sous_titre, self.input_sous_titre)
        left_layout.addWidget(group_info)

        group_caract = QGroupBox()
        group_caract.setObjectName("GroupBoxModal")
        title_caract = QLabel("Caractéristiques")
        title_caract.setObjectName("GroupBoxCustomTitle")
        layout_caract = QFormLayout(group_caract)
        layout_caract.addRow(title_caract)
        label_titre_original = QLabel("Titre Original:")
        layout_caract.addRow(label_titre_original, self.input_titre_original)
        label_cycle = QLabel("Cycle:")
        layout_caract.addRow(label_cycle, self.input_cycle)
        label_tome = QLabel("Tome:")
        layout_caract.addRow(label_tome, self.input_tome)
        label_illustration = QLabel("Illustration:")
        layout_caract.addRow(label_illustration, self.combo_illustration)
        left_layout.addWidget(group_caract)

        left_layout.addStretch()
        return left_column_widget

    def _create_middle_column(self) -> QWidget:
        """Crée le widget de la colonne des classifications et des formats."""
        target_min_width = 400
        middle_column_widget = QWidget()
        middle_column_widget.setMinimumWidth(target_min_width)
        middle_layout = QVBoxLayout(middle_column_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)

        group_class = QGroupBox()
        group_class.setObjectName("GroupBoxModal")
        title_class = QLabel("Classification")
        title_class.setObjectName("GroupBoxCustomTitle")
        layout_class = QFormLayout(group_class)
        layout_class.addRow(title_class)
        label_categorie = QLabel("Catégorie:")
        layout_class.addRow(label_categorie, self.combo_categorie)
        label_genre = QLabel("Genre:")
        layout_class.addRow(label_genre, self.combo_genre)
        label_sous_genre = QLabel("Sous-genre:")
        layout_class.addRow(label_sous_genre, self.combo_sous_genre)
        label_periode = QLabel("Période:")
        layout_class.addRow(label_periode, self.combo_periode)
        middle_layout.addWidget(group_class)

        group_pub = QGroupBox()
        group_pub.setObjectName("GroupBoxModal")
        title_pub = QLabel("Publication")
        title_pub.setObjectName("GroupBoxCustomTitle")
        layout_pub = QFormLayout(group_pub)
        layout_pub.addRow(title_pub)
        label_edition = QLabel("Édition :")
        layout_pub.addRow(label_edition, self.input_edition)
        label_collection = QLabel("Collection:")
        layout_pub.addRow(label_collection, self.input_collection)
        label_annee_edition = QLabel("Année Édition:")
        layout_pub.addRow(label_annee_edition, self.input_edition_annee)
        label_num_edition = QLabel("N° Édition:")
        layout_pub.addRow(label_num_edition, self.input_edition_numero)
        label_annee_prem_edition = QLabel("Année 1ère Édition:")
        layout_pub.addRow(label_annee_prem_edition, self.input_edition_premiere_annee)
        label_isbn = QLabel("ISBN:")
        layout_pub.addRow(label_isbn, self.input_isbn)
        middle_layout.addWidget(group_pub)

        group_form = QGroupBox()
        group_form.setObjectName("GroupBoxModal")
        title_form = QLabel("Format et Localisation")
        title_form.setObjectName("GroupBoxCustomTitle")
        layout_form = QFormLayout(group_form)
        layout_form.addRow(title_form)
        label_reliure = QLabel("Reliure:")
        layout_form.addRow(label_reliure, self.combo_reliure)
        label_num_pages = QLabel("Nombre Pages:")
        layout_form.addRow(label_num_pages, self.input_nombre_page)
        label_dimensions = QLabel("Dimensions:")
        layout_form.addRow(label_dimensions, self.input_dimensions)
        label_localisation = QLabel("Localisation:")
        layout_form.addRow(label_localisation, self.combo_localisation)
        label_localisation_details = QLabel("Localisation Détails:")
        layout_form.addRow(label_localisation_details, self.input_localisation_details)
        middle_layout.addWidget(group_form)

        middle_layout.addStretch()
        return middle_column_widget

    def _create_right_column(self) -> QWidget:
        """Crée le widget de la colonne du résumé et des couvertures, avec les couvertures côte-à-côte."""
        target_min_width = 600
        right_column_widget = QWidget()
        right_column_widget.setMinimumWidth(target_min_width)
        right_layout = QVBoxLayout(right_column_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Contenu (Résumé & Remarques)
        group_cont = QGroupBox()
        group_cont.setObjectName("GroupBoxModal")
        title_cont = QLabel("Contenu")
        title_cont.setObjectName("GroupBoxCustomTitle")
        layout_cont = QFormLayout(group_cont)
        layout_cont.addRow(title_cont)
        label_resume = QLabel("Résumé:")
        layout_cont.addRow(label_resume, self.input_resume)
        label_remarques = QLabel("Remarques:")
        layout_cont.addRow(label_remarques, self.input_remarques)
        right_layout.addWidget(group_cont)

        # 2. Groupe des Couvertures
        group_couverture = QGroupBox()
        group_couverture.setObjectName("GroupBoxModal")
        main_cover_layout = QHBoxLayout(group_couverture)
        main_cover_layout.setSpacing(20)

        # --- SECTION 1 : 1ère de Couverture ---
        section_prem = QVBoxLayout()
        title_prem_couv = QLabel("1re de Couverture")
        title_prem_couv.setObjectName("GroupBoxCustomTitle")
        section_prem.addWidget(title_prem_couv)

        btn_browse_prem = QPushButton("Parcourir")
        btn_browse_prem.setObjectName("FilesActionButton")
        btn_browse_prem.clicked.connect(lambda: self._browse_cover(False))

        btn_remove_prem = QPushButton("Retirer")
        btn_remove_prem.setObjectName("SecondaryActionButton")
        btn_remove_prem.clicked.connect(lambda: self._remove_cover(False))

        # Layout vertical pour empiler les deux boutons
        v_layout_buttons_prem = QVBoxLayout()
        v_layout_buttons_prem.addWidget(btn_browse_prem)
        v_layout_buttons_prem.addWidget(btn_remove_prem)

        # Layout horizontal pour mettre (bloc boutons + champ texte)
        h_layout_file_prem = QHBoxLayout()
        h_layout_file_prem.addLayout(v_layout_buttons_prem)
        h_layout_file_prem.addWidget(self.input_couv_prem_chemin)

        section_prem.addLayout(h_layout_file_prem)
        section_prem.addWidget(self.label_couv_prem_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        section_prem.addStretch()

        main_cover_layout.addLayout(section_prem)

        # --- SÉPARATEUR VISUEL VERTICAL ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_cover_layout.addWidget(separator)

        # --- SECTION 2 : 4ème de Couverture ---
        section_quat = QVBoxLayout()
        title_quat_couv = QLabel("4e de Couverture")
        title_quat_couv.setObjectName("GroupBoxCustomTitle")
        section_quat.addWidget(title_quat_couv)

        btn_browse_quat = QPushButton("Parcourir")
        btn_browse_quat.setObjectName("FilesActionButton")
        btn_browse_quat.clicked.connect(lambda: self._browse_cover(True))

        btn_remove_quat = QPushButton("Retirer")
        btn_remove_quat.setObjectName("SecondaryActionButton")
        btn_remove_quat.clicked.connect(lambda: self._remove_cover(True))

        # Layout vertical pour empiler les deux boutons
        v_layout_buttons_quat = QVBoxLayout()
        v_layout_buttons_quat.addWidget(btn_browse_quat)
        v_layout_buttons_quat.addWidget(btn_remove_quat)

        # Layout horizontal pour mettre (bloc boutons + champ texte)
        h_layout_file_quat = QHBoxLayout()
        h_layout_file_quat.addLayout(v_layout_buttons_quat)
        h_layout_file_quat.addWidget(self.input_couv_quat_chemin)

        section_quat.addLayout(h_layout_file_quat)
        section_quat.addWidget(self.label_couv_quat_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        section_quat.addStretch()

        main_cover_layout.addLayout(section_quat)

        right_layout.addWidget(group_couverture)
        right_layout.addStretch()

        return right_column_widget

    def _setup_common_connections(self):
        """Connecte les signaux communs des éléments interactifs."""
        # Combos dépendants
        self.combo_categorie.currentIndexChanged.connect(self._handle_categorie_change)
        self.combo_genre.currentIndexChanged.connect(self._handle_genre_change)

        # Couvertures
        self.label_couv_prem_preview.clicked.connect(lambda: self._handle_preview_cover(False))
        self.input_couv_prem_chemin.textChanged.connect(lambda text: self._load_cover_preview(False))
        self.label_couv_quat_preview.clicked.connect(lambda: self._handle_preview_cover(True))
        self.input_couv_quat_chemin.textChanged.connect(lambda text: self._load_cover_preview(True))

    # --- Helpers combos ---
    def _clear_combo(self, combo: QComboBox, default_text: str = "--- (Sélectionner) ---"):
        """Vider et réinitialiser la QComboBox."""
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(default_text, userData=None)
        combo.blockSignals(False)

    def _set_combo_value(self, combo: QComboBox, value_id: Optional[int]):
        """Sélectionne l'élément dans un QComboBox par son userData (ID)."""
        if value_id is None:
            combo.setCurrentIndex(0)
            return
        for i in range(combo.count()):
            if combo.itemData(i) == value_id:
                combo.setCurrentIndex(i)
                return

    def _load_classifications_data(self):
        """Charge toutes les catégories et initialise les listes déroulantes Genre et Sous-genre."""
        self._clear_combo(self.combo_categorie)
        categories = self.db_manager.get_all_categories()
        for c_id, c_name in categories:
            self.combo_categorie.addItem(c_name, userData=c_id)

        self._clear_combo(self.combo_genre)
        self._clear_combo(self.combo_sous_genre)

    def _handle_categorie_change(self, index: int):
        """Charge les genres basés sur la catégorie sélectionnée."""
        self._clear_combo(self.combo_genre)
        self._clear_combo(self.combo_sous_genre)

        if index > 0:
            category_id = self.combo_categorie.currentData()
            genres = self.db_manager.get_genres_by_category_id(category_id)
            for g_id, g_name in genres:
                self.combo_genre.addItem(g_name, userData=g_id)

    def _handle_genre_change(self, index: int):
        """Charge les sous-genres basés sur le genre sélectionné."""
        self._clear_combo(self.combo_sous_genre)

        if index > 0:
            genre_id = self.combo_genre.currentData()
            subgenres = self.db_manager.get_subgenres_by_genre_id(genre_id)
            for sg_id, sg_name in subgenres:
                self.combo_sous_genre.addItem(sg_name, userData=sg_id)

    def _load_illustration(self):
        """Charge les données des illustrations."""
        self._clear_combo(self.combo_illustration)
        illustrations = self.db_manager.get_all_illustrations()
        for illustration_id, illustration_nom in illustrations:
            self.combo_illustration.addItem(illustration_nom, userData=illustration_id)

    def _load_periodes(self):
        """Charge les données des périodes."""
        self._clear_combo(self.combo_periode)
        periodes = self.db_manager.get_all_periodes()
        for periode_id, periode_nom in periodes:
            self.combo_periode.addItem(periode_nom, userData=periode_id)

    def _load_reliures(self):
        """Charge les données des reliures."""
        self._clear_combo(self.combo_reliure)
        reliures = self.db_manager.get_all_reliures()
        for reliure_id, reliure_nom in reliures:
            self.combo_reliure.addItem(reliure_nom, userData=reliure_id)

    def _load_localisations(self):
        """Charge les données des localisation."""
        self._clear_combo(self.combo_localisation)
        localisations = self.db_manager.get_all_localisations()
        for localisation_id, localisation_nom in localisations:
            self.combo_localisation.addItem(localisation_nom, userData=localisation_id)

    # --- Couvertures ---
    def _browse_cover(self, is_back_cover: bool):
        """Ouvre une boîte de dialogue pour sélectionner le chemin de l'image de couverture."""
        if is_back_cover:
            title = "Sélectionner la 4ème de Couverture"
            input_chemin = self.input_couv_quat_chemin
        else:
            title = "Sélectionner la Couverture Avant"
            input_chemin = self.input_couv_prem_chemin
            input_chemin.setReadOnly(False)

        file_path, _ = QFileDialog.getOpenFileName(
            self, title, os.path.expanduser("~"),
            "Fichiers Image (*.png *.jpg *.jpeg *.webp)"
        )

        if file_path:
            input_chemin.setText(file_path)
            input_chemin.setReadOnly(True)
            input_chemin.setToolTip(file_path)
            self._load_cover_preview(is_back_cover)
        else:
            input_chemin.setReadOnly(True)

    def _load_cover_preview(self, is_back_cover: bool):
        """Affiche la miniature de l'image de couverture dans le QLabel."""
        if is_back_cover:
            input_chemin = self.input_couv_quat_chemin
            label_preview = self.label_couv_quat_preview
            default_text = "Cliquez pour ajouter/modifier la 4ème de couverture"
        else:
            input_chemin = self.input_couv_prem_chemin
            label_preview = self.label_couv_prem_preview
            default_text = "Cliquez pour ajouter/modifier la 1ère de couverture"

        chemin = input_chemin.text().strip()

        if chemin and os.path.exists(chemin):
            pixmap = QPixmap(chemin)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    PREVIEW_MAX_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                label_preview.setPixmap(scaled_pixmap)
                label_preview.setText("")
            else:
                label_preview.setText("Image invalide")
                label_preview.setPixmap(QPixmap())
        else:
            label_preview.setText(default_text)
            label_preview.setPixmap(QPixmap())

    def _handle_preview_cover(self, is_back_cover: bool):
        """Ouvre la modale d'aperçu de la couverture en grand format."""
        if is_back_cover:
            path = self.input_couv_quat_chemin.text().strip()
        else:
            path = self.input_couv_prem_chemin.text().strip()

        if path and os.path.exists(path):
            modal = CoverPreviewModal(path, parent=self)
            modal.exec()
        else:
            show_custom_message_box(
                self,
                'WARNING',
                'Aperçu Couverture',
                'Aucun chemin de couverture valide n\'est spécifié.'
            )

    def _remove_cover(self, is_back_cover: bool):
        """Retire l'image de couverture sélectionnée et réinitialise l'aperçu."""
        if is_back_cover:
            input_chemin = self.input_couv_quat_chemin
        else:
            input_chemin = self.input_couv_prem_chemin

        # Vider le champ chemin
        input_chemin.clear()
        input_chemin.setToolTip("")
        input_chemin.setReadOnly(True)

    # --- Collecte des données ---
    def _collect_data(self) -> Optional[Dict[str, Any]]:
        """Collecte les données du formulaire, avec validation obligatoire Titre + Auteur."""
        data = {
            'titre': self.input_titre.text().strip(),
            'sous_titre': self.input_sous_titre.text().strip() or None,
            'auteur': self.input_auteur.text().strip() or None,
            'auteur_2': self.input_auteur_2.text().strip() or None,
            'titre_original': self.input_titre_original.text().strip() or None,
            'cycle': self.input_cycle.text().strip() or None,
            'tome': self.input_tome.text().strip() or None,
            'id_illustration': self.combo_illustration.currentData(),
            'id_categorie': self.combo_categorie.currentData(),
            'id_genre': self.combo_genre.currentData(),
            'id_sous_genre': self.combo_sous_genre.currentData(),
            'id_periode': self.combo_periode.currentData(),
            'edition': self.input_edition.text().strip() or None,
            'collection': self.input_collection.text().strip() or None,
            'edition_annee': self.input_edition_annee.text().strip() or None,
            'edition_numero': self.input_edition_numero.text().strip() or None,
            'edition_premiere_annee': self.input_edition_premiere_annee.text().strip() or None,
            'isbn': self.input_isbn.text().strip() or None,
            'id_reliure': self.combo_reliure.currentData(),
            'nombre_page': self.input_nombre_page.text().strip() or None,
            'dimension': self.input_dimensions.text().strip() or None,
            'id_localisation': self.combo_localisation.currentData(),
            'localisation_details':self.input_localisation_details.text().strip() or None,
            'resume': self.input_resume.toPlainText().strip() or None,
            'remarques': self.input_remarques.toPlainText().strip() or None,
            'couverture_premiere_chemin': make_relative_cover_path(self.input_couv_prem_chemin.text().strip()) or None,
            'couverture_premiere_emplacement': self.input_couv_prem_location.text().strip() or None,
            'couverture_quatrieme_chemin': make_relative_cover_path(self.input_couv_quat_chemin.text().strip()) or None,
            'couverture_quatrieme_emplacement': self.input_couv_quat_location.text().strip() or None,
        }

        if not data['titre'] or not data['auteur']:
            show_custom_message_box(
                self,
                "WARNING",
                "Règle de Validation",
                "L'Auteur et le Titre doivent contenir une valeur.",
                "Les champs avec (*) sont à renseigner obligatoirement."
            )
            return None

        return data
