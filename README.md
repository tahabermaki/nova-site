# Nova AI Systems — Site web

Site vitrine + Nova Assistant (chatbot commercial IA avec base de connaissances et recherche intelligente).

## Structure du projet

```
nova-site/
├── index.html                    # Le site complet (HTML/CSS/JS, autonome)
├── assets/
│   ├── logo.png                  # Logo fond transparent (haute résolution)
│   └── logo-small.png            # Version optimisée (embarquée en base64 dans le HTML)
├── docs/
│   └── agents-documentation.md   # Documentation des agents = base de connaissances du chatbot
└── backend/
    └── main.py                   # Proxy FastAPI → API Claude (pour la production)
```

## Oui : passe sur VSCode maintenant

Le site est devenu un vrai projet (logo, chatbot, base de connaissances, backend). Workflow recommandé :

1. Copier ce dossier dans `C:\Users\tahae\Desktop\nova-site\`
2. `git init` + push vers GitHub (`github.com/tahabermaki/nova-site`, privé)
3. Ouvrir dans VSCode + extension **Live Server** pour prévisualiser `index.html`
4. Continuer les itérations avec Claude (Claude Code est idéal pour ça)

## Le chatbot — comment ça marche

- **Base de connaissances** : l'objet `KNOWLEDGE` dans `index.html`, miroir condensé de `docs/agents-documentation.md`. Pour modifier ce que le chatbot sait → éditer les deux.
- **Recherche intelligente (économie de tokens)** : à chaque message, un scoring par mots-clés sélectionne les 2-3 sections pertinentes. Seules celles-ci sont injectées dans le prompt — jamais toute la doc. Coût par échange ≈ 700-900 tokens d'entrée au lieu de ~2500.
- **Modèle** : Claude Haiku (`claude-3-5-haiku-20241022`) — rapide, ~10x moins cher que Sonnet, largement suffisant avec une bonne base de connaissances.
- **Limite de conversation** : 5 échanges, puis l'assistant propose le RDV conseiller et l'input se ferme. Coût maîtrisé + conversion.
- **Escalade** : le modèle termine par le marqueur `[RDV]` quand la demande est sérieuse → le JS affiche un bouton Calendly.

## Déploiement

### Frontend (Netlify — comme immo.novaaisystems.fr)
1. Drag & drop du dossier sur Netlify (ou connecter le repo GitHub)
2. Domaine : `novaaisystems.fr` via one.com (enregistrement CNAME)

### Backend (Railway)
1. Nouveau projet Railway → déployer `backend/`
2. Variable d'environnement : `ANTHROPIC_API_KEY`
3. Dans `index.html`, remplacer l'URL du fetch :
   ```js
   // avant (preview Claude uniquement)
   fetch('https://api.anthropic.com/v1/messages', ...)
   // après (production)
   fetch('https://TON-APP.up.railway.app/api/chat', ...)
   ```
   et retirer le champ `model` du body (le backend le fixe).

⚠️ **Jamais de clé API dans le frontend** — toujours via le proxy.

## Checklist avant mise en ligne

- [ ] Backend Railway déployé + URL mise à jour dans index.html (fetch du chat **et** `LEAD_ENDPOINT`)
- [ ] Variables Railway : `ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `LEAD_TO`
- [ ] Resend : vérifier le domaine `novaaisystems.fr` (DNS chez one.com) pour envoyer depuis `leads@novaaisystems.fr`
- [ ] Pixel LinkedIn : remplacer `LINKEDIN_PARTNER_ID` (2 occurrences) par ton ID — Campaign Manager > Analyse > Insight Tag
- [ ] **Témoignage cas concret : faire valider la citation par le client (Y.) et la remplacer par ses vrais mots**
- [ ] CORS du backend limité au domaine final
- [ ] Tester le chatbot + la capture d'email sur mobile
- [ ] Vérifier les 3 templates d'email (boutons footer)
- [ ] Calendly : https://calendly.com/taha-elbermaki-novaaisystems/30min partout
- [ ] Favicon ok (logo embarqué)
