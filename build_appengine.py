#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin, threading, re, platform

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


class AppEngineEndpointsBuildAllCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True, ios=True)
    build_thread.start()

  def is_enabled(self, paths = []):
    return True


class AppEngineEndpointsBuildAndroidCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True)
    build_thread.start()

  def is_enabled(self, paths = []):
    return True


class AppEngineEndpointsBuildIosCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, ios=True)
    build_thread.start()

  def is_enabled(self, paths = []):
    match = re.search(r'darwin', platform.system(), re.I)
    return match != None



class AppEngineEndpointsBuildThread(threading.Thread):

  def __init__(self, paths=[], android=False, ios=False):
    self.paths = paths
    self.android = android
    self.ios = ios
    threading.Thread.__init__(self)

  def run(self):
    if(self.android):
      self.buildAndroid()

    if(self.ios):
      self.buildIOS()


  def buildAndroid(self):
    settings = sublime.load_settings('AppEngineBuild.sublime-settings')

    endpointscfg = settings.get('tools').get('endpointscfg')
    gradle = settings.get('tools').get('gradle')

    project_path = self.paths[0] 
    settings.get(project_path)
    if settings.get(project_path) != None:

      apis = settings.get(project_path).get('apis')
      apis_str = ' '.join(api.get('module') + '.' + api.get('class') for api in apis)

      os.chdir(project_path)
      os.system(endpointscfg+" get_client_lib java -bs gradle " + apis_str)

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


  def buildIOS(self):
    sublime.status_message("iOS Build finished!")
