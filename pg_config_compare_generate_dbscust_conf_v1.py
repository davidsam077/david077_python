import sys
import os
import json
from pprint import pprint
from datetime import datetime

os.system('cls' if os.name == 'nt' else 'clear')
file1 = sys.argv[0]
filename = os.path.basename(file1)

# if len(sys.argv) != 3:
#     print(f"Usage: python3 {filename} <file1> <file2> <dbscust/nodbscust>")
#     print(f"[or] Show the Diff/Comman")
#     print(f"Usage: python3 {filename} <file1> <file2> <nodbscust> <diff/comman/new/old>")
#     sys.exit(1)

# file1 = sys.argv[1]
# file2 = sys.argv[2]
# flag = sys.argv[1]
# option = sys.argv[2]

now = datetime.now()
dt = now.strftime("%Y%m%d%H%M%S")

current_dir = os.getcwd()
dbscust_final_file = os.path.join(current_dir, f"dbscust_final_{dt}.txt")
log_file = os.path.join(current_dir, f"logfile_{dt}.txt")
flag = "nodbscust"
option = "diff"
#flag dbscust/nodbscust
#option diff/new/old/comman

file1 = "/Users/davidr/Documents/david_guvi/guvi_tasks_workshops/postgresql.conf_13"
file2 = "/Users/davidr/Documents/david_guvi/guvi_tasks_workshops/postgresql.conf_16"
# file1 = r"/Users/davidr/Documents/david_guvi/guvi_tasks_workshops/postgresql.conf_13"
# file2 = r"/Users/davidr/Documents/david_guvi/guvi_tasks_workshops/postgresql.conf_16"
diff_file = r"D:\Guvi\Guvi_workshop\files\diff_file_{}.txt".format(dt)
dbscust_final_file = r"D:\Guvi\Guvi_workshop\files\dbscust_final_{}.txt".format(dt)
log_file = r"D:\Guvi\Guvi_workshop\files\logfile_{}.txt".format(dt)

#Skipping keys in dbscust.conf - deprecated parameters, or specific to ignore in new version dbscust.conf
skip_keys = ['data_directory','log_directory','edb_audit_directory','idle_in_transaction_session_timeout']
#Kee the same parameters as like new version dbscust.conf
keep_newver_keys = ['port']
keep_oldver_keys = []
#keep_old_keys = ['idle_in_transaction_session_timeout', 'data_directory']


def is_json_file(filepath):
    if not os.path.isfile(filepath):
        return False    
    if not filepath.endswith('.json'):
        return False

    try:
        with open(filepath, 'r') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {filepath} is not a valid JSON file. {e}")
        return False
    return True


def process_file(filepath):
    line_dict = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            #print(line)

            if not line or line.startswith('#'):
                continue

            #print(line)
            line_parts = line.split('#', 1)
            # print(line_parts)
            first_parts = line_parts[0].strip()
            #print (first_parts)

            #line_dict = {}
            if '=' in first_parts:
                key, value = first_parts.split('=', 1)
                line_dict[key.strip()] = value.strip()
            else:
                line_dict[first_parts] = None
    return line_dict

def chk_json(json_file, json_true):
    if json_true is True:
        with open(json_file, 'r') as f:
            return json.load(f)         #Load JSON file into dict
    else:
        return process_file(json_file)  #non-JSON (postgresql.conf)
    
json_file1= is_json_file(file1)
json_file2= is_json_file(file2)
data1 = chk_json(file1, json_file1)
data2 = chk_json(file2, json_file2)

# # Find keys only in data1
only_in_data1 = data1.keys() - data2.keys()
# # Find keys only in data2
only_in_data2 = data2.keys() - data1.keys()
# # Find common keys
common_keys = data1.keys() & data2.keys()
# # Find common keys with different values
changed_values = {k: (data1[k], data2[k]) for k in data1.keys() & data2.keys() if data1[k] != data2[k]}

def find_differences(data1, data2, option):
    only_in_data1 = data1.keys() - data2.keys()
    only_in_data2 = data2.keys() - data1.keys()
    common_keys = data1.keys() & data2.keys()
    #common_keys = {k: (data1[k], data2[k]) for k in common_keys if data1[k] == data2[k]}
    changed_values = {k: (data1[k], data2[k]) for k in common_keys if data1[k] != data2[k]}
    
    #return only_in_data1, only_in_data2, common_keys, changed_values
    # return {
    #     "only_in_data1": only_in_data1,
    #     "only_in_data2": only_in_data2,
    #     "common_keys": common_keys,
    #     "changed_values": changed_values
    # }

    if option == "old":
        return only_in_data1            #set
    elif option == "new":
        return only_in_data2            #set
    elif option == "comman":
        return common_keys              #set
    else:
        return changed_values           #dict
    
    #return only_in_data1               #set
    
def final_dbscust (data1, data2):
    all_keys = set(data1.keys()) | set(data2.keys())
    data1_keys = set(data1.keys()) 
    data2_keys = set(data2.keys())

    with open(dbscust_final_file, 'w') as df, open(log_file, 'w') as lf:
        for key in all_keys:
            lf.write(f"[INFO] Parameter: {key} |old: {data1.get(key, None)} | new= {data2.get(key, None)} | Action:")
            
            value1 = data1.get(key, None)
            value2 = data2.get(key, None)
            
            if key in skip_keys:
               lf.write(f"skiped this parameter since it is in the skip list\n")
               #continue    #Skip specific keys                        
            elif key in keep_newver_keys:
                df.write(f"{key} = {value2}\n")
                #lf.write(f"modified to new version value: {value2}\n")
                lf.write(f"No modification made; retained new version value: {value2}\n")
            elif key in keep_oldver_keys:
                df.write(f"{key} = {value1}\n")
                lf.write(f"Modified to old version value: {value1}\n")
            elif key not in data1_keys:
                df.write(f"{key} = {value2}\n")
                lf.write(f"No modification made; retained new version value: {value2}\n")
            elif value1 != value2:
                # if key in skip_keys:
                #     continue    #Skip specific keys   
                #df.write(f"{key} : file1_value= {value1} | file2_value= {value2}\n")
                df.write(f"{key} = {value1}\n")
                lf.write(f"Modified to old version value: {value1}\n")
            # elif key in skip_keys:
            #     df.write(f"{key} = {value2}\n")
            else:
                df.write(f"{key} = {value2}\n")
                lf.write(f"No modification made; retained new version value: {value2}\n")
        lf.write(f"[INFO] Final parameters and values updated in:" + " {}".format(dbscust_final_file))

if flag == 'dbscust':
    #function to generate dbscust.conf
    print("\nGenerating dbscust.conf file...")
    final_dbscust(data1, data2)
    print("Final file path:", dbscust_final_file)
    print("Log file path:", log_file)
else:
    #print("\nNo changes detected, dbscust.conf generation skipped.")
    diff = find_differences(data1, data2, option)
    
    if option == "diff":  
        for key, (value1, value2) in diff.items():
            print (f"Parameter: {key} | Old: {value1} | New: {value2}")
    else:
        for key in diff:
            value1 = data1.get(key)
            value2 = data2.get(key)
            print(f"parameter: {key} |old: {value1} | new: {value2}")