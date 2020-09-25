- [Mode d'emploi](#org7d247b3)
  - [Installation](#org10ceff9)
  - [Fichier de configuration](#org1f2499b)
  - [Usage](#orga909b14)


<a id="org7d247b3"></a>

# TODO Mode d'emploi


<a id="org10ceff9"></a>

## Installation

```bash
pip install fast-eval
```


<a id="org1f2499b"></a>

## Fichier de configuration

Champs à adapter :

-   **required<sub>files</sub>:** Fichiers à chercher dans le rendu des étudiants.

-   **reference<sub>folder</sub>:** Dossier dont le contenu est à copier dans le dossier d'évaluation de chaque rendu. Cela peut être des *headers* nécessaires à la compilation, des programmes de tests etc&#x2026; Chaîne vide si pas besoin de dossier de référence.

-   **comp<sub>commands</sub>:** Liste de commandes à effectuer lors de l'étape de compilation. Liste vide si rien à faire.

```json
{
  "required_files": [
    "exo1.c"
  ],
  "reference_folder": "~/coucou_ref",
  "compilation_commands": [
    "gcc exo1.c -o exo1 -Wall"
  ]
}
```


<a id="orga909b14"></a>

## Usage

```bash
fast-eval -h
```
