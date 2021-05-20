"""
Delete samples 
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

# listing samples
response = requests.get(
    BASE_URL + "/dataset/" + DATASET_ID + "/samples", headers={"Authorization": f"Bearer {TOKEN}"}
)
response_obj = response.json()
assert (
    response_obj.get("success") == True
), f"Failed to requesting URL for upload, error: {response_obj.get('detail')}"
samples = response_obj["result"]

for sample in samples:
    # Delete sample
    print(sample)
    response = requests.delete(
        BASE_URL + "/dataset/" + DATASET_ID + "/sample/" + sample, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    response_obj = response.json()
    assert (
        response_obj.get("success") == True
    ), f"Failed to requesting URL for delete, error: {response_obj.get('detail')}"
    
    print("Deleted!")