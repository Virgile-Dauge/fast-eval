- [Implémentation](#org87f0c79)
  - [Package declaration](#orge79a200)
    - [Fichier de setup](#org8b7f928)
  - [Cli](#org8f74640)
  - [Dépendances](#org4bf35e4)
  - [Class](#org7cc0731)
    - [Init](#orgd0ce1bf)
    - [Print Helpers](#orgd67ab08)
    - [Json data files](#org3b7bce3)
    - [Préparation](#orgf18ee69)
    - [Compilation](#org90ecbe0)


<a id="org87f0c79"></a>

# Implémentation


<a id="orge79a200"></a>

## Package declaration


<a id="org8b7f928"></a>

### Fichier de setup

```python
# -*- coding: utf-
from setuptools import setup, find_packages

setup(
    name='fast-eval',
    packages=find_packages(exclude=["examples/*"]),
    version='0.2.3',
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


<a id="org8f74640"></a>

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
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    fe = FastEval(parser.parse_args())
```


<a id="org4bf35e4"></a>

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


<a id="org7cc0731"></a>

## TODO Class


<a id="orgd0ce1bf"></a>

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
            self.workspace_path = os.path.abspath(os.path.expanduser(args.ws))
            #self.workspace_path = os.path.expanduser(args.ws)
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print(f'Using  {self.info_str(self.workspace_path)} as workspace.')

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print('Given  {}'
                  ' does not exist, exiting...'.format(self.erro_str(self.archive_path)),
                  file=sys.stderr)
            sys.exit()

        config_path = os.path.expanduser(args.config)
        assert os.path.isfile(config_path), "{} is not a file.".format(self.erro_str(config_path))

        with open(config_path, 'r') as fp:
            config = json.load(fp)
        print('Loaded ' + self.info_str(config_path) + ' savefile.')
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
        #pprint.pprint(self.submissions)
        self.exte_step(self.comp_cmd, step='1_comp', label='Compiling')
        #pprint.pprint(self.submissions)
        self.exte_step(self.exec_cmd, step='2_exec', label='Executing')
        #pprint.pprint(self.submissions)
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
                print(student_code)
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


<a id="orgd67ab08"></a>

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
def print_prep(self):
    to_print = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
```


<a id="org3b7bce3"></a>

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


<a id="orgf18ee69"></a>

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
            print(student_code)
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


<a id="org90ecbe0"></a>

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
    print('           ' + self.erro_str('{} fails.'.format(len(to_exec))) + '\n')

```
