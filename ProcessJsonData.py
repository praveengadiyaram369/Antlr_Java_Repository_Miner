import json
from RepositoryData import Repository
from CommitData import Commit
from FileData import File

with open('final_repo_data.json', "r", encoding='utf-8', errors='ignore') as infile:
    json_object_list = json.load(infile, strict=False)
    for json_object in json_object_list:
        print(type(json_object))
