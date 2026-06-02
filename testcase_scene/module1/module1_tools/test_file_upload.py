from common_tools.file_upload import TestContractFileBase


import os
import hashlib
import math
import pytest
import jsonpath
import allure
import sys
from importlib import reload

base = TestContractFileBase()
newContract = PreContract()
bath_path = os.path.dirname(os.path.realpath(__file__))

@pytest.mark.middleware
@allure.feature("File Service 2.0")
class TestContractFile:
    @allure.story("Get file service token")
    def test_get_file_service_token(self, login_sess):
        global token
        res = base.get_file_service_token(login_sess)
        token = res["data"]["token"]
        assert res["message"] == "ok"

    @allure.story("Initialize file upload, get batch_id")
    def test_initiate_upload(self):
        global batch_id, file_path, file_name, file_md5, file_size, file_ext
        file_name = "[REDACTED]"  # e.g., picture.png
        file_path = bath_path + "/data" + "/" + file_name
        file_size = os.path.getsize(file_path)
        file_ext = file_path.split(".")[1]

        # Calculate MD5 hash of the file
        reload(sys)
        with open(file_path, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()

        # Initialize multipart upload and retrieve batch_id
        initiate_res = base.initiate_multipart_upload(token, file_name, file_size, file_md5)
        batch_id = initiate_res["data"]["batch_id"]
        assert initiate_res["code"] == 0
        assert initiate_res["message"] == "ok"

    @allure.story("Upload file chunks")
    def test_upload_file(self, login_sess):
        chunk_size = 1024 * 1024 * 5
        # Get total file size
        total_size = os.path.getsize(file_path)
        # Initial chunk number
        current_chunk = 1
        # Calculate total number of chunks
        total_chunk = math.ceil(total_size / chunk_size)

        # Upload chunks in a loop for large files
        while current_chunk <= total_chunk:
            # Set start position of the current chunk
            start = (current_chunk - 1) * chunk_size
            # Set end position of the current chunk
            end = min(total_size, start + chunk_size)

            # Instantiate MD5 hash object for the chunk
            m = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Seek to the start position
                f.seek(start)
                # Read chunk data
                file_chunk_data = f.read(end - start)
                m.update(file_chunk_data)
                # Get MD5 hash of the chunk
                file_slice_md5 = m.hexdigest()

            # Upload current chunk
            part_number = current_chunk
            file_byte = file_chunk_data
            res = base.upload_part(token, batch_id, part_number, file_slice_md5, file_byte)
            assert res["code"] == 0
            assert res["message"] == "ok"
            assert res["data"]["part_number"] == part_number
            assert res["data"]["part_md5"] == file_slice_md5

            current_chunk = current_chunk + 1

    @allure.story("Verify file integrity and get file info after upload")
    def test_complite_multipart_upload(self):
        global file_id, upload_time
        # After all chunks are uploaded, complete the upload and verify file integrity
        res = base.complete_multipart_upload(batch_id, token)
        file_id = res["data"]["file_id"]
        upload_time = res["data"]["last_updated_time"]
        assert res["code"] == 0
        assert res["message"] == "ok"
        assert res["data"]["file_name"] == file_name
        assert res["data"]["file_md5"] == file_md5
        assert res["data"]["file_size"] == str(file_size)
        assert res["data"]["file_ext"] == file_ext

    @allure.story("Upload file to contract")
    def test_contract_detail_edit(self, login_sess):
        global contract_id
        # Create a contract and upload the file to it
        contract = newContract.create_to_audit_contract(login_sess, room_num=1, pricing_unit_num=1, draft_file="[REDACTED]", params=None, resource_id=None, resource_name=None, rent_time=None)
        contract_id = contract["contract_id"]
        res = base.contract_detail_edit(login_sess, contract_id, file_name=file_name, file_id=file_id,
                                        upload_time=upload_time, file_size=file_size, file_ext=file_ext)
        assert res["code"] == 0
        assert res["message"] == "ok"

    @allure.story("Get file download URL")
    def test_get_file_url(self, login_sess):
        token = base.get_file_service_token(login_sess)["data"]["token"]
        res = base.get_file_url(batch_id, token)
        assert res["code"] == 0
        assert res["message"] == "ok"
        assert res["data"]["file_name"] == file_name

    @allure.story("Get attachment list from contract details")
    def test_get_contract_attachment_list(self, login_sess):
        business_id = contract_id
        res = base.get_contract_attachment_list(login_sess, business_id)
        assert res["code"] == 0
        assert res["message"] == "ok"
        file_list = jsonpath.jsonpath(res, "$.data..file_id")
        if file_list:
            assert res["data"][0]["file_id"] == file_id
            assert res["data"][0]["file_name"] == file_name
            assert res["data"][0]["size"] == file_size
        else:
            return False