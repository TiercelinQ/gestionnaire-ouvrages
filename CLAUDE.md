# Gestionnaire Ouvrage

## Origine

Framework : electron v1.5.0

## Contexte métier

Application de bureau Windows pour cataloguer, organiser et consulter une collection personnelle de livres, avec une classification à trois niveaux (Catégorie → Genre → Sous-genre) et des métadonnées d'édition fines.

Version 2 d'une application Python/PyQt6/SQLite (v1.2.1). Le changement structurant : la base SQLite posée sur un dossier synchronisé est remplacée par une **API HTTP** hébergée sur Cloudflare (Worker Hono + base D1), avec authentification par compte.

Fonctionnalités v1.0 : connexion et session, liste avec recherche, tri et défilement virtualisé, fiche complète en création et édition avec verrouillage optimiste, corbeille de trente jours, historique champ par champ, classification hiérarchique et quatre listes de référence, tableau de bord, couvertures, export CSV, thèmes clair et sombre.

## Contraintes structurantes de l'API

- **Tous les appels HTTP partent du processus principal.** Le Worker ne pose aucun en-tête CORS et répond `426` à un contrôle préalable de navigateur : un appel depuis le rendu échouerait.
- **Aucun sondage périodique.** Le quota de 100 000 requêtes par jour est partagé entre trois utilisateurs et non protégé. Pas de rafraîchissement automatique en arrière-plan.
- **La liste n'est ni paginée ni triée par le serveur.** Recherche, tri et filtrage sont entièrement côté client.
- **`PATCH` remplace la fiche entière** et exige la `version` lue au chargement. N'envoyer que sur validation explicite de l'utilisateur : un envoi automatique incrémenterait la version et ferait échouer la sauvegarde d'un autre poste.
- **Le jeton ne quitte jamais le processus principal.** Chiffré par `safeStorage`, jamais journalisé, jamais transmis au rendu.
- **Les messages d'erreur du serveur s'affichent tels quels.** Ils sont rédigés en français pour l'utilisateur final et déjà accordés en nombre ; ne jamais les analyser pour en extraire des compteurs.

## Déviations par rapport au framework

- **`IpcResult` étendu avec `code` et `champ`** - l'API impose de brancher la logique cliente sur le code d'erreur et de positionner le message sous le champ désigné.
- **Historique dans une seconde modale, pas un panneau latéral** - le drawer s'ouvrait derrière la modale de fiche qui le recouvrait. `Modal` porte une quatrième taille `moyenne` (56 rem) et une prop `fermetureClavier` : la fenêtre du dessous la passe à `false` pour qu'Échap ne ferme que celle du dessus. Plus aucun panneau latéral dans l'application, ni composant `Drawer`, ni tokens `--drawer-*` / `--z-drawer*`.
- **Deux vues pour un seul modèle `ouvrage`** - la corbeille est un état de l'entité, pas une entité distincte.
- **Icône en `resources/icon.png` au lieu de `.ico`** - PNG 256 x 256 fourni, electron-builder génère l'ICO au packaging. Copie identique en `src/renderer/public/icon.png` : sous CSP `img-src 'self'`, `splash.html` ne peut lire que le bundle du rendu. Garder les deux fichiers synchronisés si l'icône change.
- **Canal push `api:status`** - indicateur passif de disponibilité, seul moyen d'informer sans sondage.
- **Paliers d'accent 700 et 800 calculés relativement à l'accent** - l'accent Saphir `#1D4ED8` est à L 48 % ; la cible absolue du 700 (L 50 %) donnerait un survol plus clair que l'état normal. Les paliers 50, 400 et 900 suivent les cibles absolues.
- **Commentaires du code en anglais** - demande du propriétaire. Les libellés d'interface, les messages de journal, les noms de tests et les specs restent en français.
- **README et CHANGELOG en français** - demande du propriétaire, pour cette application uniquement ; `@rules/readme.md` et `@rules/versioning.md` imposent l'anglais. Les sections du changelog sont donc `Ajouté` / `Modifié` / `Corrigé` / `Supprimé` / `Sécurité` : `/electron-release` doit les lire sous ces noms pour inférer l'incrément.
- **Splash réduit à l'icône, fenêtre transparente** - `transparent: true`, `hasShadow: false`, ni nom ni texte d'état, donc plus rien à thématiser : `splash.ts` et le paramètre `?theme=` sont supprimés. `splash.css` ne lit plus des tokens que la taille de l'icône.
- **Sept champs optionnels sur `OuvrageListe`** - le Worker les fournit depuis le 9 août 2026 (`docs/api/evolution-liste-ouvrages.md`), les écrans concernés sont donc actifs. Les champs restent optionnels dans le type et `detecterChamps` reste en place : c'est le seul mécanisme qui permet à l'application de tourner devant un Worker antérieur.
- **Quatrième `tsconfig.test.json`** - les tests du processus principal importent `src/main/**`, absent du projet renderer, et les projets `composite` refusent un fichier non listé.
- **ESLint 9 au lieu de 10** - `eslint-plugin-react` plafonne à eslint 9.7 ; le conflit bloque l'installation.
- **Chargements initiaux écrits dans les effets** - `react-hooks/set-state-in-effect` interdit un `setState` atteignable synchronement depuis un effet et ne traverse pas les appels de fonction. Chaque effet porte sa propre fonction asynchrone avec drapeau d'annulation. Ne pas revenir à un appel de `recharger()` depuis un effet.

## Maintenance

- Charger le projet d'abord : `/electron-load-project`
- Le modifier : `/electron-add-feature` · `/electron-fix-issue` · `/electron-refactor-code` (chaque changement est consigné sous `[Unreleased]` dans `docs/release/CHANGELOG.md` ; la version ne bouge pas)
- Vérifier : `/electron-run-tests`
- Publier une version : `/electron-release` (transforme le `[Unreleased]` accumulé en version datée et relève le numéro)
