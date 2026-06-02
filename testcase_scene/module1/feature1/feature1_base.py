class TestContractTemplateBase:
    # Retrieve applicable projects (organization tree)
    def get_organization_tree(self, login_sess):
        params = {"filter_no_auth_company": "[REDACTED]", "is_company_select": "[REDACTED]", "_csrf": ""}
        resp = login_sess.api_get(url='[REDACTED]/[REDACTED]/get-organization-tree', params=params, caseName="Get applicable projects")
        return resp

    # Create a new contract template
    def contract_template_create(self, login_sess, name):
        # Load template data from JSON file
        params_info = JsonFileReader("contract_template_new.json", currentDir=currentDir).get()
        params_info = json.dumps(params_info)
        params_info = params_info.replace("${name}", name)
        params_info = json.loads(params_info)

        # Initialize lessor (rental party) information from API
        lessors = login_sess.api_get(
            url='[REDACTED]/[REDACTED]/list?t=1650426281872&_smp=[REDACTED]&page=1&page_size=10')
        params_info['lessors'][0]['lessor_id'] = lessors['data']['items'][0]['id']
        params_info['lessors'][0]['lessor_name'] = lessors['data']['items'][0]['name']

        # Submit request to create contract template
        resp = login_sess.api_post(url="[REDACTED]/[REDACTED]/template/create", json=params_info,
                                   caseName="Create template")
        return resp

    # Query contract template list by name and return search results
    def contract_template_list(self, login_sess, name):
        params = {"keyword": name, "project_ids": [], "page": 1, "page_size": 10}
        resp = login_sess.api_post(url='[REDACTED]/[REDACTED]/template/list', json=params,
                                   caseName="Query contract template")
        return resp