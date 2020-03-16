import json
import glob

result = []                                         #list that will store the results of all Json 
for index, f in enumerate(glob.glob("Repository_Commit_Data/*_data.json")):                       #here you will loop over multiple Json files
    with open(f, "r" ,encoding='utf-8', errors='ignore') as infile:   
        print(f'Appending File Contents of ... {index+1}. {f}')                 
        result.append(json.load(infile, strict=False)) 

with open("final_repo_data.json", "w") as outfile:    #filling the resultant file with Jason content
     json.dump(result, outfile, indent=4)