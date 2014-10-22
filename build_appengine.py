#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin, threading

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

    endpointscfg = settings.get('endpointscfg')
    gradle = settings.get('gradle')

    project_path = paths[0] 
    settings.get(project_path)
    if settings.get(project_path) != None:
      project_name = settings.get(project_path).get('project_name')
      api_name = settings.get(project_path).get('api_name')

      os.chdir(project_path)
      os.system(endpointscfg+" get_client_lib java -bs gradle " + project_name + "." + api_name)

      to_dir = "extracted-files"
      for file in glob.glob("*.zip"):
        zip = zipfile.ZipFile(file)
        zip.extractall(to_dir, get_members(zip))
        os.remove(file)

      os.chdir(to_dir)
      os.system(gradle+" install")
      os.chdir("../")
      shutil.rmtree(to_dir)
      sublime.status_message("Build finished!")
    else:
      sublime.error_message("Project \""+project_path+"\" not found in \"AppEngine Build -> user.settings\"")
