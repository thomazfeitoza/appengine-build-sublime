#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin

class AppEngineBuildCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    sublime.status_message("Initializing...")
    sublime.status_message("Compiling project...")
    os.system("endpointscfg.py get_client_lib java -bs gradle hubhug_api.HubhugApi")

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
