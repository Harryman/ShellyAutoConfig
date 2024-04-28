import requests
import json
import time
from jinja2 import Template

# Load configurations from site-config.json
with open('site-config.json') as config_file:
    config = json.load(config_file)

# Prompt for user input
name = input("Enter the device name: ")
topic_prefix = input("Enter the MQTT topic prefix: ")
ip_address = input("Enter the IP address of the target device: ")

# Construct the base URL for the device
base_url = f"http://{ip_address}/rpc"

# Configure system settings
sys_config = {
    "device": {
        "name": name
    },
    "location": config['location']
}
sys_url = f"{base_url}/Sys.SetConfig?config={json.dumps(sys_config)}"
print("System configuration request:", sys_url)
response = requests.get(sys_url)
if response.status_code == 200:
    try:
        print("System configuration response:", response.json())
    except json.JSONDecodeError:
        print("System configuration response:", response.text)
else:
    print("System configuration failed with status code:", response.status_code)

# Configure WiFi settings
wifi_config = config['wifi']
wifi_url = f"{base_url}/WiFi.SetConfig?config={json.dumps(wifi_config)}"
print("WiFi configuration request:", wifi_url)
response = requests.get(wifi_url)
if response.status_code == 200:
    try:
        print("WiFi configuration response:", response.json())
    except json.JSONDecodeError:
        print("WiFi configuration response:", response.text)
else:
    print("WiFi configuration failed with status code:", response.status_code)

# Configure MQTT settings
mqtt_config = {
    "enable": True,
    "server": config['mqtt']['server'],
    "client_id": name,
    "topic_prefix": topic_prefix,
    "user": config['mqtt'].get('user', None),
    "ssl_ca": config['mqtt'].get('ssl_ca', None),
    "rpc_ntf": config['mqtt'].get('rpc_ntf', True),
    "status_ntf": config['mqtt'].get('status_ntf', False),
    "use_client_cert": config['mqtt'].get('use_client_cert', False),
    "enable_control": config['mqtt'].get('enable_control', True)
}
mqtt_url = f"{base_url}/MQTT.SetConfig?config={json.dumps(mqtt_config)}"
print("MQTT configuration request:", mqtt_url)
response = requests.get(mqtt_url)
if response.status_code == 200:
    try:
        print("MQTT configuration response:", response.json())
    except json.JSONDecodeError:
        print("MQTT configuration response:", response.text)
else:
    print("MQTT configuration failed with status code:", response.status_code)

# Configure Switch settings for all switches (0-3)
for switch_id in range(4):
    switch_config = {
        "in_mode": "detached",
        "initial_state": "off"
    }
    switch_url = f"{base_url}/Switch.SetConfig?id={switch_id}&config={json.dumps(switch_config)}"
    print(f"Switch {switch_id} configuration request:", switch_url)
    response = requests.get(switch_url)
    if response.status_code == 200:
        try:
            print(f"Switch {switch_id} configuration response:", response.json())
        except json.JSONDecodeError:
            print(f"Switch {switch_id} configuration response:", response.text)
    else:
        print(f"Switch {switch_id} configuration failed with status code:", response.status_code)

# Prompt for ganged inputs
while True:
    ganged_inputs = input("Are there any inputs to be ganged? (y/n): ")

    if ganged_inputs.lower() == 'y':
        gang_name = input("Gang name: ")
        ganged_ids = input("Which inputs are ganged together? [1-4]: ")
        ganged_ids = [int(id) - 1 for id in ganged_ids.split(',')]
        default_state = input("Default state for the gang (on/off): ")

        # Load Jinja2 templates from files
        with open('ShellyScripts/ganged.js', 'r') as f:
            gang_template = Template(f.read())

        with open('ShellyScripts/add.js', 'r') as f:
            add_template = Template(f.read())

        # Create scripts
        gang_script = gang_template.render(gang_name=gang_name, ganged_ids=ganged_ids)
        add_script = add_template.render(gang_name=gang_name, ganged_ids=ganged_ids)

        # Create the "gang" script
        gang_script_url = f"{base_url}/Script.Create?name={gang_name}-ganged"
        response = requests.get(gang_script_url)
        if response.status_code == 200:
            try:
                gang_script_id = response.json()['id']
                print(f"Gang script created with ID: {gang_script_id}")
            except json.JSONDecodeError:
                print("Gang script creation response:", response.text)
        else:
            print(f"Gang script creation failed with status code: {response.status_code}")

        # Upload the "gang" script code
        gang_script_code = gang_script.encode('utf-8')
        chunk_size = 1024
        if len(gang_script_code) > chunk_size:
            # Split the code into chunks
            chunks = [gang_script_code[i:i+chunk_size] for i in range(0, len(gang_script_code), chunk_size)]
            for i, chunk in enumerate(chunks):
                append = 'true' if i > 0 else 'false'
                gang_script_code_url = f"{base_url}/Script.PutCode?id={gang_script_id}&code={chunk.decode('utf-8')}&append={append}"
                response = requests.get(gang_script_code_url)
                if response.status_code != 200:
                    print(f"Gang script code upload failed for chunk {i+1} with status code: {response.status_code}")
                    break
            else:
                print("Gang script code uploaded successfully")
        else:
            gang_script_code_url = f"{base_url}/Script.PutCode?id={gang_script_id}&code={gang_script_code.decode('utf-8')}"
            response = requests.get(gang_script_code_url)
            if response.status_code == 200:
                try:
                    print("Gang script code uploaded successfully")
                except json.JSONDecodeError:
                    print("Gang script code upload response:", response.text)
            else:
                print(f"Gang script code upload failed with status code: {response.status_code}")

        # Create the "add" script
        add_script_url = f"{base_url}/Script.Create?name={gang_name}-add"
        response = requests.get(add_script_url)
        if response.status_code == 200:
            try:
                add_script_id = response.json()['id']
                print(f"Add script created with ID: {add_script_id}")
            except json.JSONDecodeError:
                print("Add script creation response:", response.text)
        else:
            print(f"Add script creation failed with status code: {response.status_code}")

        # Upload the "add" script code
        add_script_code = add_script.encode('utf-8')
        if len(add_script_code) > chunk_size:
            # Split the code into chunks
            chunks = [add_script_code[i:i+chunk_size] for i in range(0, len(add_script_code), chunk_size)]
            for i, chunk in enumerate(chunks):
                append = 'true' if i > 0 else 'false'
                add_script_code_url = f"{base_url}/Script.PutCode?id={add_script_id}&code={chunk.decode('utf-8')}&append={append}"
                response = requests.get(add_script_code_url)
                if response.status_code != 200:
                    print(f"Add script code upload failed for chunk {i+1} with status code: {response.status_code}")
                    break
            else:
                print("Add script code uploaded successfully")
        else:
            add_script_code_url = f"{base_url}/Script.PutCode?id={add_script_id}&code={add_script_code.decode('utf-8')}"
            response = requests.get(add_script_code_url)
            if response.status_code == 200:
                try:
                    print("Add script code uploaded successfully")
                except json.JSONDecodeError:
                    print("Add script code upload response:", response.text)
            else:
                print(f"Add script code upload failed with status code: {response.status_code}")

        # Set the default state of the gang using Switch.SetConfig
        for switch_id in ganged_ids:
            switch_config = {
                "in_mode": "detached",
                "initial_state": default_state
            }
            switch_url = f"{base_url}/Switch.SetConfig?id={switch_id}&config={json.dumps(switch_config)}"
            response = requests.get(switch_url)
            if response.status_code == 200:
                try:
                    print(f"Switch {switch_id} default state set to {default_state}")
                except json.JSONDecodeError:
                    print(f"Switch {switch_id} default state response:", response.text)
            else:
                print(f"Setting default state for switch {switch_id} failed with status code: {response.status_code}")

    else:
        break

# Reboot the device
reboot_url = f"{base_url}/Shelly.Reboot"
print("Reboot request:", reboot_url)
response = requests.get(reboot_url)
if response.status_code == 200:
    try:
        print("Reboot response:", response.json())
    except json.JSONDecodeError:
        print("Reboot response:", response.text)
else:
    print("Reboot failed with status code:", response.status_code)

print("Configuration complete. Waiting for the device to reboot...")
# Delay for 10 seconds to allow the device to reboot
time.sleep(10)

# Check the reboot status
status_url = f"{base_url}/Shelly.GetStatus"
response = requests.get(status_url)
if response.status_code == 200:
    try:
        status = response.json()
        if status['uptime'] < 15:
            print("Device successfully rebooted")
        else:
            print("Device reboot failed")
    except json.JSONDecodeError:
        print("Reboot status check failed")
else:
    print("Reboot status check failed with status code:", response.status_code)

print("Configuration and reboot process finished.")
