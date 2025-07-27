import sys
import os
import json
from pprint import pprint
from datetime import datetime

os.system('cls' if os.name == 'nt' else 'clear')
file1 = sys.argv[0]
filename = os.path.basename(file1)

if len(sys.argv) != 3:
    print(f"Usage: python3 {filename} <file1> <file2>")
    sys.exit(1)

file1 = sys.argv[1]
file2 = sys.argv[2]


now = datetime.now()
dt = now.strftime("%Y%m%d%H%M%S")

current_dir = os.getcwd()
dbscust_final_file = os.path.join(current_dir, f"dbscust_final_{dt}.txt")
log_file = os.path.join(current_dir, f"logfile_{dt}.txt")
flag = True

# file1 = r"D:\Guvi\Guvi_workshop\files\postgresql.conf_13"
# file2 = r"D:\Guvi\Guvi_workshop\files\postgresql.conf_16"
diff_file = r"D:\Guvi\Guvi_workshop\files\diff_file_{}.txt".format(dt)
dbscust_final_file = r"D:\Guvi\Guvi_workshop\files\dbscust_final_{}.txt".format(dt)
log_file = r"D:\Guvi\Guvi_workshop\files\logfile_{}.txt".format(dt)
# file1 = r"D:\Guvi\Guvi_workshop\files\file3.json"
# file2 = r"D:\Guvi\Guvi_workshop\files\file4.json"
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

def find_differences(data1, data2):
    only_in_data1 = data1.keys() - data2.keys()
    only_in_data2 = data2.keys() - data1.keys()
    common_keys = data1.keys() & data2.keys()
    changed_values = {k: (data1[k], data2[k]) for k in common_keys if data1[k] != data2[k]}
    
    #return only_in_data1, only_in_data2, common_keys, changed_values
    # return {
    #     "only_in_data1": only_in_data1,
    #     "only_in_data2": only_in_data2,
    #     "common_keys": common_keys,
    #     "changed_values": changed_values
    # }

    return changed_values

def final_dbscust (data1, data2):
    all_keys = set(data1.keys()) | set(data2.keys())
    data1_keys = set(data1.keys()) 
    data2_keys = set(data2.keys())

    with open(dbscust_final_file, 'w') as df, open(log_file, 'w') as lf:
        for key in all_keys:
            lf.write(f"Processing parameter: {key}| old_value= {data1.get(key, None)} | new_value= {data2.get(key, None)}\n")
            # if key in skip_keys:
            #     continue    #Skip specific keys

            value1 = data1.get(key, None)
            value2 = data2.get(key, None)
            
            if key in skip_keys:
               lf.write(f"skiped this parameter since it is in the skip list\n")
               #continue    #Skip specific keys                        
            elif key in keep_newver_keys:
                df.write(f"{key} = {value2}\n")
                #lf.write(f"modified to new version value: {value2}\n")
                lf.write(f"no modification and kept as new version value: {value2}\n")
            elif key in keep_oldver_keys:
                df.write(f"{key} = {value1}\n")
                lf.write(f"modified to old version value: {value1}\n")
            elif key not in data1_keys:
                df.write(f"{key} = {value2}\n")
                lf.write(f"no modification and kept as new version value: {value2}\n")
            elif value1 != value2:
                # if key in skip_keys:
                #     continue    #Skip specific keys   
                #df.write(f"{key} : file1_value= {value1} | file2_value= {value2}\n")
                df.write(f"{key} = {value1}\n")
                lf.write(f"modified to old version value: {value1}\n")
            # elif key in skip_keys:
            #     df.write(f"{key} = {value2}\n")
            else:
                df.write(f"{key} = {value2}\n")
                lf.write(f"no modification and kept as new version value: {value2}\n")
        lf.write(f"Final parameters and values updated in:" + " {}".format(dbscust_final_file))
    # only_in_data1 = data1.keys() - data2.keys()
    # only_in_data2 = data2.keys() - data1.keys()
    # common_keys = data1.keys() & data2.keys()
    # changed_values = {k: (data1[k], data2[k]) for k in common_keys if data1[k] != data2[k]}
    
    #return only_in_data1, only_in_data2, common_keys, changed_values
    # return {
    #     "only_in_data1": only_in_data1,
    #     "only_in_data2": only_in_data2,
    #     "common_keys": common_keys,
    #     "changed_values": changed_values
    # }

    #return all_keys
# parameters = final_dbscust(data1, data2)
# print("\nFinal parameter name:")
# pprint("{}".format(parameters))

def generate_dbscust(flag):
    if flag == True:
        # Call the function to generate dbscust.conf
        print("\nGenerating dbscust.conf file...")
        final_dbscust(data1, data2)
        print("Final file path:", dbscust_final_file)
        print("Log file path:", log_file)
    else:
        print("\nNo changes detected, dbscust.conf generation skipped.")
        # Check if there are any differences
        for key, (value1, value2) in changed_values.items():
            diff = find_differences(data1, data2)
            print ("\nDifferences found:")
            pprint(diff)

# # Call the function to generate dbscust.conf
# print("\nGenerating dbscust.conf file...")
# final_dbscust (data1, data2)
# #print("\nFinal parameters & values:" + " {}".format(dbscust_final_file))
# print("Final file path:", dbscust_final_file)
# print("Log file path:", log_file)

#for key, (value1, value2) in changed_values.items():
# diff = find_differences(data1, data2)
# print ("\nDifferences found:")
# pprint(diff)

# print("\nCommon parameters with different values:")
# for key, (value1, value2) in changed_values.items():
#     #print(f"{key} = {value1} (data1) vs {value2} (data2)")  
#     pprint(f"{key} : file1_value= {value1} | file2_value= {value2}")  
#     with open(diff_file, 'a') as df:
#         df.write(f"{key} : file1_value= {value1} | file2_value= {value2}\n")

# print ("\ndiff_file created in: ", diff_file)        