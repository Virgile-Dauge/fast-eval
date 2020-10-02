- [Mode d'emploi](#org48c3817)
  - [Installation](#org1701640)
  - [Fichier de configuration](#orgcada118)
  - [Usage](#org65c91cd)
- [Concept](#org96387ca)
  - [Pourquoi ?](#orgaa5e89b)
  - [Comment ?](#orgeb6355f)
- [Implémentation](#org970686a)
  - [Package declaration](#org37a1c4c)
    - [Fichier de setup](#org518782d)
  - [Cli](#orgea6d15e)
  - [Dépendances](#org9f10d86)
  - [Class](#org6e6b3b6)
    - [Init](#org3e155b9)
    - [Print Helpers](#org0fc539e)
    - [Json data files](#org74b6129)
    - [Préparation](#org5148199)
    - [Compilation](#orgcb2169a)
- [Déploiement vers Pypi](#orgf7785ae)
- [Github Pages](#orgaa1b01d)


<a id="org48c3817"></a>

# TODO Mode d'emploi


<a id="org1701640"></a>

## Installation

```bash
pip install fast-eval
```


<a id="orgcada118"></a>

## Fichier de configuration

Champs à adapter :

-   **required<sub>files</sub>:** Fichiers à chercher dans le rendu des étudiants.

-   **reference<sub>folder</sub>:** Dossier dont le contenu est à copier dans le dossier d'évaluation de chaque rendu. Cela peut être des *headers* nécessaires à la compilation, des programmes de tests etc&#x2026; Chaîne vide si pas besoin de dossier de référence.

-   **comp<sub>commands</sub>:** Liste de commandes à effectuer lors de l'étape de compilation. Liste vide si rien à faire.

-   **execution<sub>commands</sub>:** Liste de commandes à effectuer lors de l'étape d'exécution/évaluation. Liste vide si rien à faire.

```json
{
    "required_files": [
        "hello.c",
        "nohello.c"
    ],
    "reference_folder": "~/coucou_ref",
    "compilation_commands": [
        "gcc hello.c -o hello -Wall",
        "gcc nohello.c -o nohello -Wall"
    ],
    "execution_commands": [
        "./hello",
        "./nohello"
    ]
}
```


<a id="org65c91cd"></a>

## Usage

```bash
fast-eval -h
```

    usage: fast-eval [-h] [-ws WORKSPACE] [-v {0,1,2}] config archive_path

    positional arguments:
      config                path of json config file
      archive_path          path of archive from arche

    optional arguments:
      -h, --help            show this help message and exit
      -ws WORKSPACE, --workspace WORKSPACE
                            where to build workspace
      -v {0,1,2}, --verbosity {0,1,2}
                            increase output verbosity


<a id="org96387ca"></a>

# Concept


<a id="orgaa5e89b"></a>

## Pourquoi ?

L'objectif de ce projet est de faciliter l'évaluation de TPs d'info. Généralement la procédure d'évaluation est la même :

-   **Récupération:** Je récupère tous les travaux soumis dans une unique archive fournie par Arche. (manuellement pour l'instant, il ne semble pas qu'il y ait d'API arche accessible).

-   **Préparation:** Chaque travail est généralement soumis sous la forme d'une archive, dont l'organisation varie souvent énormément d'un étudiant à l'autre. Cette partie est donc fastidieuse : il faut extraire un à un chaque archive, puis chercher les fichiers réellement utiles (en général un ou plusieurs fichiers source).

-   **Compilation:** Selon le projet et le langage, exécution de make, gcc etc&#x2026; Idem, c'est fastidieux, et facilement scriptable.

-   **Exécution et évaluation:** Faire tourner le programme et voir ce que cela donne. Une partie plus ou moins couvrante peut être déléguée à des logiciels de tests, permettant d'avoir rapidement une idée de la pertinence de la solution soumise.


<a id="orgeb6355f"></a>

## Comment ?

Automatisation de la préparation, compilation et pourquoi pas d'une partie de l'évaluation.

Cette automatisation ce concrétise par un programme python permettant de faire une grosse partie du travail fastidieux et répétitif nécessaire lors de l'évaluation de TPs/projets.


<a id="org970686a"></a>

# Implémentation


<a id="org37a1c4c"></a>

## Package declaration


<a id="org518782d"></a>

### Fichier de setup

```python
# -*- coding: utf-
from setuptools import setup, find_packages

setup(
    name='fast-eval',
    packages=find_packages(exclude=["examples/*"]),
    version='0.2.5',
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


<a id="orgea6d15e"></a>

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
    parser.add_argument("-ws", "--workspace",
                        help="where to build workspace")
    parser.add_argument("-v", "--verbosity",
                        help="increase output verbosity",
                        type=int, choices=[0, 1, 2], default=0)
    fe = FastEval(parser.parse_args())
```


<a id="org9f10d86"></a>

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

def search_files(name, d='.'):
    return [os.path.join(root, f) for root, _, files in os.walk(d) for f in files if f == name]
def choice_str(choices, target=''):
    res = '. ' + str(target) + '\n' + '│\n'
    for choice in choices[:-1]:
      res = res + '├── ' + str(choice) + '\n'
    res = res + '└── ' + choices[-1]
    return res
```


<a id="org6e6b3b6"></a>

## TODO Class


<a id="org3e155b9"></a>

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
        #self.icolor = fg('medium_turquoise') + attr('bold')
        self.icolor = fg('light_sea_green') + attr('bold')
        self.rcolor = attr('reset')
        if args.workspace:
            self.workspace_path = os.path.abspath(os.path.expanduser(args.workspace))
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print(f'Using  {self.info_str(self.workspace_path)} as workspace. {self.info_str("✓")}')

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print('Given  {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.archive_path)),
                  file=sys.stderr)
            sys.exit()

        self.verbosity = args.verbosity
        config_path = os.path.expanduser(args.config)
        assert os.path.isfile(config_path), "{} is not a file.".format(self.erro_str(config_path))

        with open(config_path, 'r') as fp:
            config = json.load(fp)
        print(f'Loaded {self.info_str(config_path)} savefile. {self.info_str("✓")}')
        self.required_files = config['required_files']

        if len(config['reference_folder']) > 0:
            self.ref_path = os.path.expanduser(config['reference_folder'])
            if not os.path.isdir(self.ref_path):
                print('Given  {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.ref_path)),
                  file=sys.stderr)
                sys.exit()
            print(f'Using  {self.info_str(self.ref_path)} as reference folder. {self.info_str("✓")}')
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
            print('Processing {} projects...\n'.format(len(submissions)))
            self.submissions = {key: dict(value, **{'step' : '0_prep', 'steps': {'0_prep' : {},
                                                                                 '1_comp' : {},
                                                                                 '2_exec' : {},
                                                                                 '3_eval' : {}}}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
            print('\n')
            self.prep_step()
        else:
            print('Processing {} projects...\n'.format(len(self.submissions)))
            self.check_prep()

        self.print_step_errors('0_prep')
        self.exte_step(self.comp_cmd, step='1_comp', label='Compiling')
        self.print_step_errors('1_comp')
        self.exte_step(self.exec_cmd, step='2_exec', label='Executing')
        self.print_step_errors('2_exec')
        self.write_data()

    def load_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        #data = load_json(data_file)
        try:
            with open(data_file, 'r') as fp:
                data = json.load(fp)


            self.pass_count = data['pass_count'] + 1
            self.submissions = data['submissions']
            print(f'Loaded {self.info_str(data_file)} savefile. {self.info_str("✓")}\n')
        except FileNotFoundError:
            print(f'Using  {self.info_str(data_file)} savefile. {self.info_str("✓")}\n')
            self.pass_count = 0
    def write_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        try:
            with open(data_file, 'w') as fp:
                json.dump({'pass_count': self.pass_count,
                           'submissions': self.submissions},
                          fp, sort_keys=True, indent=4, ensure_ascii=False)
            print(f'Wrote  {self.info_str(data_file)} savefile. {self.info_str("✓")}')
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
            for f in files:
                try:
                    shutil.unpack_archive(f, raw_dir)
                    os.remove(f)
                except shutil.ReadError:
                    print('Unpack ' + self.warn_str(f) + ' failed.')

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
                student_code = search_files(f, raw_dir)
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
        if len(to_prep) == 0:
            print(f'           0 fails. {self.info_str("✓")}')
        else:
            print('           ' + self.erro_str('{} fails.'.format(len(to_prep))) + '\n')
    def check_prep(self):
        to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print('Checking   {} projects...'.format(len(to_check)))
        for sub in to_check:
            eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')
            eval_files = [f for root, dirs, files in os.walk(eval_dir) for f in files]


            missing_files = [f for f in self.required_files if f not in eval_files]
            # Update missing files if needed
            if missing_files:
                self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
            else:
                self.submissions[sub]['step'] = '1_comp'

        to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print('           ' + self.erro_str('{} fails.'.format(len(to_check))) + '\n')
    def exte_step(self, cmd, step='1_comp', label='Compiling'):
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        print('{}  {} projects...'.format(label, len(to_exec)))
        root_dir = os.getcwd()
        for sub in to_exec:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            comp_ok = True
            for c in cmd:
                completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
                if completed_process.returncode == 1:
                    comp_ok=False
                cond = [len(completed_process.stderr) > 0, len(completed_process.stdout) > 0]
                if any(cond) and c not in self.submissions[sub]['steps'][step]:
                    self.submissions[sub]['steps'][step][c] = {}
                if cond[0]:
                    self.submissions[sub]['steps'][step][c]['stderr'] = completed_process.stderr.split('\n')
                if cond[1]:
                    self.submissions[sub]['steps'][step][c]['stdout'] = completed_process.stdout.split('\n')
            if comp_ok:
                self.submissions[sub]['step'] = self.next_step(step)
        os.chdir(root_dir)
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        if len(to_exec) == 0:
            print(f'           0 fails. {self.info_str("✓")}')
        else:
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
    def print_step_errors(self, step):
        to_print = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        if self.verbosity >= 1 and len(to_print) > 0:
            print(f"Fail list : {to_print}\n")
        if self.verbosity > 1:
            for s in to_print:
                print(f'{s}\'s errors : \n {self.submissions[s]["steps"][step]}')
        print("\n")


```


<a id="org0fc539e"></a>

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

```python
def print_step_errors(self, step):
    to_print = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    if self.verbosity >= 1 and len(to_print) > 0:
        print(f"Fail list : {to_print}\n")
    if self.verbosity > 1:
        for s in to_print:
            print(f'{s}\'s errors : \n {self.submissions[s]["steps"][step]}')
    print("\n")
```


<a id="org74b6129"></a>

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
        print(f'Loaded {self.info_str(data_file)} savefile. {self.info_str("✓")}\n')
    except FileNotFoundError:
        print(f'Using  {self.info_str(data_file)} savefile. {self.info_str("✓")}\n')
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
        print(f'Wrote  {self.info_str(data_file)} savefile. {self.info_str("✓")}')
    except:
        print('Error while writing : \n => {}\n'.format(data_file),
              file=sys.stderr)

```


<a id="org5148199"></a>

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
        for f in files:
            try:
                shutil.unpack_archive(f, raw_dir)
                os.remove(f)
            except shutil.ReadError:
                print('Unpack ' + self.warn_str(f) + ' failed.')

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
            student_code = search_files(f, raw_dir)
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
    if len(to_prep) == 0:
        print(f'           0 fails. {self.info_str("✓")}')
    else:
        print('           ' + self.erro_str('{} fails.'.format(len(to_prep))) + '\n')
```

```python
def search_files(name, d='.'):
    return [os.path.join(root, f) for root, _, files in os.walk(d) for f in files if f == name]
```

```python
def check_prep(self):
    to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    print('Checking   {} projects...'.format(len(to_check)))
    for sub in to_check:
        eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')
        eval_files = [f for root, dirs, files in os.walk(eval_dir) for f in files]


        missing_files = [f for f in self.required_files if f not in eval_files]
        # Update missing files if needed
        if missing_files:
            self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
        else:
            self.submissions[sub]['step'] = '1_comp'

    to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    print('           ' + self.erro_str('{} fails.'.format(len(to_check))) + '\n')
```


<a id="orgcb2169a"></a>

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
        comp_ok = True
        for c in cmd:
            completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
            if completed_process.returncode == 1:
                comp_ok=False
            cond = [len(completed_process.stderr) > 0, len(completed_process.stdout) > 0]
            if any(cond) and c not in self.submissions[sub]['steps'][step]:
                self.submissions[sub]['steps'][step][c] = {}
            if cond[0]:
                self.submissions[sub]['steps'][step][c]['stderr'] = completed_process.stderr.split('\n')
            if cond[1]:
                self.submissions[sub]['steps'][step][c]['stdout'] = completed_process.stdout.split('\n')
        if comp_ok:
            self.submissions[sub]['step'] = self.next_step(step)
    os.chdir(root_dir)
    to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    if len(to_exec) == 0:
        print(f'           0 fails. {self.info_str("✓")}')
    else:
        print('           ' + self.erro_str('{} fails.'.format(len(to_exec))) + '\n')

```


<a id="orgf7785ae"></a>

# Déploiement vers Pypi

```bash
rm -rf dist/
python setup.py sdist
```

```bash
twine upload dist/*
```


<a id="orgaa1b01d"></a>

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
