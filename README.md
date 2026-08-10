# Gestionnaire Ouvrage - v1.1.1

Client de bureau Windows pour cataloguer et consulter une collection personnelle d'ouvrages. Interface de bureau de l'API Gestionnaire Ouvrage (Cloudflare Worker + D1), en remplacement d'une application Python/PyQt6/SQLite dont la base vivait sur un dossier synchronisé.

## Objectif

Cataloguer, organiser et parcourir une collection personnelle d'ouvrages avec une classification à trois niveaux (catégorie → genre → sous-genre) et les métadonnées détaillées de l'édition : ISBN, année, collection, reliure, dimensions, couvertures, emplacement physique dans le logement.

## Fonctionnalités

- Connexion par compte ; le jeton de session est chiffré au repos par `safeStorage` d'Electron et ne quitte jamais le processus principal.
- Liste des ouvrages avec recherche côté client, tri par colonne et défilement virtualisé sur toute la collection.
- Fiche complète : création, modification avec verrouillage optimiste, mise à la corbeille.
- Corbeille avec jours restants et restauration. La suppression définitive est une tâche serveur quotidienne.
- Historique champ par champ de chaque ouvrage, dans une modale posée sur la fiche.
- Classification hiérarchique et quatre listes de référence (illustrations, périodes, reliures, localisations).
- Tableau de bord : compteurs, graphiques par catégorie et par période.
- Couvertures résolues depuis un dossier racine configurable, avec vignette et aperçu plein écran.
- Export CSV de la collection affichée.
- Thèmes clair et sombre, écran de démarrage, indicateur passif de disponibilité de l'API.

## Pile technique

| Couche         | Technologie                                                       |
| -------------- | ----------------------------------------------------------------- |
| Exécution      | Node.js 24+ · Electron 43                                         |
| Langage        | TypeScript strict                                                 |
| Rendu          | React 19, composants fonctionnels et hooks uniquement             |
| Construction   | electron-vite                                                     |
| Architecture   | MVC strict - principal = modèles, rendu = vues, IPC = contrôleurs |
| Style          | CSS centralisé : `tokens.css` (variables) + `styles.css`          |
| Icônes         | Lucide (`lucide-react`)                                           |
| Graphiques     | Recharts                                                          |
| Journalisation | electron-log                                                      |
| Tests          | Vitest + Testing Library                                          |
| Empaquetage    | electron-builder (NSIS + portable)                                |

Aucune base locale : toutes les données viennent de l'API. Aucun client HTTP tiers, le `fetch` natif de Node suffit. Aucune bibliothèque de virtualisation, la liste est plate et la hauteur de ligne fixe.

## Prérequis

- Windows 10 ou 11.
- Node.js 24 LTS ou supérieur.
- Un compte sur l'API Gestionnaire Ouvrage. Les comptes sont créés et réinitialisés par l'administrateur en ligne de commande ; l'application n'offre ni inscription ni changement de mot de passe.
- Accès réseau à `https://gestionnaire-ouvrages-api.qtiercelin-apps.workers.dev`.

## Installation

```
npm install
npm run dev          # développement
npm run typecheck    # vérification TypeScript (principal + rendu + tests)
npm run lint         # ESLint
npm test             # Vitest
npm run build        # construction sans empaquetage
npm run dist         # empaquetage Windows (NSIS + portable)
```

Si `npm run dev` signale `Error: Electron uninstall`, l'extraction du binaire Electron a échoué silencieusement : lancer `npm run postinstall`, qui le restaure depuis le cache local.

## Arborescence

```
src/
├── shared/                     types, constantes, noms des canaux IPC
│   ├── config.ts               URL de l'API, tailles de fenêtre, position des toasts, journalisation
│   ├── types.ts                DTO de l'API, IpcResult, WindowApi, gardes de type
│   └── ipc-channels.ts         les 23 noms de canaux
├── main/
│   ├── index.ts                fenêtres, splash, sécurité, gestionnaires d'erreurs globaux
│   ├── logger.ts               configuration d'electron-log
│   ├── models/
│   │   ├── api-client.ts       seul point d'accès réseau
│   │   ├── token-store.ts      jeton de session, chiffré par safeStorage
│   │   ├── session.model.ts    connexion, déconnexion, vérification, seuils de version
│   │   ├── ouvrage.model.ts    ouvrages, corbeille, historique
│   │   ├── nomenclature.model.ts   les sept listes de référence
│   │   ├── couverture.model.ts     résolution des chemins et lecture des images
│   │   ├── export.model.ts     génération du CSV
│   │   ├── preferences.model.ts    preferences.json
│   │   └── errors.ts           erreurs métier nommées
│   └── controllers/            un gestionnaire IPC par canal, validation des entrées
├── preload/index.ts            contextBridge, une fonction nommée par canal
└── renderer/
    ├── index.html · splash.html    tous deux porteurs de la CSP stricte
    ├── public/icon.png         copie de resources/icon.png, servie au splash sous img-src 'self'
    └── src/
        ├── App.tsx             frontière d'erreur, fournisseurs, coquille, aiguillage
        ├── views/              écrans, composants de structure, modales
        ├── hooks/              session, toasts, nomenclatures, ouvrages, virtualisation
        ├── utils/              normalisation de recherche, formatage
        ├── i18n/               libellés français centralisés
        └── styles/             tokens.css, styles.css, splash.css
```

## Canaux IPC

Convention `entite:action`. Déclarés dans `src/shared/ipc-channels.ts` ; aucune chaîne de canal n'apparaît ailleurs.

| Canal                 | Contrôleur   | `window.api`                               |
| --------------------- | ------------ | ------------------------------------------ |
| `session:status`      | session      | `sessionStatus()`                          |
| `session:login`       | session      | `sessionLogin(identifiants)`               |
| `session:logout`      | session      | `sessionLogout()`                          |
| `app:info`            | session      | `appInfo()`                                |
| `ouvrage:list`        | ouvrage      | `ouvrageList()`                            |
| `ouvrage:get`         | ouvrage      | `ouvrageGet(id)`                           |
| `ouvrage:create`      | ouvrage      | `ouvrageCreate(input)`                     |
| `ouvrage:update`      | ouvrage      | `ouvrageUpdate(id, input)`                 |
| `ouvrage:delete`      | ouvrage      | `ouvrageDelete(id, version)`               |
| `ouvrage:restore`     | ouvrage      | `ouvrageRestore(id)`                       |
| `ouvrage:history`     | ouvrage      | `ouvrageHistory(id)`                       |
| `corbeille:list`      | ouvrage      | `corbeilleList()`                          |
| `nomenclature:list`   | nomenclature | `nomenclatureList()`                       |
| `nomenclature:create` | nomenclature | `nomenclatureCreate(ressource, input)`     |
| `nomenclature:update` | nomenclature | `nomenclatureUpdate(ressource, id, input)` |
| `nomenclature:delete` | nomenclature | `nomenclatureDelete(ressource, id)`        |
| `couverture:pick`     | couverture   | `couverturePick()`                         |
| `couverture:read`     | couverture   | `couvertureRead(chemin)`                   |
| `export:csv`          | export       | `exportCsv(lignes)`                        |
| `pref:get`            | preferences  | `getPreferences()`                         |
| `pref:set`            | preferences  | `setPreference(cle, valeur)`               |
| `pref:pickFolder`     | preferences  | `pickCoversFolder()`                       |
| `api:status` (poussé) | -            | `onApiStatus(callback)`                    |

## Données

L'application ne possède aucun schéma : l'API le porte. En local, elle n'écrit que deux fichiers sous `app.getPath("userData")` :

- `preferences.json` - thème, géométrie de la fenêtre, dossier racine des couvertures.
- `session.bin` - le jeton de session et sa date d'expiration, chiffrés par `safeStorage` (DPAPI sous Windows).

## Conventions

- MVC strict : logique métier dans `src/main/models/`, validation et aiguillage dans les contrôleurs, rendu seul dans les vues. Les imports vont dans un seul sens : rendu → preload → contrôleurs → modèles.
- Aucune valeur visuelle en dur dans le TS/TSX, aucun attribut `style` en ligne. Deux exceptions assumées, toutes deux commentées : le soulignement glissant des onglets écrit deux variables CSS, et les lignes d'espacement de la table virtualisée portent une hauteur calculée.
- `styles.css` ne consomme que `var(--token)`. Le mode sombre tient dans l'unique bloc `[data-theme="dark"]` de `tokens.css`.
- La profondeur passe par le trait : aucun `box-shadow`, aucun dégradé, aucune alternance de lignes.
- Les erreurs s'affichent en toast ou sous le champ désigné par le serveur ; jamais `alert()`, `confirm()` ni `dialog.showMessageBox`.
- Sécurité Electron verrouillée : `contextIsolation`, `sandbox`, pas de `nodeIntegration`, CSP stricte, navigation et ouverture de fenêtre bloquées, toute charge utile IPC validée côté principal.
- Aucun `console.log` dans le code livré, uniquement `electron-log`, qui écrit dans `userData/logs/main.log`. Poser `GESTIONNAIREOUVRAGE_DEBUG=1` pour le niveau debug.
- Les commentaires du code sont rédigés en anglais ; les libellés d'interface, les messages de journal et les noms de tests restent en français.

## Limite connue

L'export CSV couvre les quatre colonnes affichées par la liste : auteur, titre, édition, catégorie. L'API ne sert les autres champs que fiche par fiche, exporter l'intégralité coûterait une requête par ouvrage.

## Claude Code

`.claude/settings.json` est livré avec le projet : règles de refus sur les secrets et les sorties de build, plus un hook `Stop` qui lance ESLint quand un fichier TypeScript porte des modifications non commitées. À ajuster ou retirer selon les besoins.

## Licence

Propriétaire. Usage, modification et redistribution soumis à l'accord explicite de l'auteur.
