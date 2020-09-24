- [Mode d'emploi](#org18b4a26)
  - [Fichier de configuration](#org652f49f)
- [Concept](#orgdb0dc17)
  - [Pourquoi ?](#org67bd7c6)
  - [Comment ?](#org3d8a6a3)
- [Implémentation](#orgc875d87)
  - [Package declaration](#org6681098)
    - [Fichier de setup](#org29cd51f)
  - [Cli](#org819a7fb)
  - [Imports](#org961c561)
  - [Class](#org8b9633d)
    - [Init](#orgacb86f3)
    - [Print Helpers](#orga13d82a)
    - [Extraction helpers](#org1007dda)
    - [Json data files](#org715c537)
    - [Preparation](#org06fae29)
    - [Compilation](#org7e7bf03)
- [Deploiement vers Pypi](#org96516ac)


<a id="org18b4a26"></a>

# TODO Mode d'emploi


<a id="org652f49f"></a>

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


<a id="orgdb0dc17"></a>

# DONE Concept


<a id="org67bd7c6"></a>

## Pourquoi ?

L'objectif de ce projet est de faciliter l'évaluation de TPs d'info. Généralement la procédure d'évaluation est la même :

-   **Récupération:** Je récupère tous les travaux soumis dans une unique archive fournie par Arche. (manuellement pour l'instant, il ne semble pas qu'il y ait d'API arche accessible).

-   **Préparation:** Chaque travail est généralement soumis sous la forme d'une archive, dont l'organisation varie souvent énormément d'un étudiant à l'autre. Cette partie est donc fastidieuse : il faut extraire un à un chaque archive, puis chercher les fichiers réellement utiles (en général un ou plusieurs fichiers source).

-   **Compilation:** Selon le projet et le langage, exécution de make, gcc etc&#x2026; Idem, c'est fastidieux, et facilement scriptable.

-   **Exécution et évaluation:** Faire tourner le programme et voir ce que cela donne. Une partie plus ou moins couvrante peut être déléguée à des logiciels de tests, permettant d'avoir rapidement une idée de la pertinence de la solution soumise.


<a id="org3d8a6a3"></a>

## Comment ?

Automatisation de la préparation, compilation et pourquoi pas d'une partie de l'évaluation.

Cette automatisation ce concrétise par un programme python permettant de faire une grosse partie du travail fastidieux et répétitif nécessaire lors de l'évaluation de TPs/projets.


<a id="orgc875d87"></a>

# Implémentation


<a id="org6681098"></a>

## Package declaration


<a id="org29cd51f"></a>

### Fichier de setup

```python
# -*- coding: utf-
from setuptools import setup, find_packages

setup(
    name='fast-eval',
    packages=find_packages(exclude=["examples/*"]),
    version='0.1.6',
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


<a id="org819a7fb"></a>

## Cli

```python
#!/usr/bin/env python3
import argparse
from fast_eval.util import FastEval
def main():
    print('coucou')
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        help="path of json config file")
    parser.add_argument("archive_path",
                        help="path of archive from arche")
    parser.add_argument("--ws",
                        help="where to build workspace")
    fe = FastEval(parser.parse_args())

```


<a id="org961c561"></a>

## DONE Imports

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

def extract_rm(archive_path, dest='.'):
    shutil.unpack_archive(archive_path, dest)
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
def load_json(file_path):
    try:
        with open(file_path, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        print('No data file found at (Normal if first run):\n => {}'.format(file_path))
    return None
def choice_str(choices, target=''):
    res = '. ' + str(target) + '\n' + '│\n'
    for choice in choices[:-1]:
      res = res + '├── ' + str(choice) + '\n'
    res = res + '└── ' + choices[-1]
    return res
```


<a id="org8b9633d"></a>

## TODO Class


<a id="orgacb86f3"></a>

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
        self.wcolor = bg('orange_1') + fg('white')
        self.icolor = bg('deep_sky_blue_2') + fg('white')
        self.rcolor = attr('reset')

        if args.ws:
            self.workspace_path = os.path.expanduser(args.ws)
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print('Using {} as workspace'.format(self.info_str(self.workspace_path)))

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print('Given {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.archive_path)),
                  file=sys.stderr)
            sys.exit()

        config = os.path.expanduser(args.config)
        assert os.path.isfile(config), "{} is not a file.".format(config)
        self.required_files = ['exo1.c']

        with open(config, 'r') as fp:
            config = json.load(fp)
        self.required_files = config['required_files']

        if len(config['reference_folder']) > 0:
            self.ref_path = os.path.expanduser(config['reference_folder'])
            if not os.path.isdir(self.ref_path):
                print('Given {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.ref_path)),
                  file=sys.stderr)
                sys.exit()
            print('Using {} as reference folder'.format(self.info_str(self.ref_path)))
        else:
            self.ref_path = None
            print('Not using ref folder')

        self.cmd = config['compilation_commands']

        self.submissions = {}
        self.load_data()
        # Si c'est le premier passage, il faut lancer la preparation
        if self.pass_count == 0:
            shutil.unpack_archive(self.archive_path, self.workspace_path)
            submissions = self.clean_dirs()
            self.submissions = {key: dict(value, **{'steps': {'0_prep' : {},
                                                              '1_comp' : {},
                                                              '2_exec' : {},
                                                              '3_eval' : {}}}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
            self.copy_etu()
        #if not self.check_prep():
        #    print('Exiting ...\n', file=sys.stderr)
        #    sys.exit()

        #self.compile()
        #self.execute(self.cmd)
        self.write_data()

    def load_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        data = load_json(data_file)
        if data is None:
            self.pass_count = 0
        else:
            try:
                self.pass_count = data['pass_count'] + 1
                self.submissions = data['submissions']
                print('Datafile Successfully loaded:\n'
                      ' => {}\nCurrent pass : {}\n'.format(data_file, self.pass_count))
            except KeyError:
                print('Invalid data file : \n => {}\n exiting...'.format(data_file))
                sys.exit()

    def write_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        try:
            with open(data_file, 'w') as fp:
                json.dump({'pass_count': self.pass_count,
                           'submissions': self.submissions},
                          fp, sort_keys=True, indent=4)
            print('Wrote ' + self.info_str(data_file))
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
                extract_rm(files[0], raw_dir)
            except shutil.ReadError:
                print(self.warn_str('Warn ') + ' ' + str(files[0]) + ' Impossible to unpack\n')

    def copy_ref(self):
        if self.ref_path is not None:
            for sub in self.submissions:
                shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))

    def copy_etu(self):
        for sub in self.submissions:
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
                    self.submissions[sub]['steps']['0_prep']['status'] = False
                else:
                    self.submissions[sub]['steps']['0_prep']['status'] = False
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
                self.submissions[sub]['steps']['0_prep']['status'] = True
    def check_prep(self):
        to_check = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['prep_ok'] == False}

        for sub in to_check:
            ok = True
            # Il faut vérifier que tous les fichiers sont bien présents.
            files = [o for o in os.listdir(os.path.join(to_check[sub]['path'], 'eval'))]
            for f in self.required_files:
                if f not in files:
                    ok = False
            if ok == True:
                self.submissions[sub]['prep_ok'] = True
        to_check = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['prep_ok'] == False}
        if len(to_check) == 0:
            return True
        else:
            print('\nPlease fix following issue.s'
              ' before starting auto_corrector.py again :\n')
            for c in to_check:
                print(c,'\n', to_check[c]['prep_error'])
            return False
    def compile(self):
        to_comp = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['comp_ok'] == False}
        print('Compiling {} projects...'.format(len(to_comp)))
        root_dir = os.getcwd()
        for sub in to_comp:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            completed_process = subprocess.run(["make"], capture_output=True, text=True)
            if completed_process.returncode == 0:
                self.submissions[sub]['comp_ok'] = True
                self.submissions[sub]['comp_pts'] = self.pass_count < 2
            self.submissions[sub]['comp_error'] = completed_process.stderr
        to_comp = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['comp_ok'] == False}
        print('          {} fails.'.format(len(to_comp)))
        os.chdir(root_dir)
    def execute(self, cmd):
        to_exec = {sub: self.submissions[sub] for sub in self.submissions if( not self.submissions[sub]['exec_ok'] and self.submissions[sub]['comp_ok'])}
        print('Executing {} projects...'.format(len(to_exec)))
        root_dir = os.getcwd()
        for sub in to_exec:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if completed_process.returncode != 0:
                #print(completed_process.returncode, completed_process.stderr)
                self.submissions[sub]['exec_error'] = completed_process.stderr
            else:
                self.submissions[sub]['exec_ok'] = True
                self.submissions[sub]['exec_pts'] = self.pass_count < 2
                mark_line = [i for i in completed_process.stdout.split('\n') if i][-3]
                mark = float([i for i in mark_line.split(' ') if i][-1])
                self.submissions[sub]['mark'] = mark
                #print(mark, mark_line)
        to_exec = {sub: self.submissions[sub] for sub in self.submissions if( not self.submissions[sub]['exec_ok'] and self.submissions[sub]['comp_ok'])}
        print('          {} fails.'.format(len(to_exec)))
        os.chdir(root_dir)
    def erro_str(self, msg):
        return self.ecolor + str(msg) + self.rcolor
    def warn_str(self, msg):
        return self.wcolor + str(msg) + self.rcolor
    def info_str(self, msg):
        return self.icolor + str(msg) + self.rcolor


```


<a id="orga13d82a"></a>

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


<a id="org1007dda"></a>

### Extraction helpers

```python
def extract_rm(archive_path, dest='.'):
    shutil.unpack_archive(archive_path, dest)
```


<a id="org715c537"></a>

### Json data files

```python
def load_json(file_path):
    try:
        with open(file_path, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        print('No data file found at (Normal if first run):\n => {}'.format(file_path))
    return None
```

```python
def load_json(file_path):
    try:
        with open(file_path, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        print('No data file found at (Normal if first run):\n => {}'.format(file_path))
    return None
```

```python
def load_data(self):
    data_file = os.path.join(self.workspace_path, 'data.json')
    data = load_json(data_file)
    if data is None:
        self.pass_count = 0
    else:
        try:
            self.pass_count = data['pass_count'] + 1
            self.submissions = data['submissions']
            print('Datafile Successfully loaded:\n'
                  ' => {}\nCurrent pass : {}\n'.format(data_file, self.pass_count))
        except KeyError:
            print('Invalid data file : \n => {}\n exiting...'.format(data_file))
            sys.exit()

```

```python
def write_data(self):
    data_file = os.path.join(self.workspace_path, 'data.json')
    try:
        with open(data_file, 'w') as fp:
            json.dump({'pass_count': self.pass_count,
                       'submissions': self.submissions},
                      fp, sort_keys=True, indent=4)
        print('Wrote ' + self.info_str(data_file))
    except:
        print('Error while writing : \n => {}\n'.format(data_file),
              file=sys.stderr)

```


<a id="org06fae29"></a>

### Preparation

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
            extract_rm(files[0], raw_dir)
        except shutil.ReadError:
            print(self.warn_str('Warn ') + ' ' + str(files[0]) + ' Impossible to unpack\n')

```

```python
def copy_ref(self):
    if self.ref_path is not None:
        for sub in self.submissions:
            shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))

```

```python
def copy_etu(self):
    for sub in self.submissions:
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
                self.submissions[sub]['steps']['0_prep']['status'] = False
            else:
                self.submissions[sub]['steps']['0_prep']['status'] = False
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
            self.submissions[sub]['steps']['0_prep']['status'] = True
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

```python
def check_prep(self):
    to_check = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['prep_ok'] == False}

    for sub in to_check:
        ok = True
        # Il faut vérifier que tous les fichiers sont bien présents.
        files = [o for o in os.listdir(os.path.join(to_check[sub]['path'], 'eval'))]
        for f in self.required_files:
            if f not in files:
                ok = False
        if ok == True:
            self.submissions[sub]['prep_ok'] = True
    to_check = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['prep_ok'] == False}
    if len(to_check) == 0:
        return True
    else:
        print('\nPlease fix following issue.s'
          ' before starting auto_corrector.py again :\n')
        for c in to_check:
            print(c,'\n', to_check[c]['prep_error'])
        return False
```


<a id="org7e7bf03"></a>

### Compilation

```python
def compile(self):
    to_comp = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['comp_ok'] == False}
    print('Compiling {} projects...'.format(len(to_comp)))
    root_dir = os.getcwd()
    for sub in to_comp:
        os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
        completed_process = subprocess.run(["make"], capture_output=True, text=True)
        if completed_process.returncode == 0:
            self.submissions[sub]['comp_ok'] = True
            self.submissions[sub]['comp_pts'] = self.pass_count < 2
        self.submissions[sub]['comp_error'] = completed_process.stderr
    to_comp = {sub: self.submissions[sub] for sub in self.submissions if self.submissions[sub]['comp_ok'] == False}
    print('          {} fails.'.format(len(to_comp)))
    os.chdir(root_dir)
```

```python
def execute(self, cmd):
    to_exec = {sub: self.submissions[sub] for sub in self.submissions if( not self.submissions[sub]['exec_ok'] and self.submissions[sub]['comp_ok'])}
    print('Executing {} projects...'.format(len(to_exec)))
    root_dir = os.getcwd()
    for sub in to_exec:
        os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
        completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if completed_process.returncode != 0:
            #print(completed_process.returncode, completed_process.stderr)
            self.submissions[sub]['exec_error'] = completed_process.stderr
        else:
            self.submissions[sub]['exec_ok'] = True
            self.submissions[sub]['exec_pts'] = self.pass_count < 2
            mark_line = [i for i in completed_process.stdout.split('\n') if i][-3]
            mark = float([i for i in mark_line.split(' ') if i][-1])
            self.submissions[sub]['mark'] = mark
            #print(mark, mark_line)
    to_exec = {sub: self.submissions[sub] for sub in self.submissions if( not self.submissions[sub]['exec_ok'] and self.submissions[sub]['comp_ok'])}
    print('          {} fails.'.format(len(to_exec)))
    os.chdir(root_dir)
```


<a id="org96516ac"></a>

# Deploiement vers Pypi

```bash
rm -rf dist/
python setup.py sdist
```

```bash
twine upload dist/*
```
