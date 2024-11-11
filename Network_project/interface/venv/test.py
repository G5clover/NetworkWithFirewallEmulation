import customtkinter
import socket
import json

#turns saved data in list of 2 element lists
result = []
file = open("ip_addresses.txt", "r")
saved_data = file.read()
saved_data = saved_data.replace("[", "")
saved_data = saved_data.replace("]", "")
saved_data = saved_data.replace("'", "")
saved_data = saved_data.replace(",", "")
saved_data = saved_data.split()
file.close()

for item in saved_data:
    ip_host_pair = item.split('-')  # Split by the hyphen
    result.append(ip_host_pair)     # Add each [ip, host] pair to the result

print(result)

def send_data(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to firewall
            client_socket.connect(('127.0.0.1', 5000))
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            print("Updated firewall rule", message)
        except ConnectionRefusedError:
            print("Connection failed")



# Set appearance mode and color theme
customtkinter.set_appearance_mode("Dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

def main(blocked_sites):
    f = open("ip_addresses.txt", "w")
    f.write(blocked_sites)
    f.close()
    return


#Scrollable frame
class MyFrame(customtkinter.CTkScrollableFrame):
    
    def port_block_button(port, frame):
        port = port
        mode = 0
        try:
            port = int(port.get())
        except:
            print('failed')
            return
        
        result_index= 0
        while result_index < len(result):
            if result[result_index][1] == str(port):
                mode=1
                break
            result_index = result_index+1 

        if mode == 0 and isinstance(port, int) and port <= 65535:
            # Create a frame to hold the other labels/buttons inside
            row_frame_port = customtkinter.CTkFrame(master=frame)
            row_frame_port.pack(fill='x', pady=5)  # Add some vertical spacing between rows

            # Label which holds the port
            label_left = customtkinter.CTkLabel(master=row_frame_port, text=port, anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
            label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

            # Button to delete port
            botton_X = customtkinter.CTkButton(master=row_frame_port, text="X", command = lambda: MyFrame.delete_button_port(row_frame_port, port), anchor='center', width=100, font=('TkDefaultFont', 18))
            botton_X.pack(side=customtkinter.RIGHT)
            
            #Adding the port to the result list and to the blocked_sites list
            port = str(port)
            MyFrame.blocked_sites.append('0-{}-0'.format(port))
            result.append(['0', port, '0'])

            # saving the rules
            main(str(MyFrame.blocked_sites))

            # message to send to controller
            message = {
            'protocol': 'tcp',
            'action': 'add',
            'ports': [port]
            }
            
            # Create a TCP socket
            send_data(message)


        
        


        

    # Adds saved data to the gui  (name represents domain if a domain was used as input or ip adress if that was used as input instead)
    def create_row(name, address, source, frame):   
        # If it is a port the place where there would be an address in the sublist is occupied by a '0'
        if address!='0':
            # Create a frame to hold the other labels/buttons inside
            row_frame = customtkinter.CTkFrame(master=frame)
            row_frame.pack(fill='x', pady=5)  

            # Label which holds the destination ip address
            label_left = customtkinter.CTkLabel(master=row_frame, text=name, anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
            label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

            # Label which holds the source ip address
            label_left = customtkinter.CTkLabel(master=row_frame, text=source, anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
            label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

            # Button to delete
            botton_X = customtkinter.CTkButton(master=row_frame, text="X", command = lambda value = name: MyFrame.delete_button(row_frame, value, source), anchor='center', width=100, font=('TkDefaultFont', 18))
            botton_X.pack(side=customtkinter.RIGHT)
        else:
            port = source # if it a port to block then, at the index at where there would be the source ip address, there is the port
            
            # Create a frame to hold the other labels/buttons inside
            row_frame = customtkinter.CTkFrame(master=frame)
            row_frame.pack(fill='x', pady=5)  # Add some vertical spacing between rows

            # Label which holds the port
            label_left = customtkinter.CTkLabel(master=row_frame, text=port, anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
            label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

            # Button to delete
            botton_X = customtkinter.CTkButton(master=row_frame, text="X", command = lambda value = name: MyFrame.delete_button_port(row_frame, port), anchor='center', width=100, font=('TkDefaultFont', 18))
            botton_X.pack(side=customtkinter.RIGHT)

    def delete_button_port(row, port):
        port = port

        #removes the port from the blocked_sites list
        MyFrame.blocked_sites.remove('0-{}-0'.format(port))
        
        #searches for port and deletes it from the result list
        index_result = 0
        while index_result < len(result):
            if result[index_result][1] == port:
                del result[index_result]
            index_result = index_result+1
        
        print(MyFrame.blocked_sites)
        print(str(result))

        #removes the row
        row.destroy() 

        main(str(MyFrame.blocked_sites))

        # message to send to controller
        message = {
            'protocol': 'tcp',
            'action': 'remove',
            'ports': [port]
        }
        


        # Create a TCP socket
        send_data(message)
        


    def delete_button(row, destination, source):
        #checks if destination = all ip addresses and removes from list accordingly
        if destination != '*':
            MyFrame.blocked_sites.remove('{}-{}-{}'.format(socket.gethostbyname(destination), source, destination))
        else:
            MyFrame.blocked_sites.remove('*-{}-*'.format(source))

        index_result = 0

        # gets ip address only if it is not '*' to avoid errors
        if destination != '*':
            destination = socket.gethostbyname(destination)
        
        #searches for it in the result list and deletes it
        while index_result < len(result):
            if result[index_result][0] == destination and result[index_result][1] == source:
                del result[index_result]
            index_result = index_result+1

        print(MyFrame.blocked_sites)
        print(str(result))

        #removes the row
        row.destroy() 

        main(str(MyFrame.blocked_sites))

        # message to send to the controller
        message = {
            'protocol': 'ipv4',
            'action': 'remove',
            'src_ip': source,
            'dst_ip': destination
        }
        


        # Create a TCP socket
        send_data(message)
    

    #blocked_sites list which holds data written to file
    blocked_sites = []
    i=0

    #adds saved rules to blocked_sites list
    while i<len(result):
        blocked_sites.append('{}-{}-{}'.format(result[i][0], result[i][1], result[i][2]))
        i =i+1
    
    #At boot shows all the blocked sites
    print('blocked sites: ' + str(blocked_sites))
        

    # Function to add a rows inside scrollable frame
    def block_button_function(frame, destination, source):
        addr = destination.get()
        source = source.get()

        #if it is different from * it converts input into a ip address, otherwise it is kept as *
        try:
            if addr != '*':
                addr = socket.gethostbyname(addr)
            if source != '*':
                source = socket.gethostbyname(source)
        except:
            return
            

        result_index = 0
        mode = 0

        # checks if ip rule exists already (could be changed with "return" instead eliminating one variable and indentation in the future)
        while result_index < len(result):
            if result[result_index][0] == addr and result[result_index][1] == source:
                mode=1
                break
            result_index = result_index+1

        # if rule does not exist add it
        if mode==0 and source != "":
            try:
                ip_address = addr
                if addr != "":
                    # Create a frame to hold the other labels/buttons inside
                    row_frame = customtkinter.CTkFrame(master=frame)
                    row_frame.pack(fill='x', pady=5)  # Add some vertical spacing between rows

                    # Destination label (destination.get() because if someone puts the domain like this it shows the domain instead of an ip adress (conversion is only 1:1 though))
                    label_left = customtkinter.CTkLabel(master=row_frame, text=destination.get(), anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
                    label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

                    # Source label
                    label_left = customtkinter.CTkLabel(master=row_frame, text=source, anchor='w', padx=15, justify='left', font=('TkDefaultFont', 18))
                    label_left.pack(side=customtkinter.LEFT, fill='x', expand=True)

                    # Button to delete row
                    botton_X = customtkinter.CTkButton(master=row_frame, text="X", command = lambda: MyFrame.delete_button(row_frame, addr, source), anchor='center', width=100, font=('TkDefaultFont', 18))
                    botton_X.pack(side=customtkinter.RIGHT)


                    # adds rule to lists
                    MyFrame.blocked_sites.append('{}-{}-{}'.format(ip_address, source, addr))
                    result.append([ip_address, source, addr])
                
                    print(MyFrame.blocked_sites)
                    print('result: ' + str(result))

                    main(str(MyFrame.blocked_sites))
                    
                print("button pressed")

                
                # message to send to the controller
                message = {
                    'protocol': 'ipv4',
                    'action': 'add',
                    'src_ip': source,
                    'dst_ip': ip_address
                }
                


                # Create a TCP socket
                send_data(message)


            except:
                return

     

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        #Label description
        self.label = customtkinter.CTkLabel(self, text="Inputting * in the ip boxes corresponds to all ip adresses")
        self.label.pack(padx=20, pady=5)

        #Label description
        self.label = customtkinter.CTkLabel(self, text="Destination (Ip address/Port/Domain)         -         Source (Ip address)")
        self.label.pack(padx=20, pady=1)

        
    



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Set the window size depending on the size of the monitor/display
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry('{}x{}'.format(screen_width, screen_height))

        # Create a scrollable frame inside the app
        self.my_frame = MyFrame(master=self, width=500, height=screen_height*(2/3))
        self.my_frame.pack(pady=20, fill = 'x')




        # Create a frame to hold the other labels/buttons inside (ip frame)
        row_frame = customtkinter.CTkFrame(master=self)
        row_frame.pack(side=customtkinter.BOTTOM, fill='x', pady=10)  # Add some vertical spacing between rows

        # Input for destination
        self.entry = customtkinter.CTkEntry(master=row_frame, placeholder_text="What Ip do you want to block?")
        self.entry.pack(side=customtkinter.LEFT, fill= 'x', expand = True, ipadx=200, padx=10)

        # Input for source
        self.entry2 = customtkinter.CTkEntry(master=row_frame, placeholder_text="For which Ip address do you want to block it?")
        self.entry2.pack(side=customtkinter.LEFT,fill= 'x', expand = True, ipadx=200, pady=20, padx=10)

        # Block button
        self.button = customtkinter.CTkButton(master=row_frame, text="Block", command = lambda: MyFrame.block_button_function(self.my_frame, self.entry, self.entry2))
        self.button.pack(side=customtkinter.LEFT, fill= 'x', expand = True, pady=20, padx=10)



        # Create a frame to hold the other labels/buttons inside (port frame)
        row_frame2 = customtkinter.CTkFrame(master=self)
        row_frame2.pack(side=customtkinter.BOTTOM, fill='x', pady=10)  # Add some vertical spacing between rows

        # Input for port
        self.port_entry = customtkinter.CTkEntry(master=row_frame2, placeholder_text="What port do you want to block?")
        self.port_entry.pack(side=customtkinter.LEFT, fill= 'x', expand = True, ipadx=200, padx=10)

        # Block button
        self.button = customtkinter.CTkButton(master=row_frame2, text="Block", command = lambda: MyFrame.port_block_button(self.port_entry, self.my_frame))
        self.button.pack(side=customtkinter.LEFT, fill= 'x', expand = True, pady=20, padx=10)


        # load the saved rules in the gui and send them to the controller
        i=0
        while i < (len(result)):
            MyFrame.create_row(result[i][2], result[i][0], result[i][1], self.my_frame)


            if result[i][0] == '0':
                message = {
                    'protocol': 'tcp',
                    'action': 'add',
                    'ports': [result[i][1]]
                }
            else:
                message = {
                    'protocol': 'ipv4',
                    'action': 'add',
                    'src_ip': result[i][1],
                    'dst_ip': result[i][0]
                }
           


            send_data(message)

            i = i + 1
        

   
        


# Run the application
app = App()
app.mainloop()
