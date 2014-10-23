#coding: utf-8

import sys, os, glob, zipfile, shutil
import sublime, sublime_plugin, threading, re, platform, subprocess

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

def is_osx():
  return re.search(r'darwin', platform.system(), re.I) != None

def run_os_command(cmd):
  exit_code = subprocess.call(cmd, shell=True)
  if exit_code > 0:
    raise Exception("The command '" + cmd + "' has been terminated with exit code " + str(exit_code))


class AppEngineEndpointsBuildAllCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True, ios=True)
    build_thread.start()

  def is_visible(self, paths = []):
    return is_osx()


class AppEngineEndpointsBuildAndroidCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True)
    build_thread.start()


class AppEngineEndpointsBuildIosCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, ios=True)
    build_thread.start()

  def is_visible(self, paths = []):
    return is_osx()



class AppEngineEndpointsBuildThread(threading.Thread):

  def __init__(self, paths=[], android=False, ios=False):
    self.paths = paths
    self.android = android
    self.ios = ios
    self.settings = sublime.load_settings('AppEngineBuild.sublime-settings')
    threading.Thread.__init__(self)

  def run(self):
    project_path = self.paths[0]

    if self.settings.get(project_path) != None:
      if(self.android):
        self.buildAndroid()
      if(self.ios):
        self.buildIOS()
    else:
      sublime.error_message("Project \""+project_path+"\" not found in \"AppEngine Build -> user.settings\"")


  def buildAndroid(self):
    endpointscfg = self.settings.get('tools').get('endpointscfg')
    gradle = self.settings.get('tools').get('gradle')
    project_path = self.paths[0]

    sublime.status_message("Building AppEngine client lib for Android...")

    apis = self.settings.get(project_path).get('apis')
    apis_str = ' '.join(api.get('module') + '.' + api.get('class') for api in apis)

    os.chdir(project_path)

    try:
      run_os_command(endpointscfg+" get_client_lib java -bs gradle " + apis_str)

      to_dir = "extracted-files"
      for file in glob.glob("*.zip"):
        zip = zipfile.ZipFile(file)
        zip.extractall(to_dir, get_members(zip))
        os.remove(file)

      os.chdir(to_dir)
      run_os_command(gradle+" install")
        
      os.chdir("../")
      shutil.rmtree(to_dir)
      sublime.status_message("Android build finished!")

    except Exception as e:
      sublime.error_message("Android build failed:\n" + str(e))


  def buildIOS(self):
    sublime.status_message("iOS Build finished!")
