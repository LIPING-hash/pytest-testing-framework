def run_test(test_env=None, markers=None, keyword=None, case_path=None, gen_report=True, send_mail=False,
             user_list: list = None, send_weixin_message=False, weixin_group=None, webhook_url=None, open_report=True,
             remark=None, cmd=True, thread_count=None, report_time=None, collect_api=False):
    global global_test_env
    global_test_env = test_env
    if report_time is None or len(str(report_time)) == 0:
        report_time = datetime.now().strftime("%Y%m%d%H%M%S")

    # Data cleanup
    delete_temp_data()
    delete_report(2)

    env_list = test_env.split(",")
    # Command line execution is required for multi-tenant parallel execution
    cmd = True if len(env_list) > 1 else cmd

    # Set multi-tenant thread count to prevent exceptions from excessive total threads
    if len(env_list) > 1 and thread_count is None:
        thread_count = round(psutil.cpu_count() * 1.2 / len(env_list))

    threads = []
    for env in env_list:
        thread = threading.Thread(target=local_run, args=(
            env.strip(), markers, keyword, case_path, gen_report, send_mail, user_list, send_weixin_message,
            weixin_group, webhook_url, open_report, remark, cmd, thread_count, report_time, collect_api))
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()

def multithreading_run(test_env, test_args, testcase_path, test_keyword, test_markers, test_allure, cmd, thread_count):
    """Enable multi-threaded test execution

    :param test_env: Test environment
    :param test_args: Parameters for main function execution
    :param testcase_path: Test case execution path
    :param test_keyword: Keyword filter
    :param test_markers: Test case markers/tags
    :param test_allure: Allure path parameters
    :param cmd: True/False
    :param thread_count: Number of threads to create
    :return:
    """
    # Add all discovered test case files to the queue
    testcase_queue = Queue()
    for case_path in testcase_path.split(","):
        test_path = case_path.strip()
        if os.path.isdir(test_path):
            for path, dir_list, file_list in os.walk(test_path):
                for file in file_list:
                    if str(file).startswith("test_") and str(file).endswith(".py"):
                        testcase_queue.put(os.path.join(path, file))
        else:
            testcase_queue.put(test_path)

    # Start multi-threaded execution
    cpu_count = psutil.cpu_count()
    print(f"Multi-threaded execution mode enabled. CPU core count: {cpu_count}")
    if thread_count is None or thread_count == "":
        test_thread_count = min(cpu_count, testcase_queue.qsize())
    else:
        test_thread_count = min(int(thread_count), testcase_queue.qsize())
    print(f"Thread count set to: {test_thread_count}")

    threads = []
    for t in range(test_thread_count):
        thread = threading.Thread(target=run, args=(
            testcase_queue, test_args, test_env, test_keyword, test_markers, test_allure, cmd, t + 1,))
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()

def upload_allure_report(report_path):
    """
    Upload Allure test report to OSS
    :param report_path: Allure test report path
    :return:
    """
    if not os.path.exists(report_path):
        logger.error(f"Test report directory does not exist. Please check: {report_path}")
        return
    if len(os.listdir(report_path)) == 0:
        logger.error(f"Test report directory is empty. Please check: {report_path}")
        return

    ini_path = os.path.join(project_path, 'pytest.ini')
    conf = configparser.ConfigParser()
    conf.read(ini_path)
    try:
        print("Uploading test report!!!".center(60, '='))
        # Get OSS configuration
        accessKeyId = conf.get("config", "access_key_id")
        accessKeySecret = conf.get("config", "access_key_secret")
        region = conf.get("config", "region")
        bucket = conf.get("config", "bucket")

        # Remote storage path
        remote_path = os.path.join("[REDACTED]", "auto-exec-api", "report", datetime.now().strftime("%Y%m%d%H%M%S"))
        auth = oss2.Auth(accessKeyId, accessKeySecret)
        bucket = oss2.Bucket(auth, region, bucket)

        # Upload report files
        for path, dir_list, file_list in os.walk(report_path):
            for file in file_list:
                file_path = os.path.join(path, file)
                key_path = remote_path + str(file_path).split(root_report_path)[-1]
                file_path = file_path.replace("\\", "/")
                key_path = key_path.replace("\\", "/")
                resp = bucket.put_object_from_file(key_path, file_path)
                # Assert OSS upload succeeded
                assert resp.status == 200

        remote_report_path = "https://[REDACTED]/" + \
                             os.path.join(remote_path, os.path.basename(report_path)).replace("\\", "/") + "/index.html"
        print(f"====== Test report upload completed. Access URL: {remote_report_path}")
        return remote_report_path
    except Exception as e:
        logger.error(f"Exception occurred while uploading test report to OSS server using OSS SDK. Error: {e}")

def send_qyweixin_message(group=None, webhook_url=None, content: str = ""):
    """Send WeChat Work message

    :param webhook_url: WeChat Work bot webhook URL
    :param group: WeChat Work group bot key. Default group: [REDACTED]
    :param content: Message content
    :return:
    """
    if group is not None and len(group) > 0:
        group_list = str(group).split(",")
        for group_name in group_list:
            key = weixin_group.get(group_name)
            if key is None:
                logger.error_without_fail(f"WeChat Work group [{group_name}] has no configuration. Please add it to the weixin_group dictionary!")
            else:
                send_message(key=key, content=content, group_name=group_name)

    if webhook_url is not None and len(webhook_url) > 0:
        webhook_url_list = str(webhook_url).split(",")
        for webhook in webhook_url_list:
            try:
                webhook_url_key = webhook.split('key=')[-1]
                send_message(key=webhook_url_key, content=content, group_name=webhook)
            except Exception as err:
                logger.error_without_fail(f"Failed to extract webhook_url_key. Please verify webhook_url is correct [{webhook}]: {err}")

def rental_run():
    run_test(
        test_env="[REDACTED]",  # e.g., prod_gbnuat
        case_path="testcase_scene/testcase_v2",
        keyword="bvt",
        weixin_group="[REDACTED]",  # e.g., API 100% coverage achieved - Rental
        remark="[REDACTED]",  # e.g., Gansu Urban Investment New Project
        send_mail=False, send_weixin_message=True, open_report=False, cmd=False  # When cmd=True, reads environment info from pytest.ini
    )

if __name__ == '__main__':
    rental_run()
