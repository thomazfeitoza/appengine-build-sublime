#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin

class AppEngineBuildCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    sublime.status_message("Initializing...")

    settings = sublime.load_settings('AppengineBuild/AppengineBuild.sublime-settings')

    project_path = settings.get('project_path')
    project_name = settings.get('project_name')
    project_name_camelized = project_name.split("_").each {|s| s.capitalize! }.join("")

    os.chdir(project_path)

    sublime.status_message("Compiling project...")
    os.system("endpointscfg.py get_client_lib java -bs gradle " + project_name + "." + project_name_camelized)

    sublime.status_message("Extracting files...")
    to_dir = "extracted-files"
    for file in glob.glob("*.zip"):
      zip = zipfile.ZipFile(file)
      zip.extractall(to_dir)
      os.remove(file)

    folder = os.listdir(os.getcwd() + "/" + to_dir)[0]
    os.chdir(to_dir + "/" + folder)
    sublime.status_message("Running gradle install...")
    os.system("gradle install")
    sublime.status_message("Removing tmp files...")
    os.chdir("../../")
    shutil.rmtree(to_dir)
    sublime.status_message("Done!")
