# Content Studio — /admin

Éditer les études de cas sans toucher au code. Seules les études de cas sont éditables. L'accueil, About, Off the clock, la navigation et le design ne le sont pas.

## Comment c'est fait

- **Le contenu** : une étude de cas = un fichier `content/cases/<id>.json` (header, faits, sections, carte de Search my work, Behind the decisions).
- **La construction** : `scripts/cases.py` transforme ces fichiers en pages, avec exactement le HTML d'avant la migration. Le design est figé dans ce script. `scripts/build_site.py` le lance avant de construire le site, et Vercel exécute cette construction à chaque commit (`vercel.json`).
- **Le studio** : `/admin`, c'est [Decap CMS](https://decapcms.org) (open source, gratuit, sans base de données). Il ne se charge que sur `/admin` : rien de plus pour les visiteurs.
- **La connexion** : via ton compte GitHub (`api/auth.js` et `api/callback.js`, deux petites fonctions Vercel). Le jeton reste côté serveur pendant l'échange. Seul le compte `Sapereaaude` est accepté.
- **Brouillon / publication** : enregistrer crée une branche et une pull request (rien ne change sur le site). Vercel en fait une prévisualisation privée. Publier fusionne la PR : un commit « Case study: edit <id> » sur `main`, puis le déploiement.
- **Les images** : rangées dans `assets/uploads/`, redimensionnées et compressées à la construction.

Le canevas Claude Design ne sert plus de source pour les études de cas : une modification de `project/Case-*.dc.html` est écrasée à la construction suivante. Les pages d'accueil, About, etc. ne changent pas de fonctionnement.

## Mise en route (une seule fois, ~10 minutes)

1. **Créer l'application OAuth GitHub**
   GitHub → Settings → Developer settings → OAuth Apps → **New OAuth App**
   - Application name : `Portfolio Content Studio`
   - Homepage URL : `https://uxrsafaaelouafi.vercel.app`
   - Authorization callback URL : `https://uxrsafaaelouafi.vercel.app/api/callback`
   - **Register application**, puis **Generate a new client secret**. Copie le Client ID et le secret.

2. **Ajouter les variables sur Vercel**
   Vercel → projet `portfolio` → Settings → Environment Variables, pour **Production** et **Preview** :
   - `GITHUB_CLIENT_ID` = le Client ID
   - `GITHUB_CLIENT_SECRET` = le secret
   - (facultatif) `STUDIO_ALLOWED_USERS` = `Sapereaaude` (c'est déjà la valeur par défaut)

3. **Redéployer**
   Vercel → Deployments → le dernier → **Redeploy** (pour que les variables soient prises en compte).
   Vérifie dans Settings → Build & Development que le Framework Preset est « Other ». La commande de build vient de `vercel.json` : `python3 scripts/build_site.py`.

4. **Se connecter**
   Ouvre `https://uxrsafaaelouafi.vercel.app/admin`, clique **Login with GitHub**, accepte. Utilise toujours l'adresse de production : la connexion ne fonctionne que sur l'URL de rappel enregistrée.

## Au quotidien

1. `/admin` → **Case studies** → choisis une étude de cas.
2. Modifie : titres, textes (gras, italique, liens), listes, images, ordre des sections (glisser-déposer), ajout, duplication ou suppression d'une section, carte de recherche, Behind the decisions.
3. L'aperçu à droite utilise le vrai HTML de la page (boutons **Desktop** / **Mobile**).
4. **Save** = brouillon (onglet **Workflow**, colonne Drafts). Le site public ne bouge pas.
5. Statut **Ready**, puis **Publish** : commit sur GitHub, déploiement Vercel en ~1 minute.

**Tout publier d'un coup** : quand des études de cas sont en *Ready*, un bouton noir **Publish all Ready** apparaît en bas à droite (sauf dans l'éditeur). Il publie toute la colonne Ready en un seul commit sur `main`, donc un seul déploiement. Chaque PR est marquée « merged » et sa branche supprimée. Une étude de cas dont le fichier a aussi changé ailleurs n'est pas touchée : elle reste en Ready, à publier depuis l'éditeur (`assets/admin/publish-ready.js`).

Statuts : *Published* (en ligne), *Draft / In review / Ready* (modifications non publiées). Decap affiche un message en cas d'échec de publication et prévient avant de quitter une page non enregistrée.

## Revenir en arrière

Chaque publication est un commit « Case study: edit <id> ». Pour annuler : GitHub → Commits → le commit → **Revert**.

## Blocs disponibles dans une section

| Bloc | Rendu |
| --- | --- |
| Paragraph | paragraphe, note (italique gris) ou citation (grand serif) ; une ligne vide = nouveau paragraphe |
| Bullet list | la liste à puces bleues |
| Heading | intertitre en Anton |
| Image | image + texte alternatif + légende |
| Custom figure | figure faite à la main (schémas, maquettes) : conservée telle quelle, déplaçable, non éditable |

Les illustrations SVG des en-têtes et les figures sur mesure sont verrouillées pour ne pas casser le design.
