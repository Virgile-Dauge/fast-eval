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
            print('Processing {} projects...\n'.format(len(submissions)))
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
            print('Processing {} projects...\n'.format(len(self.submissions)))
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
            #files = [os.path.join(raw_dir, o) for o in os.listdir(raw_dir)]
            files = [os.path.join(raw_dir, f) for root, _, files in os.walk(raw_dir) for f in files]
            print(files)
            for f in files:
                try:
                    shutil.unpack_archive(f, raw_dir)
                    #os.remove(f)
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
        if len(to_check) == 0:
            print(f'           0 fails. {self.info_str("✓")}')
        else:
            print('           ' + self.erro_str('{} fails.'.format(len(to_check))) + '\n')
    def exte_step(self, cmd, step='1_comp', label='Compiling', timeout=10):
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        print('{}  {} projects...'.format(label, len(to_exec)))
        root_dir = os.getcwd()
        for sub in to_exec:
            os.chdir(os.path.join(self.submissions[sub]['path'], 'eval'))
            comp_ok = True
            timeout_raised = False
            for c in cmd:
                try:
                    completed_process = subprocess.run([c], capture_output=True, text=True, shell=True, timeout=timeout)
                    if completed_process.returncode != 0:
                        comp_ok=False
                    cond = [len(completed_process.stderr) > 0, len(completed_process.stdout)]
                    if any(cond) and c not in self.submissions[sub]['steps'][step]:
                        self.submissions[sub]['steps'][step][c] = {}
                    if cond[0]:
                        self.submissions[sub]['steps'][step][c]['stderr'] = completed_process.stderr.split('\n')
                    if cond[1]:
                        out = completed_process.stdout.split('\n')
                        if len(out) > 20:
                            out = out[:10] + ['.'] + ['truncated by fast-eval'] + ['.'] + out[-10:]
                        self.submissions[sub]['steps'][step][c]['stdout'] = out
                except Exception as e:
                    comp_ok=False
                    if type(e) is subprocess.TimeoutExpired:
                        self.submissions[sub]['steps'][step][c] = 'timeout'
    
            if comp_ok:
                self.submissions[sub]['step'] = self.next_step(step)
        os.chdir(root_dir)
        to_exec = [sub for sub in self.submissions if self.submissions[sub]['step'] == step]
        if len(to_exec) == 0:
            print(f'           0 fails. {self.info_str("✓")}')
        else:
            print('           ' + self.erro_str('{} fails.'.format(len(to_exec))) + '\n')
    
    def cleanup(self):
        for c in self.cleanup_cmd:
            completed_process = subprocess.run(shlex.split(c))
            if completed_process.returncode == 0:
                print(f'Cleanup : {c} {self.info_str("✓")}')
            else:
                print(f'Cleanup : {c} {self.erro_str("❌")}')
    def export(self):
        outpath = os.path.join(self.workspace_path, 'readme.org')
        with open(outpath, 'w') as f:
            f.write("#+title: Rapport d'évaluation\n")
            for s in self.submissions:
                step = self.submissions[s]['step']
                steps = self.submissions[s]['steps']
                f.write(f'** {s}\n')
    
                # Section erreur prep
                if steps['0_prep']:
                    f.write(f'*** Erreurs de préparation\n')
                    for k, v in steps['0_prep'].items():
                        f.write(f'{k} :\n')
                        for i in v:
                            f.write(f' - {i}\n')
                # Section erreur comp
                if steps['1_comp']:
                    usefull = False
                    for v in steps['1_comp'].values():
                        if 'stderr' in v:
                            usefull = True
                    if usefull:
                        f.write(f'*** Erreurs de compilation\n')
                        for k, v in steps['1_comp'].items():
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
                    f.write(f'*** code\n')
                    for sf in self.required_files:
                        f.write(f'**** {sf}\n')
                        # Détermination du langage
                        l = os.path.splitext(sf)[-1][1:]
                        if l == 'py':
                            l = python
                        if l == 'sh':
                            l = bash
                        # Copie du code de l'étudiant
                        f.write(f'#+begin_src {l}\n')
                        with open(os.path.join(self.submissions[s]['path'], 'eval', sf), 'r') as cf:
                            f.write(cf.read())
                        f.write('\n#+end_src\n')
    
                # Section retour exécution
                if steps['2_exec']:
                    f.write(f"*** Retours d'éxécution\n")
                    for k, v in steps['2_exec'].items():
                        f.write(f'#+begin_src bash\n')
                        f.write(f'{k}\n')
                    f.write('#+end_src\n')
                    if 'stderr' in v:
                        f.write('\n#+name: stderror\n')
                        f.write(f'#+begin_example\n')
                        for line in v['stderr']:
                            f.write(f'{line}\n')
                        f.write('#+end_example\n')
                    if 'stdout' in v:
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
            print(f'Wrote  {self.info_str(outpath)} readable file. {self.info_str("✓")}')
        else:
           print('Error while generating html')
    
    def gen_csv(self):
        outpath = os.path.join(self.workspace_path, 'notes.csv')
        with open(outpath, 'w') as f:
            names = [s for s in self.submissions]
            names.sort()
            print(names)
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
