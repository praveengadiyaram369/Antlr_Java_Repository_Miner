import json
import glob

result = []                                         #list that will store the results of all Json 
for f in glob.glob("Repository_Commit_Data/*.json"):                       #here you will loop over multiple Json files
    with open(f, "r" ,encoding='utf-8', errors='ignore') as infile:   
        print(f'{f}')                 
        result.append(json.load(infile, strict=False)) 

with open("merged_file.json", "w") as outfile:    #filling the resultant file with Jason content
     json.dump(result, outfile, indent=4)