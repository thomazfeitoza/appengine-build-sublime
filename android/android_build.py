#coding: utf-8

import os, glob, shutil, sublime, threading, zipfile
from ..helper import run_os_command, get_members


class AppEngineEndpointsBuildAndroid(threading.Thread):

  def __init__(self, project_path, apis, endpointscfg, gradle):
    self.project_path = project_path
    self.apis = apis
    self.endpointscfg = endpointscfg
    self.gradle = gradle
    threading.Thread.__init__(self)

  def run(self):
    self.build()

  def build(self):
    sublime.status_message("Building AppEngine client lib for Android...")
    os.chdir(self.project_path)
    try:
      tmp_dir = self.project_path + '/.tmp'
      android_dir = tmp_dir + '/android'
      run_os_command('rm -Rf ' + android_dir)
      try:
        os.makedirs(android_dir)
      except OSError as e:
        pass

      run_os_command(self.endpointscfg + ' get_client_lib java --output=' + android_dir + '  -bs gradle ' + self.apis)
      for filename in glob.glob(android_dir + "/*.zip"):
        zip = zipfile.ZipFile(filename)
        zip.extractall(android_dir, get_members(zip))

      os.chdir(android_dir)
      run_os_command(self.gradle + ' install')
      run_os_command('rm -Rf ' + android_dir)
        
      sublime.status_message('Android build finished!')

    except Exception as e:
      sublime.error_message('Android build failed:\n' + str(e))

