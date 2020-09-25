- [Mode d'emploi](#orgb450709)
  - [Installation](#org257e70a)
  - [Fichier de configuration](#org511b151)
  - [Usage](#org08a5611)
- [Concept](#orgf789d62)
  - [Pourquoi ?](#org223b88a)
  - [Comment ?](#orgd31efd2)
- [Implémentation](#orgfe65d05)
  - [Package declaration](#org77d2b8e)
    - [Fichier de setup](#org969630b)
  - [Cli](#org58bc105)
  - [Dépendances](#org38930fa)
  - [Class](#orgbb94ccc)
    - [Init](#orge4c041d)
    - [Print Helpers](#orgc4fe988)
    - [Json data files](#orga75758f)
    - [Préparation](#orgb824294)
    - [Compilation](#org33ba628)
- [Déploiement vers Pypi](#org5b23ca4)
- [Github Pages](#org99544f3)


<a id="orgb450709"></a>

# TODO Mode d'emploi


<a id="org257e70a"></a>

## Installation

```bash
pip install fast-eval
```


<a id="org511b151"></a>

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
  ],
  "execution_commands": [
    "./exo1"
  ]
}
```


<a id="org08a5611"></a>

## Usage

```bash
fast-eval -h
```


<a id="orgf789d62"></a>

# Concept


<a id="org223b88a"></a>

## Pourquoi ?

L'objectif de ce projet est de faciliter l'évaluation de TPs d'info. Généralement la procédure d'évaluation est la même :

-   **Récupération:** Je récupère tous les travaux soumis dans une unique archive fournie par Arche. (manuellement pour l'instant, il ne semble pas qu'il y ait d'API arche accessible).

-   **Préparation:** Chaque travail est généralement soumis sous la forme d'une archive, dont l'organisation varie souvent énormément d'un étudiant à l'autre. Cette partie est donc fastidieuse : il faut extraire un à un chaque archive, puis chercher les fichiers réellement utiles (en général un ou plusieurs fichiers source).

-   **Compilation:** Selon le projet et le langage, exécution de make, gcc etc&#x2026; Idem, c'est fastidieux, et facilement scriptable.

-   **Exécution et évaluation:** Faire tourner le programme et voir ce que cela donne. Une partie plus ou moins couvrante peut être déléguée à des logiciels de tests, permettant d'avoir rapidement une idée de la pertinence de la solution soumise.


<a id="orgd31efd2"></a>

## Comment ?

Automatisation de la préparation, compilation et pourquoi pas d'une partie de l'évaluation.

Cette automatisation ce concrétise par un programme python permettant de faire une grosse partie du travail fastidieux et répétitif nécessaire lors de l'évaluation de TPs/projets.


<a id="orgfe65d05"></a>

# Implémentation


<a id="org77d2b8e"></a>

## Package declaration


<a id="org969630b"></a>

### Fichier de setup

```python
# -*- coding: utf-
from setuptools import setup, find_packages

setup(
    name='fast-eval',
    packages=find_packages(exclude=["examples/*"]),
    version='0.2.0',
    description='Simple tool to provide automation to assessment processes.',
    author=u'Virgile Daugé',
    author_email='virgile.dauge@pm.me',
    url='https://github.com/Virgile-Dauge/fast-eval',
    # download_url='',
    keywords=['assessment', 'evaluation'],
    install_requires=['colored'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        ],
    entry_points={
        'console_scripts': [
            'fast-eval=fast_eval.__main__:main',
        ],
    },
    python_requires='>=3.6',
)
```

```bash
mkdir fast_eval
tree .
```

```python

```


<a id="org58bc105"></a>

## Cli

```python
#!/usr/bin/env python3
import argparse
from fast_eval.util import FastEval
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        help="path of json config file")
    parser.add_argument("archive_path",
                        help="path of archive from arche")
    parser.add_argument("--ws",
                        help="where to build workspace")
    fe = FastEval(parser.parse_args())

```


<a id="org38930fa"></a>

## Dépendances

```python
# Pour lecture de dossiers/fichiers
import os
import sys
import csv
import json
# Pour affichage de dict
import pprint
# Pour décomprésser
import shutil
# Pour Exécution de programmes
import subprocess

from colored import fg, bg, attr
# Helpers

def search_files(directory='.', extension=''):
    extension = extension.lower()
    found = []
    for dirpath, _, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                found.append(os.path.join(dirpath, name))
            elif not extension:
                found.append(os.path.join(dirpath, name))
    return found
def choice_str(choices, target=''):
    res = '. ' + str(target) + '\n' + '│\n'
    for choice in choices[:-1]:
      res = res + '├── ' + str(choice) + '\n'
    res = res + '└── ' + choices[-1]
    return res
```


<a id="orgbb94ccc"></a>

## TODO Class


<a id="orge4c041d"></a>

### Init

Initialization :

```python
class FastEval:
    """
    @brief Simple tool to provide automation to assessment processes.
    @details Provide tools to build, compile and evaluatue a suitable
    workspace with a specific working folder for each submitted
    project from a single compressed archive.

    """
    def __init__(self, args):
        "docstring"
        self.ecolor = bg('indian_red_1a') + fg('white')
        #self.ecolor = fg('red_3a')
        #self.wcolor = bg('orange_1') + fg('white')
        self.wcolor = fg('orange_1')
        #self.icolor = bg('deep_sky_blue_2') + fg('white')
        self.icolor = fg('deep_sky_blue_2')
        self.rcolor = attr('reset')

        if args.ws:
            self.workspace_path = os.path.expanduser(args.ws)
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print('Using  {} as workspace'.format(self.info_str(self.workspace_path)))

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print('Given  {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.archive_path)),
                  file=sys.stderr)
            sys.exit()

        config = os.path.expanduser(args.config)
        assert os.path.isfile(config), "{} is not a file.".format(config)

        with open(config, 'r') as fp:
            config = json.load(fp)
        self.required_files = config['required_files']

        if len(config['reference_folder']) > 0:
            self.ref_path = os.path.expanduser(config['reference_folder'])
            if not os.path.isdir(self.ref_path):
                print('Given  {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.ref_path)),
                  file=sys.stderr)
                sys.exit()
            print('Using  {} as reference folder'.format(self.info_str(self.ref_path)))
        else:
            self.ref_path = None
            print('Not using ref folder')

        self.comp_cmd = config['compilation_commands']
        self.exec_cmd = config['execution_commands']

        self.submissions = {}
        # Chargement de la config
        self.load_data()
        # Si c'est le premier passage, il faut lancer la preparation
        if self.pass_count == 0:
            shutil.unpack_archive(self.archive_path, self.workspace_path)
            submissions = self.clean_dirs()
            print('Processing {} projects...\n'.format(len(self.submissions)))
            self.submissions = {key: dict(value, **{'step' : '0_prep', 'steps': {'0_prep' : {},
                                                                                 '1_comp' : {},
                                                                                 '2_exec' : {},
                                                                                 '3_eval' : {}}}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
        else:
            print('Processing {} projects...\n'.format(len(self.submissions)))
        self.prep_step()
        self.exte_step(self.comp_cmd, step='1_comp', label='Compiling')
        #self.exte_step(self.exec_cmd, step='2_exec', label='Executing')
        self.write_data()

    def load_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        #data = load_json(data_file)
        try:
            with open(data_file, 'r') as fp:
                data = json.load(fp)


            self.pass_count = data['pass_count'] + 1
            self.submissions = data['submissions']
            print('Loaded ' + self.info_str(data_file) + ' savefile.\n')
        except FileNotFoundError:
            print('Using  ' + self.info_str(data_file) + ' savefile.\n')
            self.pass_count = 0
    def write_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        try:
            with open(data_file, 'w') as fp:
                json.dump({'pass_count': self.pass_count,
                           'submissions': self.submissions},
                          fp, sort_keys=True, indent=4, ensure_ascii=False)
            print('Wrote  ' + self.info_str(data_file) + ' savefile.')
        except:
            print('Error while writing : \n => {}\n'.format(data_file),
                  file=sys.stderr)

    def clean_dirs(self):
        submissions = {o[:-32]:{"path": os.path.join(self.workspace_path, o)} for o in os.listdir(self.workspace_path)
                       if os.path.isdir(os.path.join(self.workspace_path, o))}
        for sub in submissions.values():
            if not os.path.exists(sub["path"][:-32]):
                shutil.move(sub['path'], sub['path'][:-32])
            if 'assignsubmission_file' in sub ['path']:
                sub['path'] = sub['path'][:-32]
        return submissions
    def extract_dirs(self):
        for sub in self.submissions:
            raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
            os.mkdir(raw_dir)
            for o in os.listdir(self.submissions[sub]['path']):
                shutil.move(os.path.join(self.submissions[sub]['path'],o), raw_dir)
            files = [os.path.join(raw_dir, o) for o in os.listdir(raw_dir)]
            try:
                shutil.unpack_archive(files[0], raw_dir)
                os.remove(files[0])
            except shutil.ReadError:
                print('Unpack ' + self.warn_str(files[0]) + ' failed.')

    def copy_ref(self):
        if self.ref_path is not None:
            for sub in self.submissions:
                shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))

    def prep_step(self):
        to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print('Preparing  {} projects...'.format(len(to_prep)))
        for sub in to_prep:
            raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
            eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')

            if not os.path.exists(eval_dir):
                os.mkdir(eval_dir)

            missing_files = []

            # Search every required files one by one
            for f in self.required_files:
                # List cadidates for searched file
                student_code = search_files(raw_dir, f)
                # Filter files in a "__MACOS" directory
                student_code = [s for s in student_code if '__MACOS' not in s]
                if len(student_code) == 1:
                    shutil.copyfile(student_code[0], os.path.join(eval_dir, f))
                elif len(student_code) == 0:
                    missing_files.append(f)
                else:
                    msg = 'You need to manually copy one of those files'
                    msg = msg + choice_str(student_code, f)
                    self.submissions[sub]['steps']['0_prep']['msg'] = msg

            # Update missing files if needed
            if missing_files:
                if 'missing_files' not in self.submissions[sub]['steps']['0_prep']:
                    self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
                else:
                    self.submissions[sub]['steps']['0_prep']['missing_files'].extend(missing_files)
            else:
                self.submissions[sub]['step'] = '1_comp'

        to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print('           ' + self.erro_str('{} fails.'.format(len(to_prep))) + '\n')
    def exte_step(self, cmd, step='1_comp', label='Compiling'):
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        print('{}  {} projects...'.format(label, len(to_exec)))
        root_dir = os.getcwd()
        for sub in to_exec:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            for c in cmd:
                completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
                if completed_process.returncode == 0:
                    self.submissions[sub]['step'] = self.next_step(step)
                    if len(completed_process.stderr) > 0:
                        self.submissions[sub]['steps'][step][c] = completed_process.stderr.split('\n')

        os.chdir(root_dir)
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        print('           ' + self.erro_str('{} fails.'.format(len(to_exec))) + '\n')

    def next_step(self, step):
        if step == '0_prep':
            return '1_comp'
        elif step == '1_comp':
            return '2_exec'
        elif step == '2_exec':
            return '3_eval'
        else:
            return 'done'
    def erro_str(self, msg):
        return self.ecolor + str(msg) + self.rcolor
    def warn_str(self, msg):
        return self.wcolor + str(msg) + self.rcolor
    def info_str(self, msg):
        return self.icolor + str(msg) + self.rcolor


```


<a id="orgc4fe988"></a>

### Print Helpers

```python
def choice_str(choices, target=''):
    res = '. ' + str(target) + '\n' + '│\n'
    for choice in choices[:-1]:
      res = res + '├── ' + str(choice) + '\n'
    res = res + '└── ' + choices[-1]
    return res
```

```python
def warn_str(self, msg):
    return self.wcolor + str(msg) + self.rcolor
```

```python
def erro_str(self, msg):
    return self.ecolor + str(msg) + self.rcolor
```

```python
def info_str(self, msg):
    return self.icolor + str(msg) + self.rcolor
```


<a id="orga75758f"></a>

### Json data files

```python
def load_data(self):
    data_file = os.path.join(self.workspace_path, 'data.json')
    #data = load_json(data_file)
    try:
        with open(data_file, 'r') as fp:
            data = json.load(fp)


        self.pass_count = data['pass_count'] + 1
        self.submissions = data['submissions']
        print('Loaded ' + self.info_str(data_file) + ' savefile.\n')
    except FileNotFoundError:
        print('Using  ' + self.info_str(data_file) + ' savefile.\n')
        self.pass_count = 0
```

```python
def write_data(self):
    data_file = os.path.join(self.workspace_path, 'data.json')
    try:
        with open(data_file, 'w') as fp:
            json.dump({'pass_count': self.pass_count,
                       'submissions': self.submissions},
                      fp, sort_keys=True, indent=4, ensure_ascii=False)
        print('Wrote  ' + self.info_str(data_file) + ' savefile.')
    except:
        print('Error while writing : \n => {}\n'.format(data_file),
              file=sys.stderr)

```


<a id="orgb824294"></a>

### Préparation

```python
def clean_dirs(self):
    submissions = {o[:-32]:{"path": os.path.join(self.workspace_path, o)} for o in os.listdir(self.workspace_path)
                   if os.path.isdir(os.path.join(self.workspace_path, o))}
    for sub in submissions.values():
        if not os.path.exists(sub["path"][:-32]):
            shutil.move(sub['path'], sub['path'][:-32])
        if 'assignsubmission_file' in sub ['path']:
            sub['path'] = sub['path'][:-32]
    return submissions
```

```python
def extract_dirs(self):
    for sub in self.submissions:
        raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
        os.mkdir(raw_dir)
        for o in os.listdir(self.submissions[sub]['path']):
            shutil.move(os.path.join(self.submissions[sub]['path'],o), raw_dir)
        files = [os.path.join(raw_dir, o) for o in os.listdir(raw_dir)]
        try:
            shutil.unpack_archive(files[0], raw_dir)
            os.remove(files[0])
        except shutil.ReadError:
            print('Unpack ' + self.warn_str(files[0]) + ' failed.')

```

```python
def copy_ref(self):
    if self.ref_path is not None:
        for sub in self.submissions:
            shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))

```

```python
def prep_step(self):
    to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    print('Preparing  {} projects...'.format(len(to_prep)))
    for sub in to_prep:
        raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
        eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')

        if not os.path.exists(eval_dir):
            os.mkdir(eval_dir)

        missing_files = []

        # Search every required files one by one
        for f in self.required_files:
            # List cadidates for searched file
            student_code = search_files(raw_dir, f)
            # Filter files in a "__MACOS" directory
            student_code = [s for s in student_code if '__MACOS' not in s]
            if len(student_code) == 1:
                shutil.copyfile(student_code[0], os.path.join(eval_dir, f))
            elif len(student_code) == 0:
                missing_files.append(f)
            else:
                msg = 'You need to manually copy one of those files'
                msg = msg + choice_str(student_code, f)
                self.submissions[sub]['steps']['0_prep']['msg'] = msg

        # Update missing files if needed
        if missing_files:
            if 'missing_files' not in self.submissions[sub]['steps']['0_prep']:
                self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
            else:
                self.submissions[sub]['steps']['0_prep']['missing_files'].extend(missing_files)
        else:
            self.submissions[sub]['step'] = '1_comp'

    to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    print('           ' + self.erro_str('{} fails.'.format(len(to_prep))) + '\n')
```

```python
def search_files(directory='.', extension=''):
    extension = extension.lower()
    found = []
    for dirpath, _, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                found.append(os.path.join(dirpath, name))
            elif not extension:
                found.append(os.path.join(dirpath, name))
    return found
```


<a id="org33ba628"></a>

### Compilation

```python
def next_step(self, step):
    if step == '0_prep':
        return '1_comp'
    elif step == '1_comp':
        return '2_exec'
    elif step == '2_exec':
        return '3_eval'
    else:
        return 'done'
```

```python
def exte_step(self, cmd, step='1_comp', label='Compiling'):
    to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    print('{}  {} projects...'.format(label, len(to_exec)))
    root_dir = os.getcwd()
    for sub in to_exec:
        os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
        for c in cmd:
            completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
            if completed_process.returncode == 0:
                self.submissions[sub]['step'] = self.next_step(step)
                if len(completed_process.stderr) > 0:
                    self.submissions[sub]['steps'][step][c] = completed_process.stderr.split('\n')

    os.chdir(root_dir)
    to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    print('           ' + self.erro_str('{} fails.'.format(len(to_exec))) + '\n')

```


<a id="org5b23ca4"></a>

# Déploiement vers Pypi

```bash
rm -rf dist/
python setup.py sdist
```

```bash
twine upload dist/*
```


<a id="org99544f3"></a>

# Github Pages

```bash
mkdir docs
```

```yaml
theme: jekyll-theme-architect
```

```bash
cp readme.md docs/index.md
```
