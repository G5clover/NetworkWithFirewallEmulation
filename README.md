# Network-Project
A virtual mininet Network with a POX controller to handle traffic between clients. The POX controller includes a firewall which receives rules from a messenger client.

## Usage
Install and run the mininet virtual machine.\
Install xfce or any other desktop environment on it to use a GUI.\
Install pip3 to install tkintercustom.\
\
The controller is in /pox/ext as suggested in the documentation.\
Use python3 to run gui.\
Use python2 to run controller and topology to avoid compatibility issues.\

## Running of software from /Network_project/interface/venv: (use: ```source venv/Scripts/activate``` to activate virtual environment)
1. Once inside the activated venv use ```pip3 install customtkinter```
   
3. To run the GUI.
   ```bash
   python3 test.py 
   ```


## Running of software from ```/Network_project/new/newvenv```: (use: ```source newvenv/bin/activate``` to activate virtual environment)
1. To run the controller:
   ```bash
   python2 ./pox/pox.py log.level --DEBUG forwarding.l2_learning firewall2
   ```
   
3. To run the topology:
   ```bash
   python2 mytopo.py (topology)
   ```


