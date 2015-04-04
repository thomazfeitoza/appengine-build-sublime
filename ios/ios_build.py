#coding: utf-8

import os, glob, shutil, sublime, threading
from ..helper import run_os_command


class AppEngineEndpointsBuildIos(threading.Thread):

  def __init__(self, project_path, dst_path, apis, endpointscfg, service_generator, remove_sources_file=True, generate_swift_bridge=False, build_as_framework=True):
    self.project_path = project_path
    self.dst_path = dst_path
    self.apis = apis
    self.endpointscfg = endpointscfg
    self.service_generator = service_generator
    self.remove_sources_file = remove_sources_file
    self.generate_swift_bridge = generate_swift_bridge
    self.build_as_framework = build_as_framework
    threading.Thread.__init__(self)

  def run(self):
    self.build()
    
  def build(self):
    sublime.status_message('Building AppEngine client lib for iOS...')

    build_tools_dir = os.path.dirname(__file__).replace(' ', '\ ')
    tmp_dir = self.project_path + '/.tmp'
    ios_dir = tmp_dir + '/ios'
    generated_dir = ios_dir + '/Generated'

    try:
      # Remove old and create new temp directories
      run_os_command('rm -Rf ' + ios_dir)
      try:
        os.makedirs(generated_dir)
      except OSError as e:
        pass

      # Create discovery doc and generate endpoints files from it
      os.chdir(self.project_path)
      run_os_command(self.endpointscfg + ' get_discovery_doc --format=rpc --output=' + ios_dir + ' ' + self.apis)
      discovery_doc = glob.glob(ios_dir + '/*.discovery')[0]
      run_os_command(self.service_generator + ' --output=' + generated_dir + ' ' + discovery_doc)

      # Removes sources file
      if(self.remove_sources_file):
        for f in glob.glob('./ios/.tmp/Generated/*Sources.m'):
          os.remove(f)

      # Create a swift bridge header file
      if(self.generate_swift_bridge):
        bridge_contents = '// To use your API with Swift you need go into your project on XCode,\n// open Build Settings tab and search for "bridging header".\n// Under the option Objective-C Bridging Header add the following line:\n// $(PROJECT_NAME)/GTLBridge.h\n\n'
        for filename in glob.glob(generated_dir + '/*.h'):
          bridge_contents += '#import "' + file + '"\n'
        bridge_file = open(generated_dir + '/GTLBridge.h', 'w')
        bridge_file.write(bridge_contents)
        bridge_file.close()

      # Package the endpoints in a framework or leave as it is
      if(self.build_as_framework):
        run_os_command('cp -R ' + build_tools_dir + '/framework ' + ios_dir)
        run_os_command('cp -R ' + generated_dir + ' ' + ios_dir + '/framework/AppengineEndpoints/')
        os.chdir(ios_dir + '/framework')
        for filename in glob.glob('AppengineEndpoints/Generated/*'):
          run_os_command(build_tools_dir + '/XcodeProjAdder -XCP AppengineEndpoints.xcodeproj -SCSV "' + filename + '"')
        run_os_command('xcodebuild -project AppengineEndpoints.xcodeproj -scheme Framework -sdk iphoneos -configuration release build')
        run_os_command('rm -Rf ' + self.dst_path + '/AppengineEndpoints.framework')
        run_os_command('ditto AppengineEndpoints.framework ' + self.dst_path + '/AppengineEndpoints.framework')
      else:
        run_os_command('cp -R ' + generated_dir + '/* ' + self.dst_path)

      # Clean temp dir
      run_os_command('rm -Rf ' + ios_dir)

      sublime.status_message('iOS Build finished!')

    except Exception as e:
      sublime.error_message('iOS build failed:\n' + str(e))
