# pylint: disable=no-name-in-module
"""
Widget de l'onglet "Tableau de bord" de l'application avec les composants :
- ChartCard pour afficher des graphiques Matplotlib,
- KpiCard pour présenter des indicateurs clés,
- Dashboard pour orchestrer l’ensemble, gérer les filtres et rafraîchir les données.
"""
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QSizePolicy, QComboBox, QSpacerItem,
)
from PyQt6.QtCore import Qt, QTimer

# ---------- Helpers: thème ----------
def normalize_theme(theme: str) -> str:
    """
    Normalise le nom du thème en une chaîne en minuscules.

    Paramètres :
    - theme : nom du thème (ex. "Dark", "LIGHT", None).

    Fonctionnement :
    - Si theme est None ou vide, retourne "light" par défaut.
    - Convertit la chaîne en minuscules pour uniformiser l'utilisation.

    Résultat :
    - Chaîne normalisée ("dark" ou "light").
    """
    return (theme or "light").lower()

def theme_props(theme: str) -> dict:
    """
    Retourne les propriétés graphiques associées au thème.

    Paramètres :
    - theme : nom du thème (ex. "dark", "light").

    Fonctionnement :
    1. Normalise le nom du thème via normalize_theme().
    2. Retourne un dictionnaire contenant :
       • "bg" : couleur de fond (gris foncé pour dark, blanc pour light).
       • "font_color" : couleur du texte (blanc pour dark, noir pour light).

    Résultat :
    - Dictionnaire des propriétés graphiques du thème.
    - Exemple :
      theme_props("dark")  -> {"bg": "#393f48", "font_color": "white"}
      theme_props("light") -> {"bg": "white", "font_color": "black"}
    """
    t = normalize_theme(theme)
    return {
        "bg": "#393f48" if t == "dark" else "white",
        "font_color": "white" if t == "dark" else "black"
    }

# ---------- Helpers: Matplotlib ----------
def merge_dicts(data: dict[str, dict[str, int]]) -> dict[str, int]:
    """
    Fusionne plusieurs dictionnaires imbriqués en un seul dictionnaire plat.

    Paramètres :
    - data : dictionnaire dont les valeurs sont elles-mêmes des dictionnaires
             {clé: {sous_clé: valeur_int}}.
             Exemple :
             {
                 "loc1": {"A": 2, "B": 3},
                 "loc2": {"A": 1, "C": 4}
             }

    Fonctionnement :
    1. Initialise un dictionnaire vide `merged`.
    2. Parcourt chaque sous-dictionnaire de `data`.
    3. Pour chaque clé/valeur rencontrée :
       • Ajoute la valeur à la clé correspondante dans `merged`.
       • Si la clé n’existe pas encore, elle est créée avec la valeur initiale.
    4. Retourne le dictionnaire fusionné.

    Résultat :
    - Un dictionnaire plat avec la somme des valeurs par clé.
    - Exemple avec l’entrée ci-dessus :
      {"A": 3, "B": 3, "C": 4}
    """

    merged: dict[str, int] = {}

    # Parcourt chaque sous-dictionnaire
    for sub in data.values():
        # Parcourt chaque paire clé/valeur
        for k, v in sub.items():
            # Ajoute ou incrémente la valeur dans le dictionnaire fusionné
            merged[k] = merged.get(k, 0) + v

    return merged

def matplotlib_pie(ax, data: dict, theme: str):
    """
    Affiche un graphique en secteurs (pie chart) sur l'axe donné.

    Paramètres :
    - ax : objet Matplotlib Axes sur lequel dessiner le graphique.
    - data : dictionnaire {clé: valeur} représentant les catégories et leurs valeurs.
    - theme : nom du thème courant (ex. "dark", "light"), utilisé pour appliquer les couleurs.

    Étapes :
    1. Récupère les propriétés du thème (couleur de fond, couleur de police, etc.).
    2. Nettoie l'axe et applique les couleurs de fond.
    3. Si aucune donnée n'est disponible :
       • Affiche un message centré "Aucune donnée disponible actuellement".
       • Supprime les axes pour un rendu propre.
       • Retourne immédiatement.
    4. Sinon :
       • Extrait les labels et valeurs du dictionnaire.
       • Définit un formateur pour afficher les valeurs absolues dans le graphique.
       • Dessine le graphique en secteurs avec les données fournies.
       • Harmonise les couleurs du texte avec le thème.
       • Ajoute une légende alignée à gauche.
       • Applique la couleur du titre (vide par défaut).

    Résultat :
    - Graphique en secteurs cohérent avec le thème.
    - Message lisible si aucune donnée n’est disponible.
    """

    # ----- Préparation du thème -----
    props = theme_props(theme)

    # ----- Nettoyage et application du fond -----
    ax.clear()
    ax.figure.set_facecolor(props["bg"])
    ax.set_facecolor(props["bg"])

    # ----- Cas sans données -----
    if not data:
        ax.text(
            0.5, 0.5,
            "Aucune donnée disponible actuellement",
            ha="center", va="center",
            color=props["font_color"]
        )
        ax.axis("off")
        return

    # ----- Extraction des labels et valeurs -----
    labels = list(data.keys())
    sizes = list(data.values())

    # ----- Formateur pour afficher les valeurs absolues -----
    def value_formatter(pct, allvals):
        total = sum(allvals)
        val = int(round(pct * total / 100.0))
        return f"{val}"

    # ----- Dessin du pie chart -----
    wedges, texts, autotexts = ax.pie(
        sizes,
        startangle=90,
        autopct=lambda pct: value_formatter(pct, sizes)
    )

    # ----- Harmonisation des couleurs du texte -----
    for t in autotexts:
        t.set_color(props["font_color"])

    # ----- Légende -----
    legend_labels = [f"{lab}" for lab in labels]
    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )

    # ----- Titre (vide mais stylé) -----
    ax.set_title("", color=props["font_color"])

# ---------- Composants UI ----------
class KpiCard(QFrame):
    """
    Widget générique pour afficher un KPI (indicateur clé) dans le dashboard.

    Structure :
    - Hérite de QFrame, avec un layout vertical principal.
    - Contient :
        • Un titre (QLabel)
        • Une zone de contenu (QFrame) avec un layout vertical
          qui héberge une liste de widgets (souvent des QLabel).
    - Le contenu peut être centré ou aligné à gauche selon l'option center_content.

    Paramètres :
    - title : texte du titre affiché en haut de la carte.
    - content_widgets : liste de widgets (souvent QLabel) à afficher dans la zone de contenu.
    - object_name : identifiant unique pour appliquer des styles via QSS.
    - center_content : booléen, True pour centrer le contenu horizontalement, False pour l’aligner à gauche.

    Fonctionnement :
    - À l'initialisation :
        • Configure le style et la taille du widget.
        • Crée le layout principal et ajoute le titre.
        • Crée la zone de contenu et y insère les widgets fournis.
        • Applique un nom d’objet par défaut aux QLabel sans objectName.
        • Aligne le contenu selon l’option center_content.
    - Résultat :
        • Carte KPI réutilisable et stylable via QSS.
        • Contenu flexible (labels, widgets) avec alignement configurable.
    """

    def __init__(self, title: str, content_widgets: list[QLabel], object_name: str, center_content=False):
        super().__init__()
        self.setObjectName(object_name)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        # ----- Layout principal -----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(0)

        # ----- Titre -----
        title_label = QLabel(title)
        title_label.setObjectName(f"{object_name}Title")

        # ----- Contenu -----
        self.content_frame = QFrame()
        self.content_frame.setObjectName(f"{object_name}Content")
        self.content_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Ajout des widgets de contenu avec alignement configurable
        if center_content:
            self.content_layout.addStretch()
            for w in content_widgets:
                if isinstance(w, QLabel) and not w.objectName():
                    w.setObjectName(f"{object_name}ContentLabel")
                self.content_layout.addWidget(w, 0, Qt.AlignmentFlag.AlignHCenter)
            self.content_layout.addStretch()
        else:
            for w in content_widgets:
                if isinstance(w, QLabel) and not w.objectName():
                    w.setObjectName(f"{object_name}ContentLabel")
                self.content_layout.addWidget(w, 0, Qt.AlignmentFlag.AlignLeft)

        # ----- Assemblage -----
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.content_frame)

class ChartCard(QFrame):
    """
    Widget générique pour afficher un graphique dans le dashboard.

    Structure :
    - Hérite de QFrame, avec un layout vertical principal.
    - Contient :
        • Un titre centré (QLabel)
        • Une zone de contenu (QFrame) qui héberge un canvas Matplotlib
    - Le graphique est rendu via une fonction passée en paramètre (chart_func).

    Fonctionnement :
    - À l'initialisation :
        • Configure le style et la taille du widget
        • Crée le layout principal et ajoute le titre
        • Instancie la figure Matplotlib et son canvas
        • Appelle la fonction de rendu initiale
        • Déclenche un redraw différé (QTimer.singleShot) pour garantir un affichage centré
    - Méthode update_chart :
        • Nettoie la figure
        • Crée un subplot
        • Exécute la fonction de rendu (chart_func) avec le thème courant
        • Redessine le canvas

    Résultat :
    - Un widget réutilisable pour afficher différents graphiques
    - Compatible avec les thèmes (dark/light) via config_manager
    - Redimensionnement et rafraîchissement gérés automatiquement
    """

    def __init__(self, title: str, chart_func, object_name: str, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.setObjectName(object_name)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ----- Layout principal -----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # ----- Titre -----
        self.label_title = QLabel(title)
        self.label_title.setObjectName(f"{object_name}Title")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_title)

        # ----- Contenu (canvas Matplotlib) -----
        self.content_frame = QFrame()
        self.content_frame.setObjectName(f"{object_name}Content")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        theme = normalize_theme(self.config_manager.get_theme())
        props = theme_props(theme)

        self.figure = Figure(facecolor=props["bg"], constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content_layout.addWidget(self.canvas)
        main_layout.addWidget(self.content_frame)

        # ----- Fonction de rendu -----
        self.chart_func = chart_func
        self.update_chart()

        # redraw différé pour garantir un affichage centré
        QTimer.singleShot(0, self.canvas.draw)

    def update_chart(self):
        """
        Met à jour le graphique affiché dans le widget.

        Étapes :
        1. Récupère le thème courant via config_manager.
        2. Efface la figure existante.
        3. Crée un subplot unique.
        4. Exécute la fonction de rendu (chart_func) avec le thème.
        5. Redessine le canvas pour afficher le graphique.
        """
        theme = normalize_theme(self.config_manager.get_theme())
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.chart_func(ax, theme)
        self.canvas.draw()

# ---------- Widget complet ---------
class DashboardWidget(QWidget):
    def __init__(self, db_manager, config_manager):
        """
        Initialise le dashboard principal.

        Paramètres :
        - db_manager : gestionnaire de base de données (accès aux ouvrages, catégories, périodes, etc.)
        - config_manager : gestionnaire de configuration (thème, préférences, etc.)

        Étapes :
        1. Appelle le constructeur parent pour initialiser le widget.
        2. Stocke les gestionnaires (db_manager, config_manager) comme attributs.
        3. Construit l'interface utilisateur via _setup_ui().
        4. Configure un timer pour rafraîchir les données toutes les 5 secondes.
        5. Déclenche un premier rafraîchissement immédiat pour afficher les données dès l'ouverture.

        Résultat :
        - Le dashboard est prêt à l’emploi, avec UI construite et données affichées.
        - Les KPI et charts se mettent à jour automatiquement toutes les 5 secondes.
        """

        # ----- Initialisation de la classe -----
        super().__init__()
        self.db_manager = db_manager
        self.config_manager = config_manager

        # ----- Construction de l'interface -----
        self._setup_ui()

        # ----- Rafraîchissement automatique -----
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # toutes les 5 secondes

        # ----- Premier affichage immédiat -----
        self.refresh_data()

    def _setup_ui(self):
        """
        Construit l'interface principale du dashboard.

        Structure :
        - Layout principal horizontal (main_layout) :
            • Colonne gauche (left_col) :
                - Filtre par localisation (comboBox)
                - KPI : Total ouvrages
                - KPI : Ouvrages et couvertures (1re et 4e)
                - KPI : Top 3 catégories
                - KPI : Derniers ouvrages ajoutés
                - Label d'instruction + espace extensible
            • Colonne droite (right_col) :
                - Chart : Ouvrages par catégorie
                - Chart : Ouvrages par périodes

        Résultat :
        - Interface claire et structurée
        - Rafraîchissement des données déclenché par le filtre
        - KPI et charts prêts à être mis à jour par refresh_data()
        """

        # ----- Layout principal -----
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(12)

        # ============================
        # Colonne gauche : Filtres + KPI
        # ============================
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        # --- Filtre par localisation ---
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(5)

        self.label_filter = QLabel("Filtre par localisation: ")
        filter_layout.addWidget(self.label_filter)

        locs = self.db_manager.get_ouvrages_by_location().keys()
        self.combo_loc = QComboBox()
        self.combo_loc.addItem("Toutes")
        self.combo_loc.addItems(sorted(locs))
        self.combo_loc.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.combo_loc, 1)

        left_col.addWidget(filter_widget)

        # --- KPI : Total ouvrages ---
        self.lbl_total_value = QLabel("")
        self.lbl_total_value.setObjectName("KpiTotalContentLabel")
        self.kpi_total = KpiCard("Total Ouvrages", [self.lbl_total_value], "KpiTotal", center_content=True)
        self.kpi_total.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- KPI : Ouvrages et couvertures ---
        self.lbl_cover1_with = QLabel(""); self.lbl_cover1_with.setObjectName("KpiCoverWith")
        self.lbl_cover1_without = QLabel(""); self.lbl_cover1_without.setObjectName("KpiCoverWithout")
        self.lbl_cover4_with = QLabel(""); self.lbl_cover4_with.setObjectName("KpiCoverWith")
        self.lbl_cover4_without = QLabel(""); self.lbl_cover4_without.setObjectName("KpiCoverWithout")

        cover1_widget = QWidget()
        cover1_widget.setObjectName("KpiCoverContent")
        cover1_layout = QHBoxLayout(cover1_widget)
        cover1_layout.setContentsMargins(0, 0, 0, 0)
        cover1_layout.setSpacing(10)
        cover1_layout.addWidget(QLabel("→ 1re Couverture :"))
        cover1_layout.addWidget(self.lbl_cover1_with)
        cover1_layout.addWidget(QLabel("/"))
        cover1_layout.addWidget(self.lbl_cover1_without)

        cover4_widget = QWidget()
        cover4_widget.setObjectName("KpiCoverContent")
        cover4_layout = QHBoxLayout(cover4_widget)
        cover4_layout.setContentsMargins(0, 0, 0, 0)
        cover4_layout.setSpacing(10)
        cover4_layout.addWidget(QLabel("→ 4e Couverture : "))
        cover4_layout.addWidget(self.lbl_cover4_with)
        cover4_layout.addWidget(QLabel("/"))
        cover4_layout.addWidget(self.lbl_cover4_without)

        self.kpi_cover = KpiCard("Ouvrages et Couvertures", [cover1_widget, cover4_widget], "KpiCover", center_content=False)
        self.kpi_cover.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- KPI : Top catégories ---
        self.kpi_topcat = KpiCard("Top 3 Catégories", [], "KpiCategories")
        self.kpi_topcat.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- KPI : Derniers ouvrages ---
        self.kpi_last = KpiCard("Derniers Ouvrages Ajoutés", [], "KpiLast")
        self.kpi_last.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Ajout des KPI à la colonne gauche
        left_col.addWidget(self.kpi_total)
        left_col.addWidget(self.kpi_cover)
        left_col.addWidget(self.kpi_topcat)
        left_col.addWidget(self.kpi_last)

        # --- Label d'instruction + espace extensible ---
        label_dashboard_info = QLabel("Rafraichissement des données toutes les 5 secondes.")
        label_dashboard_info.setObjectName("InstructionLabel")
        left_col.addWidget(label_dashboard_info)
        left_col.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ============================
        # Colonne droite : Charts
        # ============================
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        self.chart_categories = ChartCard(
            "Ouvrages par Catégorie",
            lambda ax, th: matplotlib_pie(ax, None, th),
            "ChartCategories",
            config_manager=self.config_manager
        )
        self.chart_periods = ChartCard(
            "Ouvrages par Périodes",
            lambda ax, th: matplotlib_pie(ax, None, th),
            "ChartPeriods",
            config_manager=self.config_manager
        )

        right_col.addWidget(self.chart_categories)
        right_col.addWidget(self.chart_periods)

        # ============================
        # Assemblage final
        # ============================
        main_layout.addLayout(left_col, 1)   # colonne gauche (poids 1)
        main_layout.addLayout(right_col, 2)  # colonne droite (poids 2)

    def refresh_data(self):
        """
        Rafraîchit toutes les données affichées dans le dashboard en fonction de la localisation sélectionnée.

        Étapes principales :
        1. Récupère la localisation choisie dans la comboBox.
        2. Charge depuis la base :
        - le nombre total d'ouvrages par localisation,
        - les statistiques de complétion des couvertures (1re et 4e),
        - les catégories dominantes (top 3),
        - les périodes associées,
        - les derniers ouvrages ajoutés.
        3. Met à jour les KPI :
        - total d'ouvrages,
        - couvertures complètes/incomplètes,
        - top catégories,
        - derniers ouvrages.
        → Chaque section affiche soit les données, soit un message "Aucune donnée disponible".
        4. Nettoie les layouts avant d'ajouter de nouveaux widgets pour éviter les doublons.
        5. Met à jour les graphiques (catégories et périodes) avec les données recalculées.

        Résultat :
        - Le dashboard reflète toujours l'état actuel de la base,
        - Les KPI et charts sont cohérents avec la localisation sélectionnée,
        - Les messages d'absence de données assurent une interface lisible et robuste.
        """
        loc = self.combo_loc.currentText()

        ouvrages_by_loc = self.db_manager.get_ouvrages_by_location()
        cover1_with, cover1_without = self.db_manager.get_cover_completion_stats_by_location("couverture_premiere_chemin", loc)
        cover4_with, cover4_without = self.db_manager.get_cover_completion_stats_by_location("couverture_quatrieme_chemin", loc)
        top_categories = self.db_manager.get_top_categories_by_location(loc, limit=3)

        if loc == "Toutes":
            total = sum(ouvrages_by_loc.values())
            chart_categories_data = merge_dicts(self.db_manager.get_categories_by_location())
            chart_periods_data = merge_dicts(self.db_manager.get_periodes_by_location())
        else:
            total = ouvrages_by_loc.get(loc, 0)
            chart_categories_data = self.db_manager.get_categories_by_location().get(loc, {})
            chart_periods_data = self.db_manager.get_periodes_by_location().get(loc, {})

        last_books = self.db_manager.get_last_books_by_location(loc, limit=5)

        self.lbl_total_value.setText("Aucune donnée disponible actuellement" if total == 0 else str(total))

        if cover1_with == 0 and cover1_without == 0:
            self.lbl_cover1_with.setText("Aucune donnée disponible actuellement")
            self.lbl_cover1_without.clear()
        else:
            self.lbl_cover1_with.setText(f"avec = {cover1_with}")
            self.lbl_cover1_without.setText(f"sans = {cover1_without}")

        if cover4_with == 0 and cover4_without == 0:
            self.lbl_cover4_with.setText("Aucune donnée disponible actuellement")
            self.lbl_cover4_without.clear()
        else:
            self.lbl_cover4_with.setText(f"avec = {cover4_with}")
            self.lbl_cover4_without.setText(f"sans = {cover4_without}")

        for i in reversed(range(self.kpi_topcat.content_layout.count())):
            w = self.kpi_topcat.content_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not top_categories:
            lbl = QLabel("Aucune donnée disponible actuellement")
            lbl.setObjectName("KpiCategoriesContent")
            self.kpi_topcat.content_layout.addWidget(lbl)
        else:
            for i, (cat, count) in enumerate(top_categories, start=1):
                lbl = QLabel(f"{i}. {cat} : {count}")
                lbl.setObjectName("KpiCategoriesContent")
                self.kpi_topcat.content_layout.addWidget(lbl)

        for i in reversed(range(self.kpi_last.content_layout.count())):
            w = self.kpi_last.content_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not last_books:
            lbl = QLabel("Aucune donnée disponible actuellement")
            lbl.setObjectName("KpiLastContent")
            self.kpi_last.content_layout.addWidget(lbl)
        else:
            for i, b in enumerate(last_books, start=1):
                lbl = QLabel(f"{i}. {b['titre']} de {b['auteur']}")
                lbl.setToolTip(f"le {b['date']}")
                lbl.setObjectName("KpiLastContent")
                lbl.setWordWrap(True)
                lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                self.kpi_last.content_layout.addWidget(lbl)

        self.chart_categories.chart_func = lambda ax, th: matplotlib_pie(ax, chart_categories_data, th)
        self.chart_periods.chart_func = lambda ax, th: matplotlib_pie(ax, chart_periods_data, th)
        self.chart_categories.update_chart()
        self.chart_periods.update_chart()

    def refresh_theme(self, new_theme: str):
        """
        Applique un nouveau thème au dashboard et redessine les graphiques.

        Paramètres :
        - new_theme : chaîne représentant le thème à appliquer (ex. "dark", "light").

        Fonctionnement :
        1. Vérifie si le config_manager possède une méthode `set_theme`.
        2. Si oui, applique le nouveau thème via config_manager.
        3. Rafraîchit toutes les données et les charts en appelant refresh_data().

        Résultat :
        - Le thème est mis à jour (couleurs de fond, couleurs de texte).
        - Les KPI et charts sont redessinés immédiatement pour refléter le nouveau thème.
        """
        # ----- Mise à jour du thème -----
        if hasattr(self.config_manager, "set_theme"):
            self.config_manager.set_theme(new_theme)

        # ----- Rafraîchissement complet -----
        self.refresh_data()
