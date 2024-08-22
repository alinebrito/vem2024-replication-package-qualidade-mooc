import sys
import subprocess
import os
import shutil
import requests
import re
from unidecode import unidecode

def run(cmd):
   call = ["/bin/bash", "-c", cmd]
   ret = subprocess.call(call, stdout=None, stderr=None)
   if ret > 0:
      print("Warning - result was %d" % ret)

def get_report_base_file_name():
    dir_path = "/opt/sonarqube/extensions/report"
    res = []
    for file in os.listdir(dir_path):
        if file.endswith('.md'):
            res.append(file)
    return res[0].split(".md")[0]


def createProject(project_name):
    url = 'http:/localhost:9000/api/projects/create'
    params = {'name': project_name,
             'organization': '',
             'project': unidecode(project_name).replace(' ', '-').replace(',', '')
             }
    
    response = requests.post(url,  params)
    if response.status_code == 200:
        print(response.text)
        return unidecode(project_name).replace(' ', '-').replace(',', '')
    else:
        print(response.text)
        exit()

def get_reports(project_key2):

    folder = '/home/Documents/Cursos/Projetos Extraídos/Alura/Javascript'
    projects_folder_name = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
    for index, project in enumerate(projects_folder_name):
        try: 
            print(unidecode(project).replace(' ', '-'))
            project_key = createProject(project)
            print(project_key)

            os.chdir('/home/Documents/Cursos/Projetos Extraídos/Alura/Javascript/' + project)
            # Create sonar-project.properties to exclude some extensions
            run('echo sonar.exclusions=**/*.html, **/*.css, **/*.xml, */*.scss,  **/*min.js > sonar-project.properties')
            run("sonar-scanner \
            -Dsonar.projectKey=" + project_key + "\
            -Dsonar.sources=. \
            -Dsonar.host.url=http:/localhost:9000 \
            -Dsonar.login=squ_e86d05925281e9f3a94dfb64264b6c827039d71b")

            #Create Folder
            directory = project_key
            parent_dir = "/home/Documents/Cursos/reports/Alura/Javascript"
            new_path = os.path.join(parent_dir, directory)
            os.mkdir(new_path)
            print("Directory '% s' created" % directory)

            # Run report status
            os.chdir('/opt/sonarqube/extensions/report')
            run("java -jar sonar-cnes-report.jar -p" + project_key)

            # Get generate files
            report_file_name = get_report_base_file_name()
            analysis_extensions = ['.md','.docx']
            issue_extensions = ['.csv','.xlsx']
            for extension in analysis_extensions:     
                shutil.move('/opt/sonarqube/extensions/report/' + report_file_name + extension, new_path + '/' + report_file_name + extension)
            for extension in issue_extensions:     
                shutil.move('/opt/sonarqube/extensions/report/' + report_file_name.replace("analysis", "issues") + extension, new_path + '/' + report_file_name.replace("analysis", "issues") + extension)

            print("")
            print("")
            print(project + '-> ANALISADO E SALVO COM SUCESSO!')
            print("")
            print("")
            projects_folder_name.remove(index)
        except Exception as e:
            print(e)
        
    print('\n Cursos que faltaram análise: ')
    for index, project in projects_folder_name:
        print(str(index) + ')' + project)
if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
