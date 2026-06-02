import os
import random
import allure
import pytest
from feature1_base import TestContractTemplateBase
from common_tools.tools.jsonFileReader import JsonFileReader

currentDir = os.path.dirname(os.path.realpath(__file__))
base = TestContractTemplateBase()

@allure.feature("Contract Template")  # Contract Template
class TestContractTemplate:

    @allure.story("Create new contract template")  # Create new contract template
    def test_contract_template_create(self, login_sess):
        global template_id, create_name
        # Generate a unique name with random suffix
        create_name = 'test' + str(random.randint(1, 10000000000))
        resp = base.contract_template_create(login_sess, name=create_name)

        # Verify API request succeeded
        assert resp["message"] == "ok"
        template_id = resp['data']['id']

        # Verify the contract template appears in the list query
        find_resp = base.contract_template_list(login_sess, create_name)
        assert find_resp["data"]["data_list"][0]["name"] == create_name