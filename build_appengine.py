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
    apis = self.getApisAsString()

    sublime.status_message("Building AppEngine client lib for Android...")

    os.chdir(project_path)

    try:
      run_os_command(endpointscfg+" get_client_lib java -bs gradle " + apis)

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
    endpointscfg = self.settings.get('tools').get('endpointscfg')
    service_generator = self.settings.get('tools').get('service_generator')
    ios_build_options = self.settings.get(self.paths[0]).get('options').get('ios')
    project_path = self.paths[0]
    apis = self.getApisAsString()
    to_dir = ios_build_options.get('build_output')

    sublime.status_message('Building AppEngine client lib for iOS...')

    try:
      os.chdir(project_path)
      try:
        shutil.rmtree(to_dir)
      except Exception:
        pass
      run_os_command(endpointscfg + ' get_discovery_doc --format=rpc --output=./ ' + apis)
      discovery_doc = glob.glob('*.discovery')[0]
      run_os_command(service_generator + ' --output=' + to_dir + ' ' + discovery_doc)

      for file in glob.glob('*.discovery'):
        os.remove(file)

      if(ios_build_options.get('remove_sources_file')):
        for f in glob.glob(to_dir + '/*Sources.m'):
          os.remove(f)

      if(ios_build_options.get('generate_swift_bridge')):
        os.chdir(to_dir)
        bridge_contents = '// To use your API with Swift you need go into your project on XCode,\n// open Build Settings tab and search for "bridging header".\n// Under the option Objective-C Bridging Header add the following line:\n// {YOUR_PROJECT_NAME}/GTLBridge.h\n\n'
        for file in glob.glob('*.h'):
          bridge_contents += '#import "' + file + '"\n'
        bridge_file = open('GTLBridge.h', 'w')
        bridge_file.write(bridge_contents)
        bridge_file.close()

      sublime.status_message('iOS Build finished!')

    except Exception as e:
      sublime.error_message('iOS build failed:\n' + str(e))


  def getApisAsString(self):
    apis = self.settings.get(self.paths[0]).get('apis')
    return ' '.join(api.get('module') + '.' + api.get('class') for api in apis)

