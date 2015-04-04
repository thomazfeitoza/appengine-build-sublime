#coding: utf-8

import re, platform, subprocess

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

def get_apis_as_string(apis_setting):
    return ' '.join(api.get('module') + '.' + api.get('class') for api in apis_setting)