- [Mode d'emploi](#orga604e44)
  - [Installation](#org41bc9e9)
    - [Optionnal requirements](#org7c7e6bb)
  - [Fichier de configuration](#orga8f6f6f)
  - [Usage](#orgd51cff1)
  - [Etapes de correction](#orgf7c48fd)
  - [know Issues](#orge0df301)
- [Concept](#orgb000046)
  - [Pourquoi ?](#org8620596)
  - [Comment ?](#org114985f)
- [Implémentation](#org2ce5ee5)
  - [Package declaration](#orga7b229d)
    - [Fichier de setup](#orgcf0cd06)
  - [Cli](#org5891085)
  - [Dépendances](#orgbbc1e30)
  - [Class](#org30f596a)
    - [Init](#orge0cbc4b)
    - [Print Helpers](#org584a4aa)
    - [Json data files](#orgf80316f)
    - [Préparation](#org3106702)
    - [Compilation](#orgb440269)
    - [Cleanup](#org06392ee)
    - [Export vers org-mode](#org42f97a8)
    - [org vers html](#org8f88266)
    - [gen csv with names](#org2388478)
- [Déploiement](#org7714fe5)
  - [Vers Pypi](#org3364976)
  - [Github Pages](#org2e0b027)


<a id="orga604e44"></a>

# TODO Mode d'emploi


<a id="org41bc9e9"></a>

## Installation

```bash
pip install fast-eval
```


<a id="org7c7e6bb"></a>

### Optionnal requirements

1.  For HTML export

    Install pandoc

    ```bash
    sudo apt install pandoc
    ```

    Install pandoc theme

    ```bash
    curl 'https://raw.githubusercontent.com/ryangrose/easy-pandoc-templates/master/copy_templates.sh' | bash
    ```


<a id="orga8f6f6f"></a>

## Fichier de configuration

Champs à adapter :

-   **required files:** Fichiers à chercher dans le rendu des étudiants.

-   **reference folder:** Dossier dont le contenu est à copier dans le dossier d'évaluation de chaque rendu. Cela peut être des *headers* nécessaires à la compilation, des programmes de tests etc&#x2026; Chaîne vide si pas besoin de dossier de référence.

-   **comp commands:** Liste de commandes à effectuer lors de l'étape de compilation. Liste vide si rien à faire.

-   **execution commands:** Liste de commandes à effectuer lors de l'étape d'exécution/évaluation. Liste vide si rien à faire.

```json
{
    "required_files": [
        "hello.c",
        "nohello.c"
    ],
    "reference_folder": "./ref",
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


<a id="orgd51cff1"></a>

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


<a id="orgf7c48fd"></a>

## Etapes de correction

1.  Exécuter fast-eval

```bash
fast-eval example/fake.json example/fake.zip -v 2 -ws example/
```

fast-eval a crée l'ensemble des éléments nécessaires à la correction dans le *workspace* passé en argument :

-   Un dossier par étudiant
-   Un fichier de sauvegarde *data.json*
-   Un fichier readme *readme.org* (à ouvrir dans emacs)
-   un fichier readme *readme.html*, plus lisible, contenant l'ensemble des données récoltées ainsi que le code fourni par l'étudiant.

```bash
tree example
```

1.  Régler les soucis de préparation

Ici pas d'erreurs que préparation l'on puisse corriger. Souvent, il s'agit d'un fichier ne respectant pas la convention de nommage imposée par le sujet. il faut donc copier **manuellement** les fichiers incorrectment nommés depuis le dossier *raw* de l'étudiant vers le dossier *eval* de l'étudiant, cette fois ci avec le bon nom.

example :

```bash
mv example/Dupond\ Vide/raw/nom_incorrect.c example/Dupond\ Vide/eval/nom_correct.c
```

1.  Exécuter fast-eval

```bash
fast-eval example/fake.json example/fake.zip -v 2 -ws example/
```

1.  Consulter le rapport généré pour correction

```bash
firefox example/readme.html
```


<a id="orge0df301"></a>

## know Issues

Some Zip files unzip failed, idk why.

-   zip files not marked with .zip
-   other zip files


<a id="orgb000046"></a>

# Concept


<a id="org8620596"></a>

## Pourquoi ?

L'objectif de ce projet est de faciliter l'évaluation de TPs d'info. Généralement la procédure d'évaluation est la même :

-   **Récupération:** Je récupère tous les travaux soumis dans une unique archive fournie par Arche. (manuellement pour l'instant, il ne semble pas qu'il y ait d'API arche accessible).

-   **Préparation:** Chaque travail est généralement soumis sous la forme d'une archive, dont l'organisation varie souvent énormément d'un étudiant à l'autre. Cette partie est donc fastidieuse : il faut extraire un à un chaque archive, puis chercher les fichiers réellement utiles (en général un ou plusieurs fichiers source).

-   **Compilation:** Selon le projet et le langage, exécution de make, gcc etc&#x2026; Idem, c'est fastidieux, et facilement scriptable.

-   **Exécution et évaluation:** Faire tourner le programme et voir ce que cela donne. Une partie plus ou moins couvrante peut être déléguée à des logiciels de tests, permettant d'avoir rapidement une idée de la pertinence de la solution soumise.


<a id="org114985f"></a>

## Comment ?

Automatisation de la préparation, compilation et pourquoi pas d'une partie de l'évaluation.

Cette automatisation ce concrétise par un programme python permettant de faire une grosse partie du travail fastidieux et répétitif nécessaire lors de l'évaluation de TPs/projets.


<a id="org2ce5ee5"></a>

# Implémentation


<a id="orga7b229d"></a>

## Package declaration


<a id="orgcf0cd06"></a>

### Fichier de setup

```python
# -*- coding: utf-
from setuptools import setup, find_packages

setup(
    name='fast-eval',
    packages=find_packages(exclude=["examples/*"]),
    version='1.0.1',
    description='Simple tool to provide automation to assessment processes.',
    author=u'Virgile Daugé',
    author_email='virgile.dauge@pm.me',
    url='https://github.com/Virgile-Dauge/fast-eval',
    # download_url='',
    keywords=['assessment', 'evaluation'],
    install_requires=['rich'],
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


<a id="org5891085"></a>

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


<a id="orgbbc1e30"></a>

## Dépendances

```python
# Pour lecture de dossiers/fichiers
import os
import sys
import csv
import json
import shlex
# Pour affichage de dict
import pprint
# Pour décomprésser
import shutil
# Pour Exécution de programmes
import subprocess

import re

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

#from rich import pretty
from rich import print
# Helpers

def search_files(name, d='.'):
    return [os.path.join(root, re.fullmatch(name, f).group()) for root, _, files in os.walk(d) for f in files if re.fullmatch(name, f)]

from rich import pretty
pretty.install()
```


<a id="org30f596a"></a>

## TODO Class


<a id="orge0cbc4b"></a>

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
        self.console = Console()
        if args.workspace:
            self.workspace_path = os.path.abspath(os.path.expanduser(args.workspace))
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print(f'Using  {self.workspace_path} as workspace. ✓')

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print(f'Given  {self.archive_path}'
                  ' does not exist, exiting...', file=sys.stderr)
            sys.exit()

        self.verbosity = args.verbosity
        config_path = os.path.expanduser(args.config)
        assert os.path.isfile(config_path), f'{config_path} is not a file.'

        with open(config_path, 'r') as fp:
            config = json.load(fp)
        print(f'Loaded {config_path} config file. ✓')

        if 'required_files' in config:
            self.required_files = config['required_files']
        else:
            self.required_files = []

        if 'reference_folder' in config and len(config['reference_folder']) > 0:
            self.ref_path = os.path.expanduser(config['reference_folder'])
            if not os.path.isdir(self.ref_path):
                print(f'Given  {self.ref_path}'
                  ' does not exist, exiting...', file=sys.stderr)
                sys.exit()
            print(f'Using  {self.ref_path} as reference folder. ✓')
        else:
            self.ref_path = None
            print('Not using ref folder')

        if 'compilation_commands' in config:
            self.comp_cmd = config['compilation_commands']
        else:
            self.comp_cmd = []
        if 'execution_commands' in config:
            self.exec_cmd = config['execution_commands']
        else:
            self.exec_cmd = []
        if 'cleanup' in config:
            self.cleanup_cmd = config['cleanup']
        else:
            self.cleanup_cmd = []
        if 'export_to_html' in config:
            self.export_to_html = config['export_to_html']
        else:
            self.export_to_html = True

        self.submissions = {}
        # Chargement de la config
        self.load_data()
        # Si c'est le premier passage, il faut lancer la preparation
        if self.pass_count == 0:
            shutil.unpack_archive(self.archive_path, self.workspace_path)
            submissions = self.clean_dirs()
            print(f'Processing {len(submissions)} projects...\n')
            self.submissions = {key: dict(value, **{'step' : '0_prep', 'steps': {'0_prep' : {},
                                                                                 '1_comp' : {},
                                                                                 '2_exec' : {},
                                                                                 '3_eval' : {}}}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
            print('\n')
            self.prep_step()
            self.gen_csv()
        else:
            print(f'Processing {len(self.submissions)} projects...\n')
            self.check_prep()

        self.print_step_errors('0_prep')
        self.write_data()
        self.exte_step(self.comp_cmd, step='1_comp', label='Compiling')
        self.print_step_errors('1_comp')
        self.write_data()
        self.exte_step(self.exec_cmd, step='2_exec', label='Executing')
        self.cleanup()
        self.print_step_errors('2_exec')
        self.write_data()
        self.export()

    def load_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        #data = load_json(data_file)
        try:
            with open(data_file, 'r') as fp:
                data = json.load(fp)


            self.pass_count = data['pass_count'] + 1
            self.submissions = data['submissions']
            print(f'Loaded {data_file} savefile. ✓\n')
        except FileNotFoundError:
            print(f'Using  {data_file} savefile. ✓\n')
            self.pass_count = 0
    def write_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        try:
            with open(data_file, 'w') as fp:
                json.dump({'pass_count': self.pass_count,
                           'submissions': self.submissions},
                          fp, sort_keys=True, indent=4, ensure_ascii=False)
            print(f'Wrote  {data_file} savefile. ✓')
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
            files = [os.path.join(raw_dir, f) for root, _, files in os.walk(raw_dir) for f in files]
            for f in files:
                try:
                    shutil.unpack_archive(f, raw_dir)
                    #os.remove(f)
                except shutil.ReadError:
                    print(f'Unpack {f} failed.')

    def copy_ref(self):
        if self.ref_path is not None:
            for sub in self.submissions:
                shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))

    def prep_step(self):
        to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print(f'Preparing  {len(to_prep)} projects...')
        with Progress(transient=True) as progress:
            task = progress.add_task(f'Preparing...', total=len(to_prep))
            for sub in to_prep:
                raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
                eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')

                if not os.path.exists(eval_dir):
                    os.mkdir(eval_dir)

                missing_files = []
                self.submissions[sub]['files'] = {}
                # Search every required files one by one
                for f in self.required_files:
                    # List cadidates for searched file
                    student_code = search_files(f, raw_dir)
                    # Filter files in a "__MACOS" directory
                    student_code = [s for s in student_code if '__MACOS' not in s]
                    self.submissions[sub]['files'][f] = student_code
                    if len(student_code) == 1:
                        shutil.copyfile(student_code[0], os.path.join(eval_dir, os.path.basename(student_code[0])))
                    elif len(student_code) == 0:
                        missing_files.append(f)
                    else:
                        missing_files.append(f)
                        msg = 'You need to manually copy one of those files: \n'
                        for candidate in student_code:
                            msg = msg + ' - ' + candidate + '\n'
                        self.submissions[sub]['steps']['0_prep']['msg'] = msg

                # Update missing files if needed
                if missing_files:
                    if 'missing_files' not in self.submissions[sub]['steps']['0_prep']:
                        self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
                    else:
                        self.submissions[sub]['steps']['0_prep']['missing_files'].extend(missing_files)
                else:
                    self.submissions[sub]['step'] = '1_comp'
                progress.update(task, advance=1)

        to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        if len(to_prep) == 0:
            print(f' 0 fails. ✓')
        else:
            print(f' {len(to_prep)} fails.\n')
    def check_prep(self):
        to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
        print(f'Checking   {len(to_check)} projects...')
        with Progress(transient=True) as progress:
            task = progress.add_task(f'Checking...', total=len(to_check))
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
                progress.update(task, advance=1)
        if len(to_check) == 0:
            print(f' 0 fails. ✓')
        else:
            print(f' {len(to_check)} fails.\n')

    def format_output(self, out, max_lines=400):
        if len(out) > max_lines:
            return out[:max_lines//2] + ['<'] + ['truncated by fast-eval'] + ['>'] + out[-max_lines//2:]
        return out

    def exte_step(self, cmd, step='1_comp', label='Compiling', timeout=10):
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        print(f'{label}  {len(to_exec)} projects...')
        if not cmd:
            print('Nothing to do.')
            for sub in to_exec:
                self.submissions[sub]['step'] = self.next_step(self.submissions[sub]['step'])
            return None
        root_dir = os.getcwd()
        with Progress(transient=True) as progress:
            task = progress.add_task(f"[bold]{label}...", total=len(to_exec))
            for sub in to_exec:
                os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
                comp_ok = True
                timeout_raised = False
                for c in cmd:
                    try:
                        completed_process = subprocess.run([c], capture_output=True, text=True, shell=True, timeout=timeout)
                        if completed_process.returncode != 0:
                            comp_ok=False
                        cond = [len(completed_process.stderr) > 0, len(completed_process.stdout) > 0]
                        if any(cond) and c not in self.submissions[sub]['steps'][step]:
                            self.submissions[sub]['steps'][step][c] = {}
                        if cond[0]:
                            self.submissions[sub]['steps'][step][c]['stderr'] = self.format_output(
                                completed_process.stderr.split('\n'))
                        if cond[1]:
                            out = completed_process.stdout.split('\n')
                            self.submissions[sub]['steps'][step][c]['stdout'] = self.format_output(
                                completed_process.stdout.split('\n'))

                    except Exception as e:
                        comp_ok=False
                        if type(e) is subprocess.TimeoutExpired:
                            self.submissions[sub]['steps'][step][c] = 'timeout'

                if comp_ok:
                    self.submissions[sub]['step'] = self.next_step(step)
                progress.update(task, advance=1)
        os.chdir(root_dir)
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        if len(to_exec) == 0:
            print(f' 0 fails. ✓')
        else:
            print(f' {len(to_exec)} fails.\n')

    def cleanup(self):
        for c in self.cleanup_cmd:
            completed_process = subprocess.run(shlex.split(c))
            if completed_process.returncode == 0:
                print(f'Cleanup : {c} ✓')
            else:
                print(f'Cleanup : {c} ❌')
    def export(self):
        outpath = os.path.join(self.workspace_path, 'readme.org')
        with open(outpath, 'w') as f:
            f.write("#+title: Rapport d'évaluation\n")
            f.write('#+OPTIONS: ^:nil p:nil\n')
            for s in sorted(self.submissions):
                step = self.submissions[s]['step']
                steps = self.submissions[s]['steps']
                f.write(f'* {s}\n')

                # Section erreur prep
                if steps['0_prep']:
                    f.write(f'** Erreurs de préparation\n')
                    for k, v in steps['0_prep'].items():
                        f.write(f'{k} :\n')
                        f.write(f'{v}\n')
                # Section erreur comp
                if steps['1_comp']:
                    usefull = False
                    for v in steps['1_comp'].values():
                        if 'stderr' in v and v['stderr'] and len(v['stderr'][0])>0:
                            usefull = True
                    if usefull:
                        f.write(f'** Erreurs de compilation\n')
                        for k, v in steps['1_comp'].items():
                            f.write(f'*** {k}\n')
                            f.write(f'#+begin_src bash\n')
                            f.write(f'{k}\n')
                            f.write('#+end_src\n')

                            f.write('\n#+name: stderror\n')
                            f.write(f'#+begin_example\n')
                            for line in v['stderr']:
                                f.write(f'{line}\n')
                            f.write('\n#+end_example\n')

                # Section avec code rendu
                if step != '0_prep':
                    f.write(f'** code\n')
                    for src in self.submissions[s]['files'].values():
                        src = src[0]
                    #for sf in self.required_files:
                        name = os.path.basename(src)
                        f.write(f'*** {name}\n')
                        # Détermination du langage
                        l = os.path.splitext(name)[-1]
                        if l == '.py':
                            l = 'python'
                        if l == '.sh' or l == '.bash':
                            l = 'bash'
                        if l == '.c':
                            l = 'c'
                        # Copie du code de l'étudiant
                        f.write(f'#+name: {name}\n')
                        f.write(f'#+begin_src {l}\n')
                        with open(src, 'r') as cf:
                            f.write(cf.read())
                        f.write('\n#+end_src\n')

                # Section retour exécution
                if steps['2_exec']:
                    f.write(f"** Retours d'éxécution\n")
                    for k, v in steps['2_exec'].items():
                        f.write(f'*** {k}\n')
                        f.write(f'#+begin_src bash\n')
                        f.write(f'{k}\n')
                        f.write('#+end_src\n')
                        if 'stderr' in v:
                            f.write('\nstderror\n')
                            f.write('\n#+name: stderror\n')
                            f.write(f'#+begin_example\n')
                            for line in v['stderr']:
                                f.write(f'{line}\n')
                            f.write('#+end_example\n')
                        if 'stdout' in v:
                            f.write('\nstdout\n')
                            f.write('\n#+name: stdout\n')
                            f.write(f'#+begin_example\n')
                            for line in v['stdout']:
                                f.write(f'{line}\n')
                            f.write('#+end_example\n')
        if self.export_to_html:
            self.gen_html()
    def gen_html(self, orgfile='readme.org', style='tango'):
        inpath = os.path.join(self.workspace_path, 'readme.org')
        outpath = os.path.join(self.workspace_path, 'readme.html')
        cmd = shlex.split(f'pandoc -s {inpath} -o {outpath} --highlight-style {style} --template=easy_template.html --standalone --toc')
        completed_process = subprocess.run(cmd)
        if completed_process.returncode == 0:
            print(f'Wrote  {outpath} readable file. ✓')
        else:
           print('Error while generating html')

    def gen_csv(self):
        outpath = os.path.join(self.workspace_path, 'notes.csv')
        with open(outpath, 'w') as f:
            names = [s for s in self.submissions]
            names.sort()
            for n in names:
                f.write(f'{n}, note\n')
    def next_step(self, step):
        if step == '0_prep':
            return '1_comp'
        elif step == '1_comp':
            return '2_exec'
        elif step == '2_exec':
            return '3_eval'
        else:
            return 'done'
    def print_step_errors(self, step):
        to_print = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        if self.verbosity >= 1 and len(to_print) > 0:
            print(f"Fail list : {to_print}\n")
        if self.verbosity > 1:
            for s in to_print:
                #msg = f'{s}\'s errors : \n {self.submissions[s]["steps"][step]}'
                #self.console.print(f'{s}\'s errors :', self.submissions[s]["steps"][step])
                #self.console.print(msg)
                self.console.rule(f'{s}\'s errors :')
                self.console.print(self.submissions[s]['steps'][step]['msg'])
                #self.console.print(Panel.fit(str(self.submissions[s]['steps'][step]), title=f'[red]{s}\'s errors :'))
                #if len(self.submissions[s]["steps"][step]) > 0 and len(msg) < 1000:
                #    print(msg)
        print("\n")


```


<a id="org584a4aa"></a>

### Print Helpers

```python
def print_step_errors(self, step):
    to_print = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    if self.verbosity >= 1 and len(to_print) > 0:
        print(f"Fail list : {to_print}\n")
    if self.verbosity > 1:
        for s in to_print:
            #msg = f'{s}\'s errors : \n {self.submissions[s]["steps"][step]}'
            #self.console.print(f'{s}\'s errors :', self.submissions[s]["steps"][step])
            #self.console.print(msg)
            self.console.rule(f'{s}\'s errors :')
            self.console.print(self.submissions[s]['steps'][step]['msg'])
            #self.console.print(Panel.fit(str(self.submissions[s]['steps'][step]), title=f'[red]{s}\'s errors :'))
            #if len(self.submissions[s]["steps"][step]) > 0 and len(msg) < 1000:
            #    print(msg)
    print("\n")
```


<a id="orgf80316f"></a>

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
        print(f'Loaded {data_file} savefile. ✓\n')
    except FileNotFoundError:
        print(f'Using  {data_file} savefile. ✓\n')
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
        print(f'Wrote  {data_file} savefile. ✓')
    except:
        print('Error while writing : \n => {}\n'.format(data_file),
              file=sys.stderr)

```


<a id="org3106702"></a>

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
        files = [os.path.join(raw_dir, f) for root, _, files in os.walk(raw_dir) for f in files]
        for f in files:
            try:
                shutil.unpack_archive(f, raw_dir)
                #os.remove(f)
            except shutil.ReadError:
                print(f'Unpack {f} failed.')

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
    print(f'Preparing  {len(to_prep)} projects...')
    with Progress(transient=True) as progress:
        task = progress.add_task(f'Preparing...', total=len(to_prep))
        for sub in to_prep:
            raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
            eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')

            if not os.path.exists(eval_dir):
                os.mkdir(eval_dir)

            missing_files = []
            self.submissions[sub]['files'] = {}
            # Search every required files one by one
            for f in self.required_files:
                # List cadidates for searched file
                student_code = search_files(f, raw_dir)
                # Filter files in a "__MACOS" directory
                student_code = [s for s in student_code if '__MACOS' not in s]
                self.submissions[sub]['files'][f] = student_code
                if len(student_code) == 1:
                    shutil.copyfile(student_code[0], os.path.join(eval_dir, os.path.basename(student_code[0])))
                elif len(student_code) == 0:
                    missing_files.append(f)
                else:
                    missing_files.append(f)
                    msg = 'You need to manually copy one of those files: \n'
                    for candidate in student_code:
                        msg = msg + ' - ' + candidate + '\n'
                    self.submissions[sub]['steps']['0_prep']['msg'] = msg

            # Update missing files if needed
            if missing_files:
                if 'missing_files' not in self.submissions[sub]['steps']['0_prep']:
                    self.submissions[sub]['steps']['0_prep']['missing_files'] = missing_files
                else:
                    self.submissions[sub]['steps']['0_prep']['missing_files'].extend(missing_files)
            else:
                self.submissions[sub]['step'] = '1_comp'
            progress.update(task, advance=1)

    to_prep = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    if len(to_prep) == 0:
        print(f' 0 fails. ✓')
    else:
        print(f' {len(to_prep)} fails.\n')
```

```python
def search_files(name, d='.'):
    return [os.path.join(root, re.fullmatch(name, f).group()) for root, _, files in os.walk(d) for f in files if re.fullmatch(name, f)]
```

```python
def check_prep(self):
    to_check = [sub for sub in self.submissions if self.submissions[sub]['step'] == '0_prep']
    print(f'Checking   {len(to_check)} projects...')
    with Progress(transient=True) as progress:
        task = progress.add_task(f'Checking...', total=len(to_check))
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
            progress.update(task, advance=1)
    if len(to_check) == 0:
        print(f' 0 fails. ✓')
    else:
        print(f' {len(to_check)} fails.\n')
```


<a id="orgb440269"></a>

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

def format_output(self, out, max_lines=400):
    if len(out) > max_lines:
        return out[:max_lines//2] + ['<'] + ['truncated by fast-eval'] + ['>'] + out[-max_lines//2:]
    return out

def exte_step(self, cmd, step='1_comp', label='Compiling', timeout=10):
    to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    print(f'{label}  {len(to_exec)} projects...')
    if not cmd:
        print('Nothing to do.')
        for sub in to_exec:
            self.submissions[sub]['step'] = self.next_step(self.submissions[sub]['step'])
        return None
    root_dir = os.getcwd()
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[bold]{label}...", total=len(to_exec))
        for sub in to_exec:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            comp_ok = True
            timeout_raised = False
            for c in cmd:
                try:
                    completed_process = subprocess.run([c], capture_output=True, text=True, shell=True, timeout=timeout)
                    if completed_process.returncode != 0:
                        comp_ok=False
                    cond = [len(completed_process.stderr) > 0, len(completed_process.stdout) > 0]
                    if any(cond) and c not in self.submissions[sub]['steps'][step]:
                        self.submissions[sub]['steps'][step][c] = {}
                    if cond[0]:
                        self.submissions[sub]['steps'][step][c]['stderr'] = self.format_output(
                            completed_process.stderr.split('\n'))
                    if cond[1]:
                        out = completed_process.stdout.split('\n')
                        self.submissions[sub]['steps'][step][c]['stdout'] = self.format_output(
                            completed_process.stdout.split('\n'))

                except Exception as e:
                    comp_ok=False
                    if type(e) is subprocess.TimeoutExpired:
                        self.submissions[sub]['steps'][step][c] = 'timeout'

            if comp_ok:
                self.submissions[sub]['step'] = self.next_step(step)
            progress.update(task, advance=1)
    os.chdir(root_dir)
    to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
    if len(to_exec) == 0:
        print(f' 0 fails. ✓')
    else:
        print(f' {len(to_exec)} fails.\n')

```


<a id="org06392ee"></a>

### Cleanup

```python
def cleanup(self):
    for c in self.cleanup_cmd:
        completed_process = subprocess.run(shlex.split(c))
        if completed_process.returncode == 0:
            print(f'Cleanup : {c} ✓')
        else:
            print(f'Cleanup : {c} ❌')
```


<a id="org42f97a8"></a>

### Export vers org-mode

```python
def export(self):
    outpath = os.path.join(self.workspace_path, 'readme.org')
    with open(outpath, 'w') as f:
        f.write("#+title: Rapport d'évaluation\n")
        f.write('#+OPTIONS: ^:nil p:nil\n')
        for s in sorted(self.submissions):
            step = self.submissions[s]['step']
            steps = self.submissions[s]['steps']
            f.write(f'* {s}\n')

            # Section erreur prep
            if steps['0_prep']:
                f.write(f'** Erreurs de préparation\n')
                for k, v in steps['0_prep'].items():
                    f.write(f'{k} :\n')
                    f.write(f'{v}\n')
            # Section erreur comp
            if steps['1_comp']:
                usefull = False
                for v in steps['1_comp'].values():
                    if 'stderr' in v and v['stderr'] and len(v['stderr'][0])>0:
                        usefull = True
                if usefull:
                    f.write(f'** Erreurs de compilation\n')
                    for k, v in steps['1_comp'].items():
                        f.write(f'*** {k}\n')
                        f.write(f'#+begin_src bash\n')
                        f.write(f'{k}\n')
                        f.write('#+end_src\n')

                        f.write('\n#+name: stderror\n')
                        f.write(f'#+begin_example\n')
                        for line in v['stderr']:
                            f.write(f'{line}\n')
                        f.write('\n#+end_example\n')

            # Section avec code rendu
            if step != '0_prep':
                f.write(f'** code\n')
                for src in self.submissions[s]['files'].values():
                    src = src[0]
                #for sf in self.required_files:
                    name = os.path.basename(src)
                    f.write(f'*** {name}\n')
                    # Détermination du langage
                    l = os.path.splitext(name)[-1]
                    if l == '.py':
                        l = 'python'
                    if l == '.sh' or l == '.bash':
                        l = 'bash'
                    if l == '.c':
                        l = 'c'
                    # Copie du code de l'étudiant
                    f.write(f'#+name: {name}\n')
                    f.write(f'#+begin_src {l}\n')
                    with open(src, 'r') as cf:
                        f.write(cf.read())
                    f.write('\n#+end_src\n')

            # Section retour exécution
            if steps['2_exec']:
                f.write(f"** Retours d'éxécution\n")
                for k, v in steps['2_exec'].items():
                    f.write(f'*** {k}\n')
                    f.write(f'#+begin_src bash\n')
                    f.write(f'{k}\n')
                    f.write('#+end_src\n')
                    if 'stderr' in v:
                        f.write('\nstderror\n')
                        f.write('\n#+name: stderror\n')
                        f.write(f'#+begin_example\n')
                        for line in v['stderr']:
                            f.write(f'{line}\n')
                        f.write('#+end_example\n')
                    if 'stdout' in v:
                        f.write('\nstdout\n')
                        f.write('\n#+name: stdout\n')
                        f.write(f'#+begin_example\n')
                        for line in v['stdout']:
                            f.write(f'{line}\n')
                        f.write('#+end_example\n')
    if self.export_to_html:
        self.gen_html()
```


<a id="org8f88266"></a>

### org vers html

```python
def gen_html(self, orgfile='readme.org', style='tango'):
    inpath = os.path.join(self.workspace_path, 'readme.org')
    outpath = os.path.join(self.workspace_path, 'readme.html')
    cmd = shlex.split(f'pandoc -s {inpath} -o {outpath} --highlight-style {style} --template=easy_template.html --standalone --toc')
    completed_process = subprocess.run(cmd)
    if completed_process.returncode == 0:
        print(f'Wrote  {outpath} readable file. ✓')
    else:
       print('Error while generating html')

```


<a id="org2388478"></a>

### gen csv with names

```python
def gen_csv(self):
    outpath = os.path.join(self.workspace_path, 'notes.csv')
    with open(outpath, 'w') as f:
        names = [s for s in self.submissions]
        names.sort()
        for n in names:
            f.write(f'{n}, note\n')
```


<a id="org7714fe5"></a>

# Déploiement


<a id="org3364976"></a>

## Vers Pypi

```bash
rm -rf dist/
python setup.py sdist
```

```bash
twine upload dist/*
```


<a id="org2e0b027"></a>

## Github Pages

```bash
mkdir docs
```

```yaml
theme: jekyll-theme-architect
```

```bash
cp readme.md docs/index.md
```
