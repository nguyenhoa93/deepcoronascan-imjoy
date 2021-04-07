"""
Dataset uploader 
"""
import os
import time
import requests
import zipfile
from configs import *

# %% Connect to task server
# listing tasks
response = requests.get(
    BASE_URL + "/tasks", headers={"Authorization": f"Bearer {TOKEN}"}
)
response_obj = response.json()
assert (
    response_obj.get("success") == True
), f"Failed to requesting URL for upload, error: {response_obj.get('detail')}"
tasks = response_obj["result"]

assert (
    DATASET_ID in tasks
), f"Task {DATASET_ID} not found, must be one of: {list(tasks.keys())}"

all_samples = os.listdir(DATASET_DIR)
# %% Upload stats
print("Upload statistics")
STATS_FILES = ["image.ome.tif", "cam.ome.tif", "annotations.json",
               "image.ome.tif_offsets.json", "cam.ome.tif_offsets.json"]
sample_id = "stats"
print(f"===> Uploading {sample_id} ...")
response = requests.get(
    BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}/upload?exist_ok=1",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json=UPLOAD_FILES
)
response_obj = response.json()
assert (
    response_obj.get("success") == True
), f"Failed to requesting URL for upload, error: {response_obj.get('detail')}"
result = response_obj["result"]
# upload files
for file_name in STATS_FILES:
    input_file = os.path.join("data/stats", file_name)
    upload_url = result["files"][file_name]

    # read the file content here
    content = open(input_file, "rb")
    response = requests.put(upload_url, data=content)
    assert (
        response.status_code == 200
    ), f"failed to upload file: {file_name}, {response.reason}: {response.text}"
    
# now refresh this sample
response = requests.post(
    BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}/refresh",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
response_obj = response.json()
assert (
    response_obj.get("success") == True
), f"Failed toc enable sample, error: {response_obj.get('detail')}"

response = requests.get(
    BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
response_obj = response.json()
assert (
    response_obj.get("success") == True
), f"Failed to enable sample, error: {response_obj.get('detail')}"
for file in response_obj["result"]["files"]:
    url = response_obj["result"]["files"][file]
    print(f"{file}: {url}")
    
# %% Upload sample(s) to the task
count = 0
for sample_id in all_samples:
    if not os.path.isdir(os.path.join(DATASET_DIR, sample_id)):
        continue
    count += 1
    print(f"===> ({count}/{len(all_samples)}) Uploading {sample_id} ...")
    response = requests.get(
        BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}/upload?exist_ok=1",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json=UPLOAD_FILES
    )
    response_obj = response.json()
    assert (
        response_obj.get("success") == True
    ), f"Failed to requesting URL for upload, error: {response_obj.get('detail')}"
    result = response_obj["result"]
    # upload files
    for file_name in UPLOAD_FILES:
        if file_name == "annotations":
            input_file = os.path.join("src/annotation.json")
        else:
            input_file = os.path.join(DATASET_DIR, sample_id, file_name)
        upload_url = result["files"][file_name]

        # read the file content here
        content = open(input_file, "rb")
        response = requests.put(upload_url, data=content)
        assert (
            response.status_code == 200
        ), f"failed to upload file: {file_name}, {response.reason}: {response.text}"

        if file_name not in CONVERT_FILES:
            continue
        
        # convert format
        response = requests.post(
            BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}/convert",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={input_file: {"format": "ome-tiff", "output_file": CONVERT_FILES[input_file]} for input_file in result["files"]}
        )
        response_obj = response.json()
        assert (
            response_obj.get("success") == True
        ), f"Failed to convert sample, error: {response_obj.get('detail')}"
        session_id = response_obj["result"]["session_id"]
        # check conversion status
        while True:
            response = requests.get(
                BASE_URL + f"/conversion/status/{session_id}",
                headers={"Authorization": f"Bearer {TOKEN}"},
            )
            response_obj = response.json()
            assert (
                response_obj.get("success") == True
            ), f"Failed to get conversion status, error: {response_obj.get('detail')}"
            result = response_obj["result"]
            print(result["status"])
            if result['completed']:
                break
            time.sleep(1)
            
            
    # now refresh this sample
    response = requests.post(
        BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}/refresh",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    response_obj = response.json()
    assert (
        response_obj.get("success") == True
    ), f"Failed toc enable sample, error: {response_obj.get('detail')}"

    response = requests.get(
        BASE_URL + f"/dataset/{DATASET_ID}/sample/{sample_id}",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    response_obj = response.json()
    assert (
        response_obj.get("success") == True
    ), f"Failed to enable sample, error: {response_obj.get('detail')}"
    for file in response_obj["result"]["files"]:
        url = response_obj["result"]["files"][file]
        print(f"{file}: {url}")