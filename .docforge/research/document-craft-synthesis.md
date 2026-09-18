# Synthese des recherches — Document Craft pour DocForge

> Synthese croisee de trois referentiels (taste-skill, design-engineering skills, impeccable)
> adaptee au traitement documentaire DOCX/PDF (academique, professionnel, institutionnel).
>
> Date de synthese : 2026-09-18

---

## Methodologie

Chaque principe issu des trois depots source a ete :
1. Identifie dans son contexte original (frontend, design UI, audit IA)
2. Reinterprete pour le domaine documentaire (mise en page, typographie, relecture)
3. Mappe aux agents et skills existants de la chaine DocForge
4. Traduit en critere QA mesurable et deterministe

Les principes sont regroupes en six categories operationnelles.

---

## 1. Gout editorial (Editorial Taste)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| Brief Inference Before Action | taste-skill | Avant toute action, analyser le genre, le public et le style existant du document | Phase de lecture prealable obligatoire : extraire le registre (academique, administratif, technique), identifier le lectorat cible, relever le ton dominant | Un rapport annuel doit etre traite differemment d'un memoire universitaire ; le "Document Read" detecte ces differences avant toute correction | inspector | document-inspection | Presence d'un fichier `work/inspection/document_read.json` avant toute modification |
| Three-Dial System (VARIANCE/MOTION/DENSITY) | taste-skill | Trois axes de controle adaptables au contexte documentaire | Trois parametres dans `document_config.yaml` : LAYOUT_FORMALITY (1-10), DENSITY (1-10), VISUAL_RICHNESS (1-10). Un document juridique : formality=9, density=7, richness=2. Un rapport creatif : formality=4, density=5, richness=8 | Document academique : formality=8, density=6, richness=3 — applique des marges larges, interligne aere, pas d'encadres decoratifs | analyst | structure-analysis | Les trois parametres sont definis et coherents avec le genre detecte |
| Frequency-Based Decisions | design-skills | Les elements frequents recoivent un traitement sobre ; les elements rares recoivent un traitement distinctif | Les paragraphes de corps (frequents) gardent un formatage neutre et regulier. Les encadres, citations longues ou tableaux (rares) peuvent recevoir un traitement visuel plus riche | Corps de texte : Times 12pt standard. Encadre exceptionnel : fond gris clair, bordure fine, pour signaler sa rarete | analyst | chapter-processing | Ratio elements enrichis / elements standards < 15% du document |
| Design Specificity / Swap Test | impeccable | Si le formatage pourrait appartenir a n'importe quel document, il est generique et donc insuffisant | Verifier que les choix de mise en page refletent le contenu specifique : un document medical ne doit pas ressembler a un rapport financier | Si on peut echanger les pages de titre de deux documents sans que personne ne remarque, le formatage est trop generique | reviewer | quality-loop | Test de specificite : au moins 3 elements de mise en page sont propres au type de document |
| Purpose-Justified Changes | design-skills | Chaque correction doit citer sa finalite (coherence, lisibilite, conformite) | Toute modification enregistree dans `state/corrections.json` inclut un champ `purpose` parmi : consistency, readability, compliance, accessibility | Correction : remplacement de tiret par tiret cadratin — purpose: "consistency" (uniformisation typographique) | reviewer | language-quality | 100% des entrees de corrections.json ont un champ `purpose` non vide |

---

## 2. Typographie (Typography)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| Em-Dash Ban / Discipline typographique | taste-skill | Controler l'usage excessif des tirets cadratins, verifier les guillemets typographiques, les tirets demi-cadratins dans les plages | Linter typographique integre : detecter les tirets cadratins utilises comme ponctuation paresseuse, verifier les guillemets francais, les espaces insecables avant ponctuation double | Remplacer `mot - mot` par `mot -- mot` (tiret demi-cadratin pour incise) ; verifier que les guillemets sont bien des chevrons francais et non des guillemets droits | verifier | language-quality | Zero tiret cadratin non justifie ; 100% guillemets chevrons en contexte francais |
| Size-Dependent Tracking/Leading | design-skills | Le crenage et l'interligne varient selon la taille du texte | Definir des regles d'interligne proportionnelles : corps 12pt = interligne 1.15, titres 18pt = interligne 1.05, notes 9pt = interligne 1.2 | Titre de chapitre (16pt, interligne serre) vs corps de texte (11pt, interligne aere) vs note de bas de page (9pt, interligne legerement majore) | verifier | docx-formatting | Chaque style verifie respect le ratio interligne/taille defini dans le config |
| Multi-Axis Hierarchy | design-skills | La hierarchie visuelle combine poids, taille et interligne, pas un seul axe | Les niveaux de titre se distinguent par au moins deux axes : taille + graisse, ou taille + espacement. Jamais uniquement par la taille | Heading 1 : 16pt gras, Heading 2 : 14pt semi-gras, Heading 3 : 12pt gras italique — chaque niveau differe sur au moins 2 axes | analyst | structure-analysis | Chaque paire de niveaux de titre adjacents differe sur >= 2 axes visuels |
| Typography as Architecture | impeccable | La typographie structure le document comme l'architecture structure un batiment | Mesure du corps : 45-75 caracteres par ligne. Echelle de roles deliberee. Espace au-dessus d'un titre > espace en dessous. Coherence des roles typographiques | Verifier que la largeur de colonne produit entre 50 et 70 caracteres par ligne en corps de texte ; que l'espace avant titre est 1.5x l'espace apres | verifier | docx-formatting | Largeur de ligne entre 45-75 caracteres ; ratio espacement avant/apres titres >= 1.3 |
| Design Tokens | design-skills | Toutes les valeurs de formatage comme jetons nommes ; detecter la derive par rapport a la specification | Definir un dictionnaire de tokens dans `document_config.yaml` : `body-size`, `heading1-size`, `margin-top`, `spacing-after-para`, etc. Tout ecart constitue une anomalie | Token `body-font-size: 11pt` — si un paragraphe est en 10.5pt, c'est une derive a corriger automatiquement | verifier | integrity-validation | Zero valeur de formatage hors dictionnaire de tokens (tolerance : 0.5pt pour tailles, 1pt pour espacements) |
| Font Role Consistency | impeccable | Chaque police a un role defini ; pas de variation arbitraire | Maximum 2-3 familles de polices dans un document. Chaque famille a un role clair : corps, titres, code/technique. Aucune police orpheline | Si le document utilise Garamond pour le corps et Helvetica pour les titres, un paragraphe en Calibri est une anomalie a signaler | verifier | integrity-validation | Nombre de familles de polices <= 3 ; chaque famille mappee a un role dans le config |

---

## 3. Rythme & Composition (Rhythm & Composition)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| Spacing Rhythm | impeccable | Groupes serres + separations genereuses. Echelle d'espacement coherente | Definir une echelle d'espacement par increments reguliers (ex: 3pt, 6pt, 12pt, 24pt). Les paragraphes d'un meme bloc sont serres ; les blocs entre eux sont separes | Paragraphes internes d'une section : spacing-after 6pt. Entre sections : spacing-after 24pt. Jamais de valeurs intermediaires non prevues | verifier | docx-formatting | 100% des espacements correspondent a l'echelle definie (tolerance 1pt) |
| Squint Test | impeccable | Document flou pour verifier la hierarchie visuelle sans lire | Generer une version reduite/floutee (ou verifier les proportions) pour controler que la hierarchie est perceptible sans lecture | En reduisant le zoom a 25%, les titres, sous-titres, corps et citations doivent former des blocs visuellement distincts | reviewer | quality-loop | Verification manuelle ou par script de contraste des tailles : ratio titre/corps >= 1.3 |
| Every Element Earns Its Place | impeccable | Reduire a l'essentiel. Pas de bordures decoratives, de variations de police excessives, d'artefacts de modele | Audit de chaque element de mise en page : bordures, trames, sauts, en-tetes. Supprimer tout element qui n'a pas de fonction informative | Supprimer les bordures decoratives heritees d'un modele Word, les en-tetes vides, les sauts de section inutiles | reviewer | final-audit | Zero element decoratif sans fonction informative identifiee |
| Tight Groups + Generous Separation | impeccable | Les elements lies sont proches ; les elements distincts sont eloignes | L'espacement interne d'un bloc (titre + paragraphes) est serre. L'espacement entre blocs est nettement superieur | Titre de section + premier paragraphe : 6pt. Fin de section + titre suivant : 24pt. Ratio interne/externe >= 1:3 | verifier | docx-formatting | Ratio espacement intra-bloc / inter-bloc <= 0.4 |
| DENSITY Parameter | taste-skill | Controle de la densite informationnelle par page | Adapter la densite selon le type de document : document juridique dense vs rapport executif aere | Document dense (DENSITY=8) : marges etroites, interligne 1.0, paragraphes compacts. Document aere (DENSITY=3) : marges larges, interligne 1.5 | analyst | chapter-processing | Densite mesuree (caracteres/page) coherente avec le parametre DENSITY cible |

---

## 4. Finition humaine (Human Finish)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| Redesign Audit Protocol | taste-skill | Inspecter avant de modifier. Extraire les tokens de style, cartographier la structure, identifier les anomalies, corriger par priorite | Workflow obligatoire : extraction complete du formatage existant, identification des ecarts, plan de corrections ordonne par impact (hierarchie > paragraphes > espacement > tableaux) | Avant de reformater un chapitre : lister tous les styles utilises, detecter les incoherences, corriger d'abord la hierarchie des titres, puis les paragraphes, puis les details | inspector | document-inspection | Phase d'inspection completee avec rapport d'anomalies avant toute correction |
| Audit-Then-Plan Workflow | design-skills | Phase d'analyse en lecture seule produisant un plan autonome pour les executants | L'agent d'inspection produit un plan de corrections (`work/inspection/correction_plan.json`) que l'agent de traitement execute sans reinterpretation | Le plan liste : "P000045: changer style Normal -> BodyText", "P000102: supprimer bordure orpheline" — l'executant applique sans analyser | inspector, processor | document-inspection, chapter-processing | Plan de corrections genere et complet avant debut du traitement |
| Full-Output Enforcement | taste-skill | L'agent ne doit jamais tronquer ou sauter des paragraphes. Comparaison deterministe pour valider la completude | Apres chaque traitement de chapitre, script `compare_docx.py` verifie que tous les paragraphes source sont presents dans la sortie, sans perte ni ajout | Comparaison paragraph-par-paragraphe : meme nombre de P-IDs, meme contenu textuel (hors corrections loguees), meme ordre | verifier | integrity-validation | Delta paragraphes source/sortie = 0 (hors suppressions documentees) |
| Vocabulary Standardization | design-skills | Terminologie precise du document : veuve, orpheline, crenage, interligne, gouttiere | Utiliser un lexique normalise dans tous les logs, rapports et corrections. Jamais d'approximations ("espace bizarre", "titre mal place") | Log : "Orpheline detectee P000234 — derniere ligne isolee en haut de page" au lieu de "paragraphe coupe bizarrement" | tous | language-quality | 100% des termes techniques dans les logs correspondent au lexique normalise |
| Isolated Validation Passes | impeccable | Separer la revue de contenu de la revue de formatage pour eviter le biais d'ancrage | Deux passes distinctes et sequentielles : (1) validation du contenu/texte, (2) validation du formatage/mise en page. Jamais simultanees | Passe 1 : verifier orthographe, grammaire, coherence textuelle. Passe 2 : verifier styles, espacements, polices. Les deux passes produisent des rapports separes | reviewer, verifier | quality-loop, integrity-validation | Deux rapports de validation distincts produits pour chaque chapitre |

---

## 5. Anti-slop documentaire (Anti-Slop)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| AI Tells Catalog | taste-skill | Catalogue de marqueurs revelant un traitement IA generique | Catalogue de defauts documentaires typiques : abus de tirets cadratins, placeholders generiques ("Lorem ipsum", "[A completer]"), longueurs de paragraphes uniformes, gras excessif, styles de puces incoherents, titres orphelins | Detecter : 5 paragraphes consecutifs de longueur quasi identique (ecart < 10%) — signe de generation IA ou de copier-coller mecanique | reviewer | language-quality | Zero marqueur du catalogue anti-slop non resolu dans le document final |
| Prose Quality Linter | impeccable | Bannir les mots et patterns typiques de l'IA : "delve", "seamless", "robust", "elevate" | Liste noire adaptee au francais : "il convient de noter que", "dans le cadre de", "force est de constater", "en definitive", "il va sans dire". Detecter aussi les structures repetitives : listes de trois systematiques, paragraphes en miroir, pivots par negation | Detecter : 3 paragraphes consecutifs commencant par "Il est important de..." — structure repetitive a varier | reviewer | language-quality | Zero occurrence de la liste noire dans le document final ; variance structurelle des paragraphes > seuil |
| Uniform Paragraph Length Detection | taste-skill | Paragraphes de longueur trop uniforme = signe de traitement mecanique | Calculer l'ecart-type des longueurs de paragraphes par chapitre. Un ecart-type trop faible signale un manque de naturel | Chapitre de 20 paragraphes tous entre 80 et 90 mots : ecart-type < 5% de la moyenne = alerte | reviewer | quality-loop | Ecart-type des longueurs de paragraphes par chapitre > 15% de la moyenne |
| Excessive Bold / Generic Formatting | taste-skill | Trop de gras noie l'information ; le formatage generique ne guide pas la lecture | Audit du ratio de texte en gras : maximum 5% du corps de texte. Verifier que le gras sert la hierarchie et non la decoration | Document ou 30% du texte est en gras : le gras perd sa fonction de mise en relief. Reduire aux termes vraiment saillants | reviewer | quality-loop | Ratio texte gras / texte total < 5% dans le corps (hors titres) |
| Inconsistent Bullet Styles | taste-skill | Styles de puces melanges = desordre visuel | Verifier la coherence des puces dans tout le document : un seul style de puce par niveau de liste. Pas de melange tiret/point/fleche au meme niveau | Liste niveau 1 : toujours des tirets. Liste niveau 2 : toujours des points. Jamais de melange au sein d'un meme niveau dans le document | verifier | integrity-validation | Un seul caractere de puce par niveau de liste dans tout le document |
| Negation Pivot Detection | impeccable | Structure "X n'est pas Y, mais Z" utilisee de maniere repetitive = pattern IA | Detecter les pivots par negation repetes dans un meme chapitre (plus de 2 occurrences du pattern "ne...pas...mais") | "Il ne s'agit pas de..., mais de..." repete 4 fois dans un chapitre : pattern a varier | reviewer | language-quality | Maximum 2 pivots par negation par chapitre |

---

## 6. Audit & Qualite (Audit & Quality)

| Principe source | Repo | Interpretation | Adaptation documentaire | Exemple DOCX/PDF | Agent concerne | Skill concernee | Critere QA |
|---|---|---|---|---|---|---|---|
| Pre-Flight Check Matrix | taste-skill | 50+ items binaires pass/fail avant livraison du document | Matrice de verification finale couvrant typographie, mise en page, coherence, accessibilite. Chaque item est binaire (OK/KO) sans zone grise | Checklist : guillemets corrects [OK], hierarchie titres continue [OK], pas de page blanche orpheline [OK], table des matieres a jour [KO] — blocage | verifier | final-audit | 100% des items de la matrice en statut OK avant export |
| Deterministic Pattern Detection | impeccable | 61 regles sans LLM. Portage en linter DOCX pour coherence des polices, echelle d'espacement, hierarchie des titres, contraste | Scripts Python deterministes dans `scripts/` : verification des polices, des espacements, de la hierarchie, des contrastes. Le LLM ne se substitue jamais au script | `check_unicode.py` verifie les caracteres speciaux ; `validate_layout.py` verifie la mise en page ; `compare_docx.py` verifie l'integrite | verifier | integrity-validation | Tous les scripts deterministes passent sans erreur |
| Multi-Dimensional Scoring | impeccable | Score sur 5 dimensions (0-4 chacune). Severite P0-P3. "Un scan propre est une preuve, pas une certitude" | Scoring du document final sur 5 axes : Structure (0-4), Typographie (0-4), Coherence (0-4), Completude (0-4), Accessibilite (0-4). Severite des defauts : P0 (bloquant), P1 (majeur), P2 (mineur), P3 (suggestion) | Score final : Structure 4/4, Typographie 3/4 (P2: interligne note de bas de page), Coherence 4/4, Completude 4/4, Accessibilite 2/4 (P1: contraste insuffisant) | reviewer | final-audit | Score global >= 16/20 ; zero defaut P0 ; maximum 2 defauts P1 |
| Non-Negotiable Standards | design-skills | Checklist binaire (Block/Approve) avec declencheurs d'escalade | Certains criteres sont absolus et non negociables : integrite du contenu (aucune perte), hierarchie des titres (pas de saut de niveau), encodage Unicode correct | Si un seul paragraphe est perdu entre source et sortie : verdict BLOCK immediat, pas de compromis | verifier | integrity-validation | Zero violation des criteres non negociables (liste definie dans config) |
| LLM Output is Not Proof | impeccable / CLAUDE.md | La sortie du LLM n'est pas une preuve d'integrite. Toujours verifier par scripts deterministes | Regle fondamentale de DocForge : chaque affirmation du LLM sur l'integrite du document est verifiee par `compare_docx.py`, `check_unicode.py`, `validate_layout.py` | L'agent dit "tous les paragraphes sont presents" — le script `compare_docx.py` confirme ou infirme de maniere deterministe | verifier | integrity-validation | Verification script obligatoire apres chaque affirmation d'integrite par le LLM |
| Clean Scan is Evidence, Not Proof | impeccable | Un passage reussi des tests est un indice, pas une certitude absolue | Meme si tous les scripts passent, le rapport de qualite mentionne les limites : ce qui a ete verifie et ce qui ne l'a pas ete. Pas de faux sentiment de completude | Rapport final : "Verification automatique : 47/47 tests passes. Limites : contraste des images non verifie, coherence semantique non evaluee" | reviewer | final-audit | Rapport de qualite inclut une section "Limites de la verification automatique" |
| 5-Iteration Limit | CLAUDE.md | Apres 5 echecs QA sur un chapitre, marquer PENDING_MANUAL et passer au suivant | Eviter les boucles infinies de correction. Chaque iteration est loguee. Au-dela de 5, l'intervention humaine est requise | Chapitre 3 echoue 5 fois sur la verification d'espacement : marque PENDING_MANUAL, le pipeline continue avec le chapitre 4 | verifier | quality-loop | Nombre d'iterations QA par chapitre <= 5 ; statut PENDING_MANUAL si atteint |
| Local Errors Don't Stop Pipeline | CLAUDE.md | Un echec de chapitre ne bloque pas les autres chapitres | Isolation des erreurs : chaque chapitre est traite independamment. Un echec est logue et le pipeline continue | Chapitre 7 a une erreur de police non resoluble : logue, marque en erreur, les chapitres 8-12 sont traites normalement | verifier | quality-loop | Pipeline complete meme avec des chapitres en erreur ; rapport final liste tous les chapitres en erreur |

---

## Matrice de priorite des corrections

L'ordre de traitement des corrections suit une hierarchie stricte :

| Priorite | Categorie | Exemples | Severite |
|---|---|---|---|
| 1 | Integrite du contenu | Paragraphes manquants, contenu altere | P0 — Bloquant |
| 2 | Hierarchie structurelle | Sauts de niveaux de titre, sections mal ordonnees | P0 — Bloquant |
| 3 | Encodage et caracteres | Unicode incorrect, caracteres corrompus | P0 — Bloquant |
| 4 | Typographie fondamentale | Polices incorrectes, tailles hors specification | P1 — Majeur |
| 5 | Espacement et rythme | Interlignes irreguliers, marges incoherentes | P1 — Majeur |
| 6 | Coherence visuelle | Styles de puces melanges, gras excessif | P2 — Mineur |
| 7 | Qualite de prose | Patterns IA, repetitions structurelles | P2 — Mineur |
| 8 | Finition | Veuves/orphelines, coupures de mots | P3 — Suggestion |

---

## Mapping agents DocForge

| Agent | Role dans cette synthese |
|---|---|
| inspector | Lecture prealable, extraction des tokens de style, detection des anomalies |
| analyst | Analyse structurelle, calibrage des trois parametres (formality/density/richness) |
| processor | Execution des corrections selon le plan, sans reinterpretation |
| reviewer | Verification qualitative, detection anti-slop, scoring multi-dimensionnel |
| verifier | Verification deterministe par scripts, matrice pre-vol, criteres non negociables |

---

## Mapping skills DocForge

| Skill | Principes integres |
|---|---|
| document-inspection | Document Read, Redesign Audit Protocol, Audit-Then-Plan |
| structure-analysis | Multi-Axis Hierarchy, Three-Dial System, Design Specificity |
| chapter-processing | Frequency-Based Decisions, DENSITY Parameter, Audit-Then-Plan |
| language-quality | Em-Dash Ban, Prose Quality Linter, AI Tells Catalog, Vocabulary Standardization |
| docx-formatting | Size-Dependent Tracking, Spacing Rhythm, Typography as Architecture, Design Tokens |
| integrity-validation | Full-Output Enforcement, Deterministic Pattern Detection, Font Role Consistency |
| quality-loop | Squint Test, Isolated Validation Passes, 5-Iteration Limit, Multi-Dimensional Scoring |
| final-audit | Pre-Flight Check Matrix, Non-Negotiable Standards, Every Element Earns Its Place, Clean Scan |

---

## References

| Depot source | URL | Licence | Principes extraits |
|---|---|---|---|
| Leonxlnx/taste-skill | github.com/Leonxlnx/taste-skill | MIT | Brief Inference, Three-Dial, AI Tells, Pre-Flight, Redesign Audit, Em-Dash Ban, Full-Output |
| emilkowalski/skills | github.com/emilkowalski/skills | MIT | Frequency-Based, Purpose-Justified, Audit-Then-Plan, Typography Rules, Design Tokens, Non-Negotiable, Vocabulary |
| pbakaus/impeccable | github.com/pbakaus/impeccable | MIT | Deterministic Detection, Swap Test, Typography Architecture, Spacing Rhythm, Prose Linter, Every Element, Multi-Dimensional Scoring |
