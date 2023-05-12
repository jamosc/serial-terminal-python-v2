import tkinter as tk
from tkinter import ttk
from serial_class import SerialClass
from threading import *
import threading
from time import sleep
import math

# improve jogging
# disable buttons when connecting

class Terminal():
    def __init__(self):

        #######################################################################

        # MAIN WINDOW CONFIGURATION

        self.root = tk.Tk()

        # title and icon config
        self.root.title("Python Serial Terminal")
        icon = tk.PhotoImage(file='ufu-logo.png')
        self.root.iconphoto(False, icon)

        # window geometry config
        self.root.resizable(False, False)
        width = 640
        height = 480
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y-50))

        # frames config
        self.MainPage = tk.Frame(self.root, height=height, width=width)
        self.PositionPage = tk.Frame(self.root, height=height, width=width)
        self.GCodePage = tk.Frame(self.root, height=height, width=width)

        self.MainPage.pack()

########################################################################

        ### MAIN PAGE WIDGETS ###

        # label to indicate main page
        self.label = tk.Label(self.MainPage, text="Main Page", bg='gray')
        self.label.place(width=130, height=25, x=20, y=10)

        # button to switch to position config screen
        self.position_page_button = tk.Button(
            self.MainPage,
            text="Configure Positions",
            command=self.switch_to_position_click
        )
        self.position_page_button.place(width=130, height=25, x=490, y=80)

        # button to switch to g-code generation screen
        self.gcode_page_button = tk.Button(
            self.MainPage,
            text="Generate G-Code",
            command=self.switch_to_gcode_click
        )
        self.gcode_page_button.place(width=130, height=25, x=490, y=120)

        # button to input '$$' in the terminal, open grbl configuration
        self.config_button = tk.Button(
            self.MainPage,
            text="GRBL Configuration",
            command=self.config_click
        )
        self.config_button.place(width=130, height=25, x=490, y=200)

        # 
        self.standard_settings_buttons = tk.Button(
            self.MainPage,
            text="Standard Settings",
            # command=self.config_click
        )
        self.standard_settings_buttons.place(width=130, height=25, x=490, y=240)

        # button to clear the terminal output
        self.clear_button = tk.Button(
            self.MainPage,
            text="Clear Output",
            command=self.output_clear
        )
        self.clear_button.place(width=130, height=25, x=490, y=280)

        # button to update the serial port
        self.update_ports_button = tk.Button(
            self.MainPage,
            text="Update ports",
            command=self.update_ports_click
        )
        self.update_ports_button.place(width=130, height=25, x=180, y=10)

        # dropdown button to select a serial
        self.port_list = ttk.Combobox(
            self.MainPage,
            state='readonly'
        )
        self.port_list.place(width=130, height=25, x=180, y=40)

        # dropdown button to select a baudrate
        self.baud_list = ttk.Combobox(
            self.MainPage,
            state='readonly'
        )
        self.baud_list.place(width=130, height=25, x=20, y=40)

        # button to connect to the selected serial port
        self.connect_button = tk.Button(
            self.MainPage,
            text="Connect",
            command=self.connect_click
        )
        self.connect_button.place(width=130, height=25, x=340, y=10)

        # button to disconnect the serial port
        self.disconnect_button = tk.Button(
            self.MainPage,
            text="Disconnect",
            command=self.disconnect_click
        )
        self.disconnect_button.place(width=130, height=25, x=340, y=40)

        # entry/input line to send data to the serial device
        self.input_line = tk.Entry(
            self.MainPage,
            bd=3
        )
        self.input_line.place(width=520, height=25, x=20, y=440)

        # button to send the text from the input line to the serial device
        self.input_button = tk.Button(
            self.MainPage,
            text="Enter",
        )
        self.input_button.place(width=70, height=25, x=550, y=439)
        self.input_button.bind('<Button-1>', self.input_click)

        # binds the return key to the method to send the data in the input line to the serial device
        self.root.bind('<Return>', self.input_click)

        # output screen to show received and sent data from the serial device
        self.output_screen = tk.Text(
            self.MainPage,
            state='disabled',
            bd=3
        )
        self.output_screen.place(width=450, height=360, x=20, y=70)

        # send the g-code file lines to the serial device
        self.send_gcode_button = tk.Button(
            self.MainPage,
            text="Send G-Code",
            command=self.send_gcode_click
        )
        self.send_gcode_button.place(width=130, height=25, x=490, y=400)

########################################################################

        ### POSITION PAGE WIDGETS ###

        # label to indicate position page
        self.label = tk.Label(
            self.PositionPage, text="Position Configuration", bg='gray')
        self.label.place(width=130, height=25, x=20, y=10)

        #
        self.pos_frame = tk.Frame(
            self.PositionPage, bg='gray', width=600, height=350)
        self.pos_frame.place(x=20, y=110)

        # button to clear the position screen output
        self.clear_button = tk.Button(
            self.PositionPage,
            text="Clear Output",
            command=self.pos_output_clear
        )
        self.clear_button.place(width=130, height=25, x=500, y=70)

        self.xplus_button = tk.Button(
            self.PositionPage,
            text="X+",
            command=lambda m="x plus": self.jog_controller_thread(m)
        )
        self.xplus_button.place(width=20, height=25, x=150, y=300)

        self.xminus_button = tk.Button(
            self.PositionPage,
            text="X-",
            command=lambda m="x minus": self.jog_controller_thread(m)
        )
        self.xminus_button.place(width=20, height=25, x=100, y=300)

        self.stop_jog_button = tk.Button(
            self.PositionPage,
            text="STOP",
            command=lambda m="stop": self.jog_controller_thread(m)
        )
        self.stop_jog_button.place(width=20, height=25, x=125, y=300)

        # button to go back to the main page
        self.back_to_main_button1 = tk.Button(
            self.PositionPage,
            text="Back to Main Page",
            command=self.position_to_main_click
        )
        self.back_to_main_button1.place(width=130, height=25, x=20, y=40)

        #
        self.register_position_button = tk.Button(
            self.PositionPage,
            text="OK",
            command=self.register_position_click
        )
        self.register_position_button.place(width=70, height=25, x=530, y=416)

        #
        self.reg_element_list = ttk.Combobox(
            self.PositionPage,
            state='readonly'
        )
        self.reg_element_list.place(width=130, height=25, x=340, y=10)
        elements_file = open("elements.txt", "r")
        elements = elements_file.readlines()
        self.reg_element_list['values'] = elements
        elements_file.close()

        #
        self.get_position_button = tk.Button(
            self.PositionPage,
            text="Get Position",
            command=self.get_element_values
        )
        self.get_position_button.place(width=130, height=25, x=340, y=40)

        #
        self.remove_element_button = tk.Button(
            self.PositionPage,
            text="Remove Element",
            command=self.remove_element
        )
        self.remove_element_button.place(width=130, height=25, x=340, y=70)

        #
        self.clear_elements_button = tk.Button(
            self.PositionPage,
            text="Clear Elements",
            command=self.clear_elements
        )
        self.clear_elements_button.place(width=130, height=25, x=500, y=40)

        #
        self.name_line = tk.Entry(
            self.PositionPage,
            bd=3
        )
        self.name_line.place(width=360, height=25, x=150, y=415)
        self.name_label = tk.Label(
            self.PositionPage, bg='gray', text="Element Name:")
        self.name_label.place(width=80, height=25, x=50, y=415)

        #
        self.position_screen = tk.Text(
            self.PositionPage,
            state='disabled',
            bd=3
        )
        self.position_screen.place(width=360, height=210, x=230, y=130)

        #
        self.element_list = ttk.Combobox(
            self.PositionPage,
            state='readonly'
        )
        elements = ['Vial Plate (96)', 'Becker']
        for element in elements:
            self.element_list['values'] = (*self.element_list['values'], element)
        self.element_list.place(width=130, height=25, x=65, y=130)
        self.element_list.current(newindex=0)

        #
        self.x_label = tk.Label(self.PositionPage, bg='gray', text="X:")
        self.x_label.place(width=20, height=25, x=50, y=170)
        self.x_position_line = tk.Entry(self.PositionPage, bd=3)
        self.x_position_line.place(width=130, height=25, x=80, y=170)

        #
        self.y_label = tk.Label(self.PositionPage, bg='gray', text="Y:")
        self.y_label.place(width=20, height=25, x=50, y=210)
        self.y_position_line = tk.Entry(self.PositionPage, bd=3)
        self.y_position_line.place(width=130, height=25, x=80, y=210)

        #
        self.z_label = tk.Label(self.PositionPage, bg='gray', text="Z:")
        self.z_label.place(width=20, height=25, x=50, y=250)
        self.z_position_line = tk.Entry(self.PositionPage, bd=3)
        self.z_position_line.place(width=130, height=25, x=80, y=250)

        #
        self.xf_label = tk.Label(self.PositionPage, bg='gray', text="Xf:")
        self.xf_label.place(width=20, height=25, x=50, y=290)
        self.xf_position_line = tk.Entry(self.PositionPage, bd=3)
        self.xf_position_line.place(width=130, height=25, x=80, y=290)

        #
        self.yf_label = tk.Label(self.PositionPage, bg='gray', text="Yf:")
        self.yf_label.place(width=20, height=25, x=50, y=330)
        self.yf_position_line = tk.Entry(self.PositionPage, bd=3)
        self.yf_position_line.place(width=130, height=25, x=80, y=330)

########################################################################

        ### G-CODE PAGE WIDGETS ###

        # label to indicate g-code page
        self.label = tk.Label(
            self.GCodePage, text="G-Code Generation", bg='gray')
        self.label.place(width=130, height=25, x=20, y=10)

        # button to go back to the main page
        self.back_to_main_button2 = tk.Button(
            self.GCodePage,
            text="Back to Main Page",
            command=self.gcode_to_main_click
        )
        self.back_to_main_button2.place(width=130, height=25, x=20, y=40)

        #
        self.gcode_line = tk.Entry(
            self.GCodePage,
            bd=3
        )
        self.gcode_line.place(width=460, height=25, x=20, y=440)

        # append g-code
        self.append_gcode_button = tk.Button(
            self.GCodePage,
            text="Append G-Code",
            command=self.append_gcode_click
        )
        self.append_gcode_button.place(width=130, height=25, x=490, y=439)

        #
        self.clear_gcode_button = tk.Button(
            self.GCodePage,
            text="Clear G-Code File",
            command=self.clear_gcode
        )
        self.clear_gcode_button.place(width=130, height=25, x=500, y=40)

        #
        self.reg_elements_gcode = ttk.Combobox(
            self.GCodePage,
            state='readonly'
        )
        self.reg_elements_gcode.place(width=130, height=25, x=340, y=10)
        elements_file = open("elements.txt", "r")
        elements = elements_file.readlines()
        self.reg_elements_gcode['values'] = elements
        elements_file.close()

        #
        self.action_list = ttk.Combobox(
            self.GCodePage,
            state='readonly'
        )
        elements = ['Fill Syringe', 'Fill Vials']
        for element in elements:
            self.action_list['values'] = (*self.action_list['values'], element)
        self.action_list.place(width=130, height=25, x=65, y=130)
        self.action_list.current(newindex=0)

        #
        self.confirm_action = tk.Button(
            self.GCodePage,
            text="OK",
            # command=self.confirm_action
        )
        self.confirm_action.place(width=70, height=25, x=210, y=130)

########################################################################

        ### SERIAL DEVICE CONFIGURATION ###

        # serial device startup
        self.serial = SerialClass()
        for baud in self.serial.baudratesDIC.keys():
            self.baud_list['values'] = (*self.baud_list['values'], baud)
        self.baud_list.set('115200')
        self.update_ports_click()

        self.start_disable_thread()

########################################################################

    ###DEBUG###

        self.check_threads_debug = tk.Button(
            self.MainPage,
            text="threads",
            command=self.print_threads
        )
        self.check_threads_debug.place(width=130, height=25, x=490, y=300)


        # runs the terminal
        self.root.mainloop()


    def print_threads(self):
        for thread in threading.enumerate():
            print(thread.name)

########################################################################

    ### MAIN PAGE METHODS ###

    def send_to_output(self, string):
        self.output_screen.config(state='normal')
        if (len(self.output_screen.get("1.0", "end-1c")) != 0):
            self.output_screen.insert(tk.END, '\n' + string)
        else:
            self.output_screen.insert(tk.END, string)
        self.output_screen.config(state='disabled')
        self.output_screen.see(tk.END)

    def update_output(self):
        self.stop_serial = False
        while (self.serial.serialPort.is_open):
            data = self.serial.serialPort.readline().decode("utf-8").strip()
            if (data == "Grbl 1.1h ['$' for help]"):
                self.stop_enable = True
            if (len(data) > 0):
                self.send_to_output(str(data))
            elif (self.stop_serial):
                break
        
    def output_clear(self):
        self.output_screen.config(state='normal')
        self.output_screen.delete(1.0, tk.END)
        self.output_screen.config(state='disabled')

    def connect_click(self):
        for widget in self.MainPage.winfo_children():
            widget.configure(state="disabled")
        self.send_to_output('Connecting...')
        port = self.port_list.get()
        baud = self.baud_list.get()
        self.serial.serialPort.port = port
        self.serial.serialPort.baudrate = baud
        error_message = self.serial.serial_connect()
        if (self.serial.serialPort.is_open):
            self.send_to_output('Connected')
            self.start_serial_thread()
        else:
            self.send_to_output(error_message)
            self.send_to_output('Could not connect')
            self.connect_button.config(state='normal')
        self.enable_thread = Thread(target=self.enable_buttons())
        self.enable_thread.daemon = True
        self.enable_thread.start()
        
    def enable_buttons(self):
        self.stop_enable = False
        while not self.stop_enable:
            continue
        for widget in self.MainPage.winfo_children():
            if (str(widget) != ".!frame.!button7"):
                widget.configure(state="normal")

    def disconnect_click(self):
        self.connect_button.config(state='normal')
        self.stop_serial = True
        self.serial.serial_disconnect()

    def input_click(self, event):
        if (len(self.input_line.get()) > 0 and self.input_line.get().isspace() == False):
            data = self.input_line.get()
            self.send_to_output(self.input_line.get())
            self.serial.serial_sendData(data)
        self.input_line.delete(0, tk.END)

    def config_click(self):
        self.send_to_output('$$')
        self.serial.serial_sendData('$$')

    def update_ports_click(self):
        self.serial.update_ports()
        self.port_list['values'] = []
        self.port_list.set('')
        for port in self.serial.portList:
            self.port_list['values'] = (*self.port_list['values'], port)
        if (len(self.port_list['values']) >= 1):
            self.port_list.current(newindex=0)

    def start_serial_thread(self):
        self.serial_thread = Thread(target=self.update_output)
        self.serial_thread.daemon = True
        self.serial_thread.start()

########################################################################

    ### POSITION PAGE METHODS ###

    def start_disable_thread(self):
        self.disable_thread = Thread(target=self.disable_extra_buttons)
        self.disable_thread.daemon = True
        self.disable_thread.start() 

    def disable_extra_buttons(self):
        while True:
            if (self.element_list.get() == "Becker"):
                self.xf_position_line.config(state='disabled')
                self.yf_position_line.config(state='disabled')
            else:
                self.xf_position_line.config(state='normal')
                self.yf_position_line.config(state='normal')

    def jog_controller_thread(self,button):
        # try:
        self.jog_thread = Thread(target=lambda: self.jog_increment(button))
        self.jog_thread.daemon = True
        self.jog_thread.start() 
        # except:
        #     self.send_to_pos_output('No devices connected')

    def jog_increment(self,button):
        arg = ''
        self.stop_jog_threads = False
        if (button == "x plus"):
            arg = "Y0.005"
        if (button == "x minus"):
            arg = "Y-0.005"
        if (button == "stop"):
            self.stop_jog_threads = True
        self.serial.serial_sendData("G91")
        while True:
            if (self.stop_jog_threads):
                break
            self.serial.serial_sendData(arg)
            sleep(0.1)

    def send_to_pos_output(self, string):
        self.position_screen.config(state='normal')
        if (len(self.position_screen.get("1.0", "end-1c")) != 0):
            self.position_screen.insert(tk.END, '\n' + string)
        else:
            self.position_screen.insert(tk.END, string)
        self.position_screen.config(state='disabled')
        self.position_screen.see(tk.END)

    def pos_output_clear(self):
        self.position_screen.config(state='normal')
        self.position_screen.delete(1.0, tk.END)
        self.position_screen.config(state='disabled')

    def start_sleep_thread(self):
        self.sleep_thread = Thread(target=self.invalid_position)
        self.sleep_thread.daemon = True
        self.sleep_thread.start()

    def invalid_position(self):
        self.x_position_line.delete(0, tk.END)
        self.y_position_line.delete(0, tk.END)
        self.z_position_line.delete(0, tk.END)
        self.x_position_line.insert(0, 'Invalid')
        self.y_position_line.insert(0, 'Invalid')
        self.z_position_line.insert(0, 'Invalid')
        self.x_position_line.config(state='disabled')
        self.y_position_line.config(state='disabled')
        self.z_position_line.config(state='disabled')
        sleep(2)
        self.x_position_line.config(state='normal')
        self.y_position_line.config(state='normal')
        self.z_position_line.config(state='normal')
        self.x_position_line.delete(0, tk.END)
        self.y_position_line.delete(0, tk.END)
        self.z_position_line.delete(0, tk.END)

    def update_reg_elements(self, element):
        elements_file = open("elements.txt", "a")
        elements_file.write(element)
        elements_file.close()
        elements_file = open("elements.txt", "r")
        elements = elements_file.readlines()
        self.reg_element_list['values'] = elements
        self.reg_elements_gcode['values'] = elements
        elements_file.close()

    def register_position_click(self):
        if (self.element_list.get() == 'Vial Plate (96)'):
            try:
                vp_config = []
                well_spacing_x = 9
                well_spacing_y = 9
                x_i = float(self.x_position_line.get())
                y_i = float(self.y_position_line.get())
                x_f = float(self.xf_position_line.get())
                y_f = float(self.yf_position_line.get())
                name = self.name_line.get()
                name_input = 'Vials: ' + name + '\n'
                vp_config.append(name_input)
                vp_config.append(self.z_position_line.get() + '\n')
                
                cos_alpha = (x_f - x_i)/(well_spacing_x*11)
                sin_alpha = (y_f - y_i)/(well_spacing_y*11)
                increment_x = (well_spacing_x * cos_alpha)
                increment_y = (well_spacing_y * sin_alpha)

                for j in range(1,9):
                    for i in range(1,13):
                        pos_x = x_i + (i-1)*(increment_x) + (j-1)*(increment_y)
                        pos_y = y_i + (i-1)*(increment_y) - (j-1)*(increment_x)
                        position = (str(pos_x) + ' ' + str(pos_y) + '\n')
                        vp_config.append(position)
                        
                positions_file = open("positions.txt", "a")
                positions_file.writelines(vp_config)
                positions_file.close()
                self.update_reg_elements(name_input)
                self.send_to_pos_output('Registered')
            except:
                self.start_sleep_thread()
                self.send_to_pos_output('Could not register')

        elif (self.element_list.get() == 'Becker'):
            try:
                x = self.x_position_line.get()
                y = self.y_position_line.get()
                name = self.name_line.get()
                name_input = 'Becker: ' + name + '\n'
                b_pos = []
                b_pos.append(name_input)
                b_pos.append(self.z_position_line.get() + '\n')
                pos = (str(x) + ' ' + str(y) + '\n')
                b_pos.append(pos)
                positions_file = open("positions.txt", "a")
                positions_file.writelines(b_pos)
                positions_file.close()
                self.update_reg_elements(name_input)
                self.send_to_pos_output('Registered')
            except:
                self.start_sleep_thread()
                self.send_to_pos_output('Could not register')

        self.name_line.delete(0, tk.END)
        self.x_position_line.delete(0, tk.END)
        self.y_position_line.delete(0, tk.END)
        self.xf_position_line.delete(0, tk.END)
        self.yf_position_line.delete(0, tk.END)
        self.z_position_line.delete(0, tk.END)

    def get_element_values(self):
        try:
            positions_file = open("positions.txt", "r")
            lines = positions_file.readlines()
            index = lines.index(self.reg_element_list.get())
            id_line = lines[index].split()
            if (id_line[0] == 'Vials:'):
                qnt = 98
            elif (id_line[0] == 'Becker:'):
                qnt = 3
            for i in range(index, index+qnt):
                line = lines[i].split()
                string = ''
                for element in line:
                    string = string + element + ' '
                self.send_to_pos_output(str(string))
        except:
            self.send_to_pos_output('Not registered')
        positions_file.close()

    def remove_element(self):
        try:
            positions_file = open("positions.txt", "r")
            lines = positions_file.readlines()
            index = lines.index(self.reg_element_list.get())
            id_line = lines[index].split()
            if (id_line[0] == 'Vials:'):
                qnt = 98
            elif (id_line[0] == 'Becker:'):
                qnt = 3
            del lines[index:index+qnt]
            positions_file = open("positions.txt", "w")
            positions_file.writelines(lines)
            positions_file.close()
            #
            elements_file = open("elements.txt", "r")
            e_lines = elements_file.readlines()
            e_index = e_lines.index(self.reg_element_list.get())
            del e_lines[e_index]
            elements_file = open("elements.txt", "w")
            e_lines = elements_file.writelines(e_lines)
            elements_file.close()
            #
            elements = list(self.reg_element_list['values'])
            elements.remove(self.reg_element_list.get())
            self.reg_element_list['values'] = elements
            self.reg_element_list.set('')
        except:
            self.send_to_pos_output('Could not remove element')

    def clear_elements(self):
        clear_str = []
        positions_file = open("positions.txt", "w")
        positions_file.writelines(clear_str)
        elements_file = open("elements.txt", "w")
        elements_file.writelines(clear_str)
        self.reg_element_list['values'] = clear_str
        self.reg_element_list.set('')
        positions_file.close()
        elements_file.close()

########################################################################

    ### G-CODE PAGE METHODS ###

    def append_gcode_click(self):
        if (len(self.gcode_line.get()) > 0 and self.gcode_line.get().isspace() == False):
            data = self.gcode_line.get()
            gcode = open("g-code.txt", "a")
            gcode.write('\n' + str(data))
        self.gcode_line.delete(0, tk.END)
        gcode.close()

    def send_gcode_click(self):
        gcode = open("g-code.txt", "r")
        for line in gcode.readlines():
            if (len(line) > 0 and line.isspace() == False):
                self.send_to_output(line)

                self.serial.serial_sendData(line)
        gcode.close()

    def clear_gcode(self):
        clear_str = []
        gcode_file = open("g-code.txt", "w")
        gcode_file.writelines(clear_str)
        gcode_file.close()

########################################################################

    ### SWITCH BETWEEN PAGES ###

    def switch_to_position_click(self):
        self.MainPage.pack_forget()
        self.PositionPage.pack()

    def switch_to_gcode_click(self):
        self.MainPage.pack_forget()
        self.GCodePage.pack()

    def position_to_main_click(self):
        self.PositionPage.pack_forget()
        self.MainPage.pack()

    def gcode_to_main_click(self):
        self.GCodePage.pack_forget()
        self.MainPage.pack()

########################################################################

if __name__ == "__main__":
    terminalObj = Terminal()
