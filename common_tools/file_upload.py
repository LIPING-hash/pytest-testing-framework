import requests
import os
import hashlib
import sys
import json
from os import path
from importlib import reload
from common_tools.env_config import envConfig

# Initialize environment configuration
conf_init = envConfig

# [REDACTED]: file service endpoint
pre_url = conf_init["host"]["file_service_v2"]
nc = PreContract()


class TestContractFileBase:

    # Calculate MD5 hash of a file
    def get_md5(self, path):
        m = hashlib.md5()
        with open(path, 'rb') as f:
            for line in f:
                m.update(line)
        md5code = m.hexdigest()
        return md5code

    # Retrieve token for file service authentication
    def get_file_service_token(self, login_sess):
        resp = login_sess.api_get(url="[REDACTED]-service/web/attachment/get-file-service-token",
                                  caseName="Get file service token")
        return resp

    # Initialize multipart upload session
    def initiate_multipart_upload(self, token, file_name, file_size, file_md5):
        params = {
                    "file_name": file_name,
                    "file_size": file_size,
                    "file_md5": file_md5
                }
        headers = {"token": token,
                   "accept-encoding": "gzip, deflate, br",
                   "Content-Type": "application/json"
                   }
        resp = requests.post(url=pre_url + "/initiate-multipart-upload",
                             data=json.dumps(params), headers=headers
                             ).json()
        return resp

    # Upload a single part of a multipart upload
    def upload_part(self, token, batch_id, part_number, part_md5, data):
        headers = {"token": token,
                   "accept-encoding": "gzip, deflate, br",
                   "Content-Type": "application/octet-stream"
                   }
        params = {"batch_id": batch_id,
                  "part_number": part_number,
                  "part_md5": part_md5}
        resp = requests.post(url=pre_url+"/upload-part", params=params, data=data,
                             headers=headers).json()
        return resp

    # Complete multipart upload after all parts are uploaded
    def complete_multipart_upload(self, batch_id, token):
        headers = {"token": token,
                   "accept-encoding": "gzip, deflate, br",
                   "Content-Type": "application/json"
                   }
        params = {"batch_id": batch_id}
        data = { }
        resp = requests.post(url=pre_url+"/complete-multipart-upload", params=params, data=data, headers=headers,
                            ).json()
        return resp

    # Retrieve file URL using batch ID
    def get_file_url(self, batch_id, token):
        headers = {"token": token}
        params = {"response_content_disposition": "inline"}
        resp = requests.get(url=pre_url+"/"+batch_id, json=params, headers=headers).json()
        return resp

    # Edit contract details (e.g., update attached file)
    def contract_detail_edit(self, login_sess, contract_id, file_name, file_id, upload_time, file_size, file_ext):
        params = {
                    "contract_id": contract_id,
                    "files": [
                        {
                            "file_id": file_id,
                            "file_name": file_name,
                            "format": file_ext,
                            "size": file_size,
                            "upload_time": upload_time,
                            "id": "[REDACTED]"  # Example: "fsl078o90u18060ad8587"
                        }
                    ]
                }
        resp = login_sess.api_post(url="[REDACTED]-service/[REDACTED]/[REDACTED]/detail-edit", json=params,
                                   caseName="Update contract attachment")
        return resp

    # Fetch attachment list for a given business entity
    def get_contract_attachment_list(self, login_sess, business_id):
        res = login_sess.api_get(url="[REDACTED]-service/web/attachment/list?business=[REDACTED]&business_id=" + business_id)
        return res

if __name__ == '__main__':
     a = path.dirname("[REDACTED]")
     base_path = os.path.dirname(os.path.realpath(__file__))
     print(base_path)