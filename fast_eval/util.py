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
        self.exte_step(self.comp_cmd, step='1_comp', label='Compiling')
        self.exte_step(self.exec_cmd, step='2_exec', label='Executing')
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
            for c in cmd:
                completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
                if completed_process.returncode == 0:
                    self.submissions[sub]['step'] = self.next_step(step)
                    cond = [len(completed_process.stderr) > 0, len(completed_process.stdout) > 0]
                    if any(cond):
                        self.submissions[sub]['steps'][step][c] = {}
                    if cond[0]:
                        self.submissions[sub]['steps'][step][c]['stderr'] = completed_process.stderr.split('\n')
                    if cond[1]:
                        self.submissions[sub]['steps'][step][c]['stdout'] = completed_process.stdout.split('\n')
    
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
