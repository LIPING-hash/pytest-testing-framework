"""Iterate through configuration files in all folders using the env value"""
class EnvConfig:

    def conf_init(self, file_flag=None):
        # Get passed-in variables
        flag = False
        project_dir = os.getenv('project_dir')
        if project_dir is None:
            project_dir = os.path.split(os.path.realpath(__file__))[0].split('common_tools')[0]
        t = sys.argv
        # Parse command line arguments
        for arg in sys.argv:
            if arg == '--env':
                flag = True
                continue
            if flag:
                # Locate matching config file for the given environment
                file_path = find_matching_files(os.path.join(project_dir, 'conf'), arg)
                with open(file_path, 'r', encoding="utf-8") as f:
                    config_data = yaml.full_load(f)
                # Store the test environment value into envConfig
                config_data["test_env"] = arg
                if file_flag is not None:
                    return file_path
                else:
                    return config_data

        # Fallback: read environment from pytest.ini
        iniPath = os.path.join(project_dir, 'pytest.ini')
        conf = configparser.ConfigParser()
        conf.read(iniPath)
        addopts = conf.get("pytest", "addopts")
        env = addopts.split(' ')[1]
        # Traverse all folders' config files using the env value
        file_path = find_matching_files(os.path.join(project_dir, 'conf'), env)
        if file_path is None:
            logger.error(f"Configuration file for environment [{env}] does not exist!")
        with open(file_path, 'r', encoding="utf-8") as f:
            config_data = yaml.full_load(f)
        # Store the test environment value into envConfig
        config_data["test_env"] = env
        if file_flag is not None:
            return file_path
        else:
            return config_data


envConfig = EnvConfig().conf_init()

if __name__ == '__main__':
    print(EnvConfig().conf_init(file_flag=True))
    print(envConfig)