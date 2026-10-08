# O'Tools

Addon personnel pratique pour affichage rigging & animation sous Blender 3.6+.

### Installation
À partir de Blender 4.2, ajoute le dépôt. Les versions suivantes se mettent à jour dans Blender.

1. Edit → Preferences → Get Extensions
2. En haut à droite : Repositories → **+** → Add Remote Repository
3. Coller l’adresse : `https://olanlive.github.io/o_tools/index.json`
4. Cocher **Check for Updates on Startup**, sous l’adresse
5. Installer **O'Tools**, puis l’activer

Si O'Tools, ou l’ancienne « O Tools », a déjà été installé par zip, désinstalle cette copie avant : Preferences → Add-ons → fiche de l’addon → Uninstall. Sinon Blender affiche les deux, l’ancienne dans le dépôt local et la nouvelle dans le dépôt ajouté.

Le zip reste disponible, y compris pour Blender 3.6. Cette installation ne prévient pas des mises à jour suivantes.

1. Aller dans **Releases** → télécharger le .zip le plus récent  
   → https://github.com/olanlive/o_tools/releases
2. Blender → Edit → Preferences → Add-ons → Install → sélectionner le .zip → Enable

### Fonctionnalités
- **Bone Wire / In Front** toggle
<img src="docs/Bone_Wire_In_Front.gif?raw=true" width="400" alt="Bone Wire / In Front demo">

- **Smart Slow-Mo** : multiple intelligent du FPS original  
  → 24 → 6 fps 25 → 5 fps 30 → 6 fps 50 → 10 fps 60 → 12 fps etc.
<img src="docs/Slow-Mo.gif?raw=true" width="400" alt="Slow-Mo demo">

- **Profil Viewport** : silhouette noire propre  
  → Flat + fond noir + overlays/gizmos désactivés  
  → fonctionne depuis **n’importe quel mode**  
  → retour **exact** à l’état précédent (multi-viewport)
<img src="docs/Profil_Viewport.gif?raw=true" width="400" alt="Profil Viewport demo">

- **Status Bar Filename** : affiche le nom du fichier .blend en bas à droite de la status bar (avec * si modifié)
  → Très pratique en plein écran où le titre est masqué  
  → Idéal quand on travaille avec des versions numérotées (.blend001, .blend002…)
<img src="docs/status_bar_filename.png?raw=true" width="200" alt="Status Bar Filename">

- **Préférences** : cases à cocher pour activer/désactiver chaque fonctionnalité individuellement (Preferences → Add-ons → O'Tools)

### Auteur
Olivier L with Grok  
Licence GPL-3.0

---

# O'Tools

Useful personal add-on for rigging & animation display in Blender 3.6+.

### Installation
From Blender 4.2, add the repository. Later versions update inside Blender.

1. Edit → Preferences → Get Extensions
2. Top right: Repositories → **+** → Add Remote Repository
3. Paste this address: `https://olanlive.github.io/o_tools/index.json`
4. Check **Check for Updates on Startup**, under the address
5. Install **O'Tools**, then enable it

If O'Tools, or the older “O Tools”, was already installed from a zip, uninstall that copy first: Preferences → Add-ons → the add-on entry → Uninstall. Otherwise Blender shows both, the old one in the local repository and the new one in the repository you add.

The zip remains available, including for Blender 3.6. That install does not notify you of later updates.

1. Go to **Releases** → download the latest .zip  
   → https://github.com/olanlive/o_tools/releases
2. Blender → Edit → Preferences → Add-ons → Install → select the .zip → Enable

### Features
- **Bone Wire / In Front** toggle
<img src="docs/Bone_Wire_In_Front.gif?raw=true" width="400" alt="Bone Wire / In Front demo">

- **Smart Slow-Mo** : clean integer multiple of original FPS  
  → 24 → 6 fps 25 → 5 fps 30 → 6 fps 50 → 10 fps 60 → 12 fps etc.
<img src="docs/Slow-Mo.gif?raw=true" width="400" alt="Slow-Mo demo">

- **Profil Viewport** : clean black silhouette  
  → Flat shading + black background + overlays/gizmos hidden  
  → works from **any viewport mode**  
  → **exact** restoration of previous state (multi-viewport)
<img src="docs/Profil_Viewport.gif?raw=true" width="400" alt="Profil Viewport demo">

- **Status Bar Filename** : displays current .blend filename on the right of the status bar (with * if modified)  
  → Very useful in full-screen mode where the title is hidden  
  → Perfect when working with numbered versions (.blend001, .blend002…)
<img src="docs/status_bar_filename.png?raw=true" width="200" alt="Status Bar Filename">

- **Preferences** : checkboxes to enable/disable each feature individually (Preferences → Add-ons → O'Tools)

### Author
Olivier L with Grok  

License GPL-3.0
