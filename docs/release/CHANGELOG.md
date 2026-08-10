# Journal des modifications

Toutes les modifications notables de ce projet sont consignées dans ce fichier.
Le format s'appuie sur Keep a Changelog, et le projet suit le versionnage sémantique.

## [Non publié]

## [1.1.2] - 2026-08-10

### Modifié

- Chaque proposition de modification est désormais vérifiée automatiquement par GitHub avant d'être intégrée : contrôle des types, du style de code, du formatage, des 91 tests et de la compilation.
- Les versions publiées sont construites et mises en ligne automatiquement : l'installeur et la version portable sont désormais téléchargeables depuis la page des versions du dépôt, accompagnés des notes tirées de ce journal.
- Les montées de dépendances sont proposées chaque semaine et passent par les mêmes contrôles que le reste.

### Corrigé

- Une installation propre du projet ne récupérait plus l'exécutable Electron, rendant l'application impossible à lancer depuis un clone neuf. Electron ayant retiré son propre script d'installation à partir de la version 42, le garde-fou du projet le déclenche désormais lui-même.

## [1.1.1] - 2026-08-10

### Corrigé

- Il était impossible de saisir quoi que ce soit dans la fiche d'un ouvrage : la valeur tapée disparaissait aussitôt. La fiche se rechargeait en boucle et écrasait la saisie, chaque rechargement déclenchant le suivant par l'indicateur de disponibilité de l'API. Le chargement ne dépend plus que de l'ouvrage ciblé, et un test de non-régression le verrouille.
- Dans l'historique, les lignes passaient devant la ligne d'en-tête au défilement et les valeurs longues se découpaient sur plusieurs lignes. Le tableau reprend la mécanique de la liste des ouvrages : en-tête hors du conteneur défilant, largeurs de colonnes figées, texte tronqué avec l'intégralité en infobulle.
- Les colonnes « Avant » et « Après » de l'historique étaient réduites à quelques pixels et illisibles. Les colonnes date, auteur et action sont resserrées à leur largeur utile, les deux dernières se partagent l'espace restant.

### Modifié

- Les libellés d'en-tête de tableau, et tout texte partageant leur couleur, passent au noir pur en thème clair et au blanc pur en thème sombre.
- L'icône à gauche du nom de l'application dans la barre supérieure devient `library-big`.
- Le bouton « Voir l'historique » quitte la troisième colonne de la fiche pour le pied de la modale, à l'opposé de « Annuler » et « Enregistrer ».

## [1.1.0] - 2026-08-10

### Modifié

- Nouvelle palette de couleurs Saphir, accent `#1D4ED8`, appliquée aux deux thèmes. Les couleurs sémantiques suivent désormais la règle de dérivation du design system pour cet accent.
- Les tableaux séparent leurs colonnes par un trait, du même poids que celui des lignes.
- L'indicateur de tri se place contre la bordure droite de la colonne concernée au lieu de suivre le libellé.
- Le chevron des listes déroulantes est écarté de la bordure droite du champ.
- L'historique d'un ouvrage s'ouvre dans une modale posée sur la fiche, sous forme de tableau, au lieu d'un panneau latéral rendu illisible par la modale qui le recouvrait. La touche Échap ne ferme plus que la fenêtre du dessus.
- L'écran de démarrage ne montre plus que l'icône de l'application, sur une fenêtre transparente et sans encadré.
- Nouvelle icône d'application, reprise par la fenêtre, la barre des tâches, l'écran de démarrage et l'exécutable empaqueté.
- Les commentaires du code sont rédigés en anglais. Les libellés d'interface, les messages de journal et les noms de tests restent en français.
- Le README et ce journal sont rédigés en français.

## [1.0.1] - 2026-08-10

### Corrigé

- La barre supérieure et la barre d'état restaient en place au défilement : la coquille occupe désormais la fenêtre au lieu de grandir avec son contenu, seule la zone de contenu défile.
- La barre de défilement du tableau commence sous la ligne d'en-tête, qui n'est plus dans le conteneur défilant.
- Les colonnes du tableau gardent une largeur fixe au lieu de se redimensionner quand les lignes virtualisées entrent et sortent du DOM ; le texte trop long est tronqué.

## [1.0.0] - 2026-08-09

### Ajouté

- Version initiale.
- Connexion par compte sur l'API hébergée sur Cloudflare Worker, jeton de session chiffré au repos par `safeStorage` d'Electron.
- Liste des ouvrages avec recherche côté client, tri et défilement virtualisé sur toute la collection.
- Fiche d'ouvrage : création, modification avec verrouillage optimiste, mise à la corbeille.
- Corbeille avec jours restants et restauration.
- Panneau d'historique champ par champ d'un ouvrage.
- Classification hiérarchique (catégorie, genre, sous-genre) et quatre listes de référence.
- Tableau de bord avec compteurs et graphiques par catégorie et par période.
- Résolution des couvertures depuis un dossier racine configurable, vignette et aperçu plein écran.
- Export CSV de la collection affichée.
- Thèmes clair et sombre, écran de démarrage, indicateur passif de disponibilité de l'API.
