# Pour lecture de dossiers/fichiers
import os
import sys
import csv
import json
# Pour affichage de dict
import pprint
# Pour décomprésser
import shutil
# Pour les options du script
import argparse
# Pour Exécution de programmes
import subprocess

# Helpers

def extract(archive_path, dest='.'):
    try:
        shutil.unpack_archive(archive_path, dest)
        return True
    except:
        print("Unexpected error while unpacking:",archive_path, '\n' , sys.exc_info()[0])
        return False

def extract_rm(archive_path, dest='.'):
    if(extract(archive_path, dest)):
        os.remove(archive_path)

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
def write_json(data, file_path):
    try:
        with open(file_path, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
    except:
        print('Error while writing : \n => {}\n'.format(file_path),
              file=sys.stderr)

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
def write_csv(data, file_path):
    try:
        with open('coucou.csv', 'w') as f:
            csvwriter = csv.writer(f)
            for d in data:
                csvwriter.writerow(d)
    except:
        print('Error while writing : \n => {}\n'.format(file_path),
              file=sys.stderr)

class FastEval:
    """
    @brief Simple tool to provide automation to assessment processes.
    @details Provide tools to build, compile and evaluatue a suitable
    workspace with a specific working folder for each submitted
    project from a single compressed archive.

    """
    def __init__(self, args):
        "docstring"

        if args.workspace_path:
            self.workspace_path = os.path.expanduser(args.workspace_path)
        else:
            self.workspace_path = os.path.join(os.getcwd(), 'submissions')
        print('Using {} as workspace'.format(self.workspace_path))

        if args.ref_path:
            self.ref_path = os.path.expanduser(args.ref_path)
            print('Using {} as ref'.format(self.ref_path))
        else:
            self.ref_path = None
            print('Not using ref folder')


        #TODO
        self.required_files = ['exo1.c']

        if args.cmd:
            self.cmd = args.cmd
        else:
            self.cmd = ["./promo-test"]

        self.archive_path = os.path.expanduser(args.archive_path)
        if not os.path.exists(self.archive_path):
            print('Given path : {}'
                  ' does not exist, exiting...'.format(self.archive_path),
                  file=sys.stderr)
            sys.exit()


        self.submissions = {}
        self.load_data()
        # Si c'est le premier passage, il faut lancer la preparation
        if self.pass_count == 0:
            extract(self.archive_path, self.workspace_path)
            submissions = self.clean_dirs()
            self.submissions = {key: dict(value, **{'prep_ok': True,
                                                    'comp_ok': False,
                                                    'exec_ok': False}) for key, value in submissions.items()}
            self.extract_dirs()
            self.copy_ref()
            self.copy_etu()
            self.write_data()
        if not self.check_prep():
            print('Exiting ...\n', file=sys.stderr)
            sys.exit()

        self.compile()
        self.execute(self.cmd)
        self.gen_stats()
        self.write_data()
        self.save_csv()

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
        write_json({'pass_count': self.pass_count, 'submissions': self.submissions}, data_file)
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
            extract_rm(files[0], raw_dir)
    
    def copy_ref(self):
        if self.ref_path is not None:
            for sub in self.submissions:
                shutil.copytree(self.ref_path, os.path.join(self.submissions[sub]['path'], 'eval'))
    
    def copy_etu(self):
        for sub in self.submissions:
            raw_dir = os.path.join(self.submissions[sub]['path'], 'raw')
            eval_dir = os.path.join(self.submissions[sub]['path'], 'eval')
            for f in self.required_files:
                student_code = search_files(raw_dir, f)
                if len(student_code) == 1:
                    shutil.copyfile(student_code[0], os.path.join(eval_dir, f))
    
                else:
                    self.submissions[sub]['prep_ok'] = False
                    msg = 'You need to manually copy one of those files'
                    msg = msg + choice_str(student_code, f)
                    #for code in student_code:
                    #    msg = msg + ' └── {}\n'.format(code)
                    self.submissions[sub]['prep_error'] = msg
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
    
    def save_csv(self, file_path='notes.csv'):
        try:
            with open(file_path, 'w') as f:
                csvwriter = csv.writer(f)
                for d in self.submissions:
                    if 'mark_with_bonuses' in self.submissions[d]:
                        csvwriter.writerow([d, self.submissions[d]['mark_with_bonuses']])
                    else:
                        csvwriter.writerow([d])
        except:
            print('Error while writing : \n => {}\n'.format(file_path),
                  file=sys.stderr)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("archive_path",
                      help="path of archive from arche")
  parser.add_argument("--workspace_path",
                      help="where to build workspace")
  parser.add_argument("--ref_path",
                      help="where to pick reference files")
  parser.add_argument("--cmd",
                      help="which cmd to execute to test")
  parser.add_argument("--cfg",
                      help="path of json config file")
  fe = FastEval(parser.parse_args())
