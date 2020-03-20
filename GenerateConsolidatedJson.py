import json
import glob

# _initializing the result list which holds the information of all repo json objects
result = []

# _iterate through all the repository json files
for index, f in enumerate(glob.glob("Repository_Commit_Data/*_data.json")):
    with open(f, "r", encoding='utf-8', errors='ignore') as infile:
        print(f'Appending File Contents of ... {index+1}. {f}')

        # _append each json object to the list
        result.append(json.load(infile, strict=False))

# _write resulting json to a file
with open("final_repo_data.json", "w") as outfile:
    # _json dump to convert list of json objects to a valid json and write to a file
    json.dump(result, outfile, indent=4)