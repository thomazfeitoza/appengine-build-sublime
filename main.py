#coding: utf-8

import sublime, sublime_plugin, pprint
from .helper import is_osx, get_apis_as_string
from .ios import ios_build


class AppEngineEndpointsBuildAllCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True, ios=True)
    build_thread.start()

  def is_visible(self, paths = []):
    return False


class AppEngineEndpointsBuildAndroidCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    build_thread = AppEngineEndpointsBuildThread(paths=paths, android=True)
    build_thread.start()

  def is_visible(self, paths = []):
    return False


class AppEngineEndpointsBuildIosCommand(sublime_plugin.WindowCommand):
  def run(self, paths = []):
    settings = sublime.load_settings('AppEngineBuild.sublime-settings')
    dst_path = settings.get(paths[0]).get('options').get('ios').get('build_output')
    apis = get_apis_as_string(settings.get(paths[0]).get('apis'))
    endpointscfg = settings.get('tools').get('endpointscfg')
    service_generator = settings.get('tools').get('service_generator')
    remove_sources_file = settings.get(paths[0]).get('options').get('ios').get('remove_sources_file')
    generate_swift_bridge = settings.get(paths[0]).get('options').get('ios').get('generate_swift_bridge')
    build_as_framework = settings.get(paths[0]).get('options').get('ios').get('build_as_framework')

    build_thread = ios_build.AppEngineEndpointsBuildIos(
      project_path=paths[0],
      dst_path=dst_path,
      apis=apis,
      endpointscfg=endpointscfg,
      service_generator=service_generator,
      remove_sources_file=remove_sources_file,
      generate_swift_bridge=generate_swift_bridge,
      build_as_framework=build_as_framework
      )
    build_thread.start()

  def is_visible(self, paths = []):
    return is_osx()