#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin

def get_members(zip):
    parts = []
    for name in zip.namelist():
        if not name.endswith('/'):
            parts.append(name.split('/')[:-1])
    prefix = os.path.commonprefix(parts) or ''
    if prefix:
        prefix = '/'.join(prefix) + '/'
    offset = len(prefix)
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        if len(name) > offset:
            zipinfo.filename = name[offset:]
            yield zipinfo

class AppEngineBuildCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    settings = sublime.load_settings('AppEngineBuild.sublime-settings')

    project_path = settings.get('project_path')
    project_name = settings.get('project_name')
    
    api_name = settings.get('api_name')

    os.chdir(project_path)
    
    sublime.status_message("Starting endpoints creation...")
    os.system("endpointscfg.py get_client_lib java -bs gradle " + project_name + "." + api_name)
    sublime.status_message("Endpoints generated with success!")

    to_dir = "extracted-files"

    sublime.status_message("Extracting endpoints zip file...")
    for file in glob.glob("*.zip"):
      zip = zipfile.ZipFile(file)
      zip.zip.extractall(to_dir, get_members(zip))
      os.remove(file)

    sublime.status_message("Endpoints extraction success!")
    
    os.chdir(to_dir)

    sublime.status_message("Updating maven local repository...")
    os.system("gradle install")
    sublime.status_message("MAven local reposity updated with success!")

    os.chdir("../")
    shutil.rmtree(to_dir)
    sublime.status_message("Build finished!")
