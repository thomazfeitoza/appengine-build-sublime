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