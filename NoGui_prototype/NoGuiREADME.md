
# Network-Project

A virtual mininet Network with a POX controller to handle traffic between clients. The POX controller includes a stateful firewall which receives rules from a messenger client


## Usage

Install a mininet vm

Move firewall.py to ```~/pox/pox/misc```\
Move star-topology.py to ```~/mininet/custom``` 

### Note: You will need to run the files in different terminal shell windows (Use a terminal multiplexer for this) 

Execute the following command to start the mininet topology
```bash
sudo mn --custom ~/mininet/custom/star-topology.py --topo mytopo --controller=remote,ip=127.0.0.1,port=6633 --nat
```
In a different shell window execute these commands to run the controller 
```bash
cd ~/pox
./pox.py log.level --DEBUG forwarding.l2_learning misc.firewall
```

In a third shell window execute this command to run the messenger client
```bash
python client.py
```


    
