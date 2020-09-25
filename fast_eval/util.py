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
        self.ecolor = fg('indian_red_1a')
        #self.wcolor = bg('orange_1') + fg('white')
        self.wcolor = fg('orange_1')
        self.icolor = bg('deep_sky_blue_2') + fg('white')
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
        self.required_files = ['exo1.c']

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

        self.cmd = config['compilation_commands']

        self.submissions = {}
        # Chargement de la config
        self.load_data()
        # Si c'est le premier passage, il faut lancer la preparation
        if self.pass_count == 0:
            shutil.unpack_archive(self.archive_path, self.workspace_path)
            submissions = self.clean_dirs()
            self.submissions = {key: dict(value, **{'step' : '0_prep', 'steps': {'0_prep' : {},
                                                                                 '1_comp' : {},
                                                                                 '2_exec' : {},
                                                                                 '3_eval' : {}}}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
            #self.copy_etu()
        #if not self.check_prep():
        #    print('Exiting ...\n', file=sys.stderr)
        #    sys.exit()

        #self.compile()
        #self.execute(self.cmd)
        self.prep_step()
        self.comp_step()
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
                print('Loaded ' + self.info_str(data_file) + ' savefile.\n')
            except KeyError:
                print('Invalid ' + self.erro_str(data_file) + 'exiting...\n')
                sys.exit()
    
    def write_data(self):
        data_file = os.path.join(self.workspace_path, 'data.json')
        try:
            with open(data_file, 'w') as fp:
                json.dump({'pass_count': self.pass_count,
                           'submissions': self.submissions},
                          fp, sort_keys=True, indent=4)
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
    def comp_step(self):
        to_comp = [sub for sub in self.submissions if self.submissions[sub]['step'] == '1_comp']
        print('Compiling {} projects...'.format(len(to_comp)))
        root_dir = os.getcwd()
        for sub in to_comp:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            for c in self.cmd:
                completed_process = subprocess.run([c], capture_output=True, text=True, shell=True)
                if completed_process.returncode == 0:
                    self.submissions[sub]['step'] = '2_exec'
                    if len(completed_process.stderr) > 0:
                        self.submissions[sub]['steps']['1_comp'][c] = completed_process.stderr
        to_comp = [sub for sub in self.submissions if self.submissions[sub]['step'] == '1_comp']
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
