#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin

class AppEngineBuildCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    settings = sublime.load_settings('AppEngineBuild.sublime-settings')

    project_path = settings.get('project_path')
    project_name = settings.get('project_name')
    # project_name_camelized = ''.join([item.capitalize() for item in project_name.split("_")])
    api_name = settings.get('api_name')

    os.chdir(project_path)
    os.system("endpointscfg.py get_client_lib java -bs gradle " + project_name + "." + api_name)

    to_dir = "extracted-files"
    for file in glob.glob("*.zip"):
      zip = zipfile.ZipFile(file)
      zip.extractall(to_dir)
      os.remove(file)

    folder = os.listdir(os.getcwd() + "/" + to_dir)[0]
    os.chdir(to_dir + "/" + folder)
    os.system("gradle install")
    os.chdir("../../")
    shutil.rmtree(to_dir)
    sublime.status_message("Build finished!")
