# 0004-Homelab_Monitor
0004-Homelab_Monitor is a python project for monitoring my Homelab setup's hardware information. 

## To run the monitor, execute the following commands and open in your browser:
```python
pip3 install -r requirements_server.txt
python3 app.py -s --ip 0.0.0.0 --port 5000
```
setting the ip to 0.0.0.0 will make it accessible to all devices on the network make sure to only set the ip if on a trusted network. Otherwise, do not set the ip
the port can be any port number you want

## To run the client, execute the following commands:
```python
 pip3 install -r requirements_client.txt
 python3 app.py -c
```