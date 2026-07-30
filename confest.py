# -*- coding: utf-8 -*-
from common_tools.env_config import envConfig, EnvConfig
from common_tools.mysql_operate import is_mysql_connect

conf_init = envConfig

# Load YAML configuration path
yaml_path = EnvConfig().conf_init(file_flag=True)
user_agent = " "


@pytest.fixture(scope="session")
def login_sess():
    return login_sess_ykj()


@allure_step("[REDACTED]")  # Cloud workspace login
def login_sess_ykj():
    sessionInit = SessionConf()
    global login_sess_init

    # Check if super workbench is enabled
    if 'is_super_work' in list(conf_init.keys()) and conf_init['is_super_work'] is True:
        # Check if this is a new tenant with super workbench enabled
        if 'is_new_super_tenant' in list(conf_init.keys()) and conf_init['is_new_super_tenant'] is True:
            # Execute master data JMX file for current environment
            # [REDACTED]: JMX execution logic removed
            pass

        current_super_key = login_super_work()
        get_info_header = {
            'Authorization': current_super_key,
            'Content-Type': 'application/json',
            'User-Agent': user_agent
        }
        get_info_params = {
            "pageUrl": conf_init['host']['public'] + "/dist/[REDACTED]/[REDACTED]?_smp=[REDACTED]",
            "integratedType": "[REDACTED]", "siteCode": "[REDACTED]", "isIframe": "1"}

        # Get integrated info from super workbench
        info_res = sessionInit.api_post(url=conf_init["host"]["super_work"] + "/workbench/integrated/get-info",
                                        json=get_info_params, headers=get_info_header)
        ykj_direct_url = info_res['result']['integratedUrl']

        # Follow redirects to obtain cloud workspace cookies
        ykj_res = sessionInit.api_get(url=ykj_direct_url, allow_redirects=False, api_type='default')
        direct1 = sessionInit.api_get(url=ykj_res.headers['Location'], allow_redirects=False, api_type='default')
        ykj_manage_res = sessionInit.api_get(
            url=conf_init['host']['public'] + "/[REDACTED]/[REDACTED]/layout/base-info?_smp=[REDACTED]",
            cookies=direct1.cookies, case_name='Get cloud workspace cookies after super workbench login')

        if ykj_manage_res['message'] != "success":
            logger.error(f'Login failed. Please check super workbench domain and username!')
            return

        sessionInit.headers['super_key'] = current_super_key
        login_sess_init = sessionInit
        global_variable.set_value("login_sess", sessionInit)
        return sessionInit

    @pytest.fixture(scope="session")
    @allure_step("Login to APP")
    def login_sess_app():
        # Determine login method based on app type
        if 'is_super_work' in list(conf_init.keys()) and conf_init['is_super_work'] is True:
            return login_sess_app_cyjg()
        if conf_init['app_type'] == '[REDACTED]':  # super_app
            return login_sess_app_cyjg()
        if conf_init['app_type'] == '[REDACTED]':  # smart_ykj
            return login_sess_app_zhkj()
        if conf_init['app_type'] == '[REDACTED]':  # ykj
            return login_sess_merchant()

if __name__ == '__main__':
    login_sess_ykj()
