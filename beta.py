from tkinter import *
import requests
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from config import *
from tkinter.ttk import Combobox
import re

def decode_license(license_key):
    odd_chars = license_key[1::2]  # Even indexed characters
    even_chars = license_key[0::2]  # Odd indexed characters
    return odd_chars + even_chars

def check_license():
    entered_license = entry.get()
    decoded_license = decode_license(entered_license)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        decoded_keys = response.text.splitlines()
        
        if decoded_license in decoded_keys:
            result_label.config(text="License is valid!", fg="green")
            rootX.destroy()  # Close the current window
            start_second_app()  # Start the second app if the license is valid
        else:
            result_label.config(text="License is invalid.", fg="red")
    except requests.RequestException as e:
        result_label.config(text="Error fetching license data.", fg="red")

# URL for the decoded keys
url = "https://raw.githubusercontent.com/MuOssama/pr/main/marlin"

def start_second_app():
    def select_file():
        global file_selected  # Declare the variable as global
        file_path = filedialog.askopenfilename(filetypes=[("Header files", "*.h"), ("All files", "*.*")])
        if file_path:
            read_file(file_path)
            file_selected = True  # Set the flag to True when a file is selected


    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                global content
                content = file.read()
                messagebox.showinfo("File Content", f"File {file_path} content:\n\n{content}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
        


    def save_file():
        global content
        #add delay for lcd to prevent flickering 
        if (not line_exists("#define ST7920_DELAY_1")) or (not line_exists("#define ST7920_DELAY_2"))  or (not line_exists("#define ST7920_DELAY_3")):
            modify_configuration_file("// @section info", "// @section info\n\n/*delay for LCD*/\n#define ST7920_DELAY_1 DELAY_NS(200) // After CLK LOW\n#define ST7920_DELAY_2 DELAY_NS(400) // After DAT\n#define ST7920_DELAY_3 DELAY_NS(200) // After CLK HIGH")

        file_path = filedialog.asksaveasfilename(defaultextension=".h", initialfile="Configuration.h", filetypes=[("Header files", "*.h"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(content)
                    messagebox.showinfo("Success", f"File saved successfully at {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def modify_configuration_file(old_prefix, new_line):
        global content
        lines = content.splitlines()
        modified_lines = []
        for line in lines:
            if line.strip().startswith(old_prefix):
                if new_line:
                    modified_lines.append(new_line)
            else:
                modified_lines.append(line)
        content = "\n".join(modified_lines)

        
    def line_exists(line_to_check, portions=2):
        global content
        # Normalize the line to check by stripping whitespace
        normalized_line = line_to_check.strip()
        # Split the line into parts
        line_parts = normalized_line.split()
        
        # Check if there are enough parts to compare
        if len(line_parts) < portions:
            return False
        
        # Create a set of the portions to check
        portions_to_check = set(line_parts[:portions])
        
        # Check if any line in the content has the required portions
        for line in content.splitlines():
            line_parts_in_content = line.strip().split()
            if len(line_parts_in_content) >= portions and set(line_parts_in_content[:portions]) == portions_to_check:
                return True
        
        return False

        
        
    def prefill_input_fields():
        global content
        
        # Extract the 3D printer name
        author_match = re.search(r'#define STRING_CONFIG_H_AUTHOR "(.*?)"', content)
        if author_match:
            name_entry.delete(0, END)
            name_entry.insert(0, author_match.group(1))
            
        # Extract the motherboard
        motherboard_match = re.search(r'#define MOTHERBOARD (.+)', content)
        if motherboard_match:
            motherboard_entry.delete(0, END)
            motherboard_entry.insert(0, motherboard_match.group(1).strip())

        # Extract driver types
        driver_names = ["X_DRIVER_TYPE", "Y_DRIVER_TYPE", "Z_DRIVER_TYPE", "E0_DRIVER_TYPE"]
        for driver in driver_names:
            match = re.search(rf'#define {driver} (.+)', content)
            if match:
                driver_value = match.group(1).strip()
                if driver == "X_DRIVER_TYPE":
                    x_driver_var.set(driver_value)
                elif driver == "Y_DRIVER_TYPE":
                    y_driver_var.set(driver_value)
                elif driver == "Z_DRIVER_TYPE":
                    z_driver_var.set(driver_value)
                elif driver == "E0_DRIVER_TYPE":
                    e0_driver_var.set(driver_value)

        # Extract temperature sensors
        nozzle_temp_match = re.search(r'#define TEMP_SENSOR_0 (.*?)(?:\s|//)', content)
        if nozzle_temp_match:
            nozzle_temp_entry.delete(0, END)
            nozzle_temp_entry.insert(0, nozzle_temp_match.group(1))

        bed_temp_match = re.search(r'#define TEMP_SENSOR_BED (.*?)(?:\s|//)', content)
        if bed_temp_match:
            bed_temp_entry.delete(0, END)
            bed_temp_entry.insert(0, bed_temp_match.group(1))


        # Extract endstop inversion values
        endstop_names = [
            "X_MIN_ENDSTOP_INVERTING", "Y_MIN_ENDSTOP_INVERTING", "Z_MIN_ENDSTOP_INVERTING",
            "X_MAX_ENDSTOP_INVERTING", "Y_MAX_ENDSTOP_INVERTING", "Z_MAX_ENDSTOP_INVERTING"
        ]
        
        for endstop in endstop_names:
            match = re.search(rf'#define {endstop} (\S+)', content)
            if match:
                value = match.group(1).strip().lower()  # Convert to lowercase for comparison..
                if endstop == "X_MIN_ENDSTOP_INVERTING":
                    x_endstop_var.set(value)  # Set the variable directly           
                elif endstop == "Y_MIN_ENDSTOP_INVERTING":
                    y_endstop_var.set(value)
                elif endstop == "Z_MIN_ENDSTOP_INVERTING":
                    z_endstop_var.set(value)
                elif endstop == "X_MAX_ENDSTOP_INVERTING":
                    # You can create and handle a variable for X_MAX if needed
                    pass
                elif endstop == "Y_MAX_ENDSTOP_INVERTING":
                    # Create and handle a variable for Y_MAX if needed
                    pass
                elif endstop == "Z_MAX_ENDSTOP_INVERTING":
                    # Create and handle a variable for Z_MAX if needed
                    pass


        # Extract motor inversion values
        motor_inversion_names = ["INVERT_X_DIR", "INVERT_Y_DIR", "INVERT_Z_DIR"]
        for motor_inv in motor_inversion_names:
            match = re.search(rf'#define {motor_inv} (.+)', content)
            if match:
                value = match.group(1).strip()
                if motor_inv == "INVERT_X_DIR":
                    x_motor_inv_var.set(value)
                elif motor_inv == "INVERT_Y_DIR":
                    y_motor_inv_var.set(value)
                elif motor_inv == "INVERT_Z_DIR":
                    z_motor_inv_var.set(value)

        # Extract home direction values
        home_direction_names = ["X_HOME_DIR", "Y_HOME_DIR", "Z_HOME_DIR"]
        for home_dir in home_direction_names:
            match = re.search(rf'#define {home_dir} (.+)', content)
            if match:
                value = match.group(1).strip()
                if home_dir == "X_HOME_DIR":
                    x_home_direction_var.set("min" if value == "-1" else "max")
                elif home_dir == "Y_HOME_DIR":
                    y_home_direction_var.set("min" if value == "-1" else "max")
                elif home_dir == "Z_HOME_DIR":
                    z_home_direction_var.set("min" if value == "-1" else "max")

                    
        # Extract printer volume values
        printer_size_names = ["X_BED_SIZE", "Y_BED_SIZE", "Z_MAX_POS"]
        for printer_size in printer_size_names:
            match = re.search(rf'#define {printer_size} (.+)', content)
            if match:
                value = match.group(1).strip()
                if printer_size == "X_BED_SIZE":
                    x_bed_size_entry.delete(0, END)
                    x_bed_size_entry.insert(0, match.group(1))
                elif printer_size == "Y_BED_SIZE":
                    y_bed_size_entry.delete(0, END)
                    y_bed_size_entry.insert(0, match.group(1))
                elif printer_size == "Z_MAX_POS":
                    z_max_height_entry.delete(0, END)
                    z_max_height_entry.insert(0, match.group(1))
                    
        # Extract LCD configuration
        lcd_options = [
            "NONE",
            "REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER",
            "REPRAP_DISCOUNT_SMART_CONTROLLER",
            "REPRAPWORLD_GRAPHICAL_LCD",
            "MKS_MINI_12864",
            "MKS_MINI_12864_V3",
            "MKS_TS35_V2_0",
            "MKS_ROBIN_TFT24",
            "MKS_ROBIN_TFT28",
            "MKS_ROBIN_TFT32",
            "MKS_ROBIN_TFT35",
            "MKS_ROBIN_TFT43"
        ]
        
        for option in lcd_options:
            if re.search(rf'#define {option}', content):
                lcd_combobox.set(option)  # Set the combobox to the found option
                break  # Exit once the first match is found


      # Extract probe configuration
        if re.search(r'^\s*#define\s+BLTOUCH\s*$', content, re.MULTILINE):
                probe_combobox.current(1)  # Set the combobox to the found probe type
        else:
                probe_combobox.set("Not recognised")  # Set the combobox to the found probe type

        # Extract probing points
        probing_points_match = re.search(r'#define GRID_MAX_POINTS_X (\d+)', content)
        if probing_points_match:
            probing_points_entry.config(state="normal")  # Enable entry if points are found
            probing_points_entry.delete(0, END)
            probing_points_entry.insert(0, probing_points_match.group(1))
        else:
            probing_points_entry.config(state="disabled")  # Disable entry if no points are found

        # Additional configurations based on selected probe type
        if probe_combobox.get() == "BlTouch":
            z_endstop_match = re.search(r'#define Z_MIN_ENDSTOP_INVERTING (.+)', content)
            if z_endstop_match:
                z_endstop_value = z_endstop_match.group(1).strip().lower()
                z_endstop_var.set(z_endstop_value)
                if z_endstop_value == "true":
                    z_endstop_true.select()
                else:
                    z_endstop_false.select()

        # Update UI based on selected probe
        on_probe_select(None)  # Trigger the selection function to update UI state
        
        
                
    def update_all_inputs():
        # Call functions to get the inputs
        get_name_input()
        get_motherboard_input()
        get_driver_inputs()
        get_temp_sensor_inputs()
        get_endstop_inputs()
        get_motor_inversion_inputs()
        get_probing_points_input()  # Call your probing points function
        get_printer_size_inputs()
        get_lcd_input()
        validate_z_endstop_change()
        get_home_direction_inputs()
        # Schedule the next update
        root.after(1000, update_all_inputs)


    def on_probe_select(event):
        selected_probe = probe_combobox.get()
        if selected_probe == "BlTouch":
            modify_configuration_file("//#define BLTOUCH", "#define BLTOUCH")
            modify_configuration_file("//#define AUTO_BED_LEVELING_BILINEAR", "#define AUTO_BED_LEVELING_BILINEAR")
            modify_configuration_file("//#define Z_SAFE_HOMING", "#define Z_SAFE_HOMING")
            modify_configuration_file("#define Z_MIN_PROBE_ENDSTOP_INVERTING true", "#define Z_MIN_PROBE_ENDSTOP_INVERTING false")
            modify_configuration_file("##define Z_MIN_ENDSTOP_INVERTING", "#define Z_MIN_ENDSTOP_INVERTING false")
            modify_configuration_file("//#define Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN", "#define Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN")
            modify_configuration_file("//#define LCD_BED_LEVELING", "#define LCD_BED_LEVELING")
            print(selected_probe)

            # Enable probing points entry
            probing_points_entry.config(state="normal")

            # Set Z MIN endstop radiobutton to False
            z_endstop_var.set("False")
            z_endstop_false.select()
            
        elif selected_probe == "Capacitive" or selected_probe == "Inductive":
            modify_configuration_file(f"#define {selected_probe}", "//#define {selected_probe}")

            # Enable probing points entry
            probing_points_entry.config(state="normal")
            
        elif selected_probe == "Z Endstop (Mesh bed leveling)":
            modify_configuration_file(f"#define {selected_probe}", "//#define {selected_probe}")

            # Enable probing points entry
            probing_points_entry.config(state="normal")

            
        elif selected_probe == "NONE":
            # Disable probing points entry
            probing_points_entry.config(state="disabled")
            probing_points_entry.delete(0, END)  # Clear the entry if disabled

    def validate_z_endstop_change():
        if probe_combobox.get() == "BlTouch" and z_endstop_var.get() == "True":
            messagebox.showerror("Error", "You cannot make Z MIN Endstop True while using BLTouch.")
            z_endstop_var.set("False")  # Reset to False if invalid change is attempted
            z_endstop_false.select()

    def get_probing_points_input():
        probing_points = probing_points_entry.get()
        modify_configuration_file("#define GRID_MAX_POINTS_X", f"  #define GRID_MAX_POINTS_X {probing_points}")


    def get_name_input():
        name = name_entry.get()
        modify_configuration_file("""#define STRING_CONFIG_H_AUTHOR""", f"""#define STRING_CONFIG_H_AUTHOR "{name}" """)

    def get_motherboard_input():
        motherboard = motherboard_entry.get()
        modify_configuration_file("#define MOTHERBOARD", f"#define MOTHERBOARD {motherboard}")


    def get_driver_inputs():
        x_driver = x_driver_var.get()
        y_driver = y_driver_var.get()
        z_driver = z_driver_var.get()
        e0_driver = e0_driver_var.get()
        modify_configuration_file("#define X_DRIVER_TYPE", f"#define X_DRIVER_TYPE {x_driver}")
        modify_configuration_file("#define Y_DRIVER_TYPE", f"#define Y_DRIVER_TYPE {y_driver}")
        modify_configuration_file("#define Z_DRIVER_TYPE", f"#define Z_DRIVER_TYPE {z_driver}")
        modify_configuration_file("#define E0_DRIVER_TYPE", f"#define E0_DRIVER_TYPE {e0_driver}")
        
        
    def get_temp_sensor_inputs():
        nozzle_temp = nozzle_temp_entry.get()
        bed_temp = bed_temp_entry.get()
        modify_configuration_file("#define TEMP_SENSOR_0", f"#define TEMP_SENSOR_0 {nozzle_temp}")
        modify_configuration_file("#define TEMP_SENSOR_BED", f"#define TEMP_SENSOR_BED {bed_temp}")

    def get_endstop_inputs():
        x_endstop = x_endstop_var.get()
        y_endstop = y_endstop_var.get()
        z_endstop = z_endstop_var.get()
        modify_configuration_file("#define X_MIN_ENDSTOP_INVERTING", f"#define X_MIN_ENDSTOP_INVERTING {x_endstop}")
        modify_configuration_file("#define Y_MIN_ENDSTOP_INVERTING", f"#define Y_MIN_ENDSTOP_INVERTING {y_endstop}")
        modify_configuration_file("#define Z_MIN_ENDSTOP_INVERTING", f"#define Z_MIN_ENDSTOP_INVERTING {z_endstop}")

    # Function to get motor inversion inputs
    def get_motor_inversion_inputs():
        x_motor_inv = x_motor_inv_var.get()
        y_motor_inv = y_motor_inv_var.get()
        z_motor_inv = z_motor_inv_var.get()
        modify_configuration_file("#define INVERT_X_DIR", f"#define INVERT_X_DIR {x_motor_inv}")
        modify_configuration_file("#define INVERT_Y_DIR", f"#define INVERT_Y_DIR {y_motor_inv}")
        modify_configuration_file("#define INVERT_Z_DIR", f"#define INVERT_Z_DIR {z_motor_inv}")


    # Function to get LCD input
    def get_lcd_input():
        lcd_option = lcd_combobox.get()
        modify_configuration_file("//#define SDSUPPORT", "#define SDSUPPORT")
        modify_configuration_file("//#define INDIVIDUAL_AXIS_HOMING_MENU", "#define INDIVIDUAL_AXIS_HOMING_MENU")
        modify_configuration_file("//#define INDIVIDUAL_AXIS_HOMING_SUBMENU", "#define INDIVIDUAL_AXIS_HOMING_SUBMENU")

        if lcd_option == "NONE":
            pass
        elif lcd_option == "REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER":
            modify_configuration_file("//#define REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER", "#define REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER")
        elif lcd_option == "REPRAP_DISCOUNT_SMART_CONTROLLER":
            modify_configuration_file("//#define REPRAP_DISCOUNT_SMART_CONTROLLER", "#define REPRAP_DISCOUNT_SMART_CONTROLLER")
        elif lcd_option == "REPRAPWORLD_GRAPHICAL_LCD":
            modify_configuration_file("//#define REPRAPWORLD_GRAPHICAL_LCD", "#define REPRAPWORLD_GRAPHICAL_LCD")
        elif lcd_option == "MKS_MINI_12864":
            modify_configuration_file("//#define MKS_MINI_12864", "#define MKS_MINI_12864")
        elif lcd_option == "MKS_MINI_12864_V3":
            modify_configuration_file("//#define MKS_MINI_12864_V3", "#define MKS_MINI_12864_V3")
        elif lcd_option == "MKS_TS35_V2_0":
            modify_configuration_file("//#define MKS_TS35_V2_0", "#define MKS_TS35_V2_0")
        elif lcd_option == "MKS_ROBIN_TFT24":
            modify_configuration_file("//#define MKS_ROBIN_TFT24", "#define MKS_ROBIN_TFT24")
        elif lcd_option == "MKS_ROBIN_TFT28":
            modify_configuration_file("//#define MKS_ROBIN_TFT28", "#define MKS_ROBIN_TFT28")
        elif lcd_option == "MKS_ROBIN_TFT32":
            modify_configuration_file("//#define MKS_ROBIN_TFT32", "#define MKS_ROBIN_TFT32")
        elif lcd_option == "MKS_ROBIN_TFT35":
            modify_configuration_file("//#define MKS_ROBIN_TFT35", "#define MKS_ROBIN_TFT35")
        elif lcd_option == "MKS_ROBIN_TFT43":
            modify_configuration_file("//#define MKS_ROBIN_TFT43", "#define MKS_ROBIN_TFT43")

        
    # Function to get printer dimensions
    def get_printer_size_inputs():
        x_bed_size = x_bed_size_entry.get()
        y_bed_size = y_bed_size_entry.get()
        z_max_height = z_max_height_entry.get()
        modify_configuration_file("#define X_BED_SIZE", f"#define X_BED_SIZE {x_bed_size}")
        modify_configuration_file("#define Y_BED_SIZE", f"#define Y_BED_SIZE {y_bed_size}")
        modify_configuration_file("#define Z_MAX_POS", f"#define Z_MAX_POS {z_max_height}")

        
    def get_home_direction_inputs():
        x_home_direction = x_home_direction_var.get()
        y_home_direction = y_home_direction_var.get()
        z_home_direction = z_home_direction_var.get()
        if x_home_direction == 'min':
            modify_configuration_file("#define X_HOME_DIR", "#define X_HOME_DIR -1")
        else:
            modify_configuration_file("#define X_HOME_DIR", "#define X_HOME_DIR 1")

        if y_home_direction == 'min':
            modify_configuration_file("#define Y_HOME_DIR", "#define Y_HOME_DIR -1")
        else:
            modify_configuration_file("#define Y_HOME_DIR", "#define Y_HOME_DIR 1")

        if z_home_direction == 'min':
            modify_configuration_file("#define Z_HOME_DIR", "#define Z_HOME_DIR -1")
        else:
            modify_configuration_file("#define Z_HOME_DIR", "#define Z_HOME_DIR 1")

        
        
        
        
        
        
        
        
        
        
        
        
        
    # Global variable    
    file_selected = False
    content = ""
    offsetIncL = 0
    offsetIncM = 3
    offsetIncR = 0

    root = Tk()
    select_file()

    root.title("Marlin Configrator")
    root.geometry(f"{screenWidth}x{screenHeight}")
    root.resizable(False, False)  # Prevent resizing

    # Add logo
    logo_image = Image.open("RD3D.png")
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = Label(root, image=logo_photo)
    logo_label.place(x=0, y=0)




    """##################################"""
    """##################################"""
    """######                      ######"""
    """######     Left screen      ######"""
    """######                      ######"""
    """##################################"""
    """##################################"""


    # File operations buttons
    select_button = Button(root, text="Select File", command=select_file)
    select_button.place(x=0, y=0, width=100, height=40)

    save_button = Button(root, text="Save File", command=save_file, bg="light green")
    save_button.place(x=objectWidth, y=0, width=100, height=40)
    offsetIncL += 1

    # Name input field
    name_label = Label(root, text="3D printer name:")
    name_label.place(x=0, y=offsetIncL * 50)
    name_entry = Entry(root)
    name_entry.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    # Motherboard input
    motherboard_label = Label(root, text="Motherboard:")
    motherboard_label.place(x=0, y=offsetIncL * 50)
    motherboard_entry = Entry(root)
    motherboard_entry.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1


    # Driver inputs
    # List of driver options
    driver_options = [
        'A4988', 'A5984', 'DRV8825', 'LV8729', 'L6470', 'L6474', 
        'POWERSTEP01', 'TB6560', 'TB6600', 'TMC2100', 'TMC2130', 
        'TMC2130_STANDALONE', 'TMC2160', 'TMC2160_STANDALONE', 
        'TMC2208', 'TMC2208_STANDALONE', 'TMC2209', 'TMC2209_STANDALONE', 
        'TMC26X', 'TMC26X_STANDALONE', 'TMC2660', 'TMC2660_STANDALONE', 
        'TMC5130', 'TMC5130_STANDALONE', 'TMC5160', 'TMC5160_STANDALONE']

    # Driver inputs
    x_driver_label = Label(root, text="X Driver:")
    x_driver_label.place(x=0, y=offsetIncL * 50)
    x_driver_var = StringVar()
    x_driver_dropdown = ttk.Combobox(root, textvariable=x_driver_var, values=driver_options)
    x_driver_dropdown.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    y_driver_label = Label(root, text="Y Driver:")
    y_driver_label.place(x=0, y=offsetIncL * 50)
    y_driver_var = StringVar()
    y_driver_dropdown = ttk.Combobox(root, textvariable=y_driver_var, values=driver_options)
    y_driver_dropdown.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    z_driver_label = Label(root, text="Z Driver:")
    z_driver_label.place(x=0, y=offsetIncL * 50)
    z_driver_var = StringVar()
    z_driver_dropdown = ttk.Combobox(root, textvariable=z_driver_var, values=driver_options)
    z_driver_dropdown.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    e0_driver_label = Label(root, text="E0 Driver:")
    e0_driver_label.place(x=0, y=offsetIncL * 50)
    e0_driver_var = StringVar()
    e0_driver_dropdown = ttk.Combobox(root, textvariable=e0_driver_var, values=driver_options)
    e0_driver_dropdown.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1




    # Endstop Inverting
    x_endstop_label = Label(root, text="X MIN Endstop Inverting:")
    x_endstop_label.place(x=0, y=offsetIncL * 50)
    x_endstop_var = StringVar(value="false")
    x_endstop_true = Radiobutton(root, text="true", variable=x_endstop_var, value="true")
    x_endstop_true.place(x=200, y=offsetIncL * 50)
    x_endstop_false = Radiobutton(root, text="false", variable=x_endstop_var, value="false")
    x_endstop_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1

    y_endstop_label = Label(root, text="Y MIN Endstop Inverting:")
    y_endstop_label.place(x=0, y=offsetIncL * 50)
    y_endstop_var = StringVar(value="false")
    y_endstop_true = Radiobutton(root, text="true", variable=y_endstop_var, value="true")
    y_endstop_true.place(x=200, y=offsetIncL * 50)
    y_endstop_false = Radiobutton(root, text="false", variable=y_endstop_var, value="false")
    y_endstop_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1

    z_endstop_label = Label(root, text="Z MIN Endstop Inverting:")
    z_endstop_label.place(x=0, y=offsetIncL * 50)
    z_endstop_var = StringVar(value="false")
    z_endstop_true = Radiobutton(root, text="true", variable=z_endstop_var, value="true", command=validate_z_endstop_change)
    z_endstop_true.place(x=200, y=offsetIncL * 50)
    z_endstop_false = Radiobutton(root, text="false", variable=z_endstop_var, value="false", command=validate_z_endstop_change)
    z_endstop_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1

    # Temperature sensors
    nozzle_temp_label = Label(root, text="Nozzle Temperature Sensor:")
    nozzle_temp_label.place(x=0, y=offsetIncL * 50)
    nozzle_temp_entry = Entry(root)
    nozzle_temp_entry.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    bed_temp_label = Label(root, text="Bed Temperature Sensor:")
    bed_temp_label.place(x=0, y=offsetIncL * 50)
    bed_temp_entry = Entry(root)
    bed_temp_entry.place(x=200, y=offsetIncL * 50, width=objectWidth)
    offsetIncL += 1

    # Motor Inversion Variables
    x_motor_inv_var = StringVar(value="false")
    y_motor_inv_var = StringVar(value="false")
    z_motor_inv_var = StringVar(value="false")

    # X Motor Inversion
    x_motor_inv_label = Label(root, text="X Motor Inversion:")
    x_motor_inv_label.place(x=0, y=offsetIncL * 50)
    x_motor_inv_true = Radiobutton(root, text="true", variable=x_motor_inv_var, value="true")
    x_motor_inv_true.place(x=200, y=offsetIncL * 50)
    x_motor_inv_false = Radiobutton(root, text="false", variable=x_motor_inv_var, value="false")
    x_motor_inv_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1

    # Y Motor Inversion
    y_motor_inv_label = Label(root, text="Y Motor Inversion:")
    y_motor_inv_label.place(x=0, y=offsetIncL * 50)
    y_motor_inv_true = Radiobutton(root, text="true", variable=y_motor_inv_var, value="true")
    y_motor_inv_true.place(x=200, y=offsetIncL * 50)
    y_motor_inv_false = Radiobutton(root, text="false", variable=y_motor_inv_var, value="false")
    y_motor_inv_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1

    # Z Motor Inversion
    z_motor_inv_label = Label(root, text="Z Motor Inversion:")
    z_motor_inv_label.place(x=0, y=offsetIncL * 50)
    z_motor_inv_true = Radiobutton(root, text="true", variable=z_motor_inv_var, value="true")
    z_motor_inv_true.place(x=200, y=offsetIncL * 50)
    z_motor_inv_false = Radiobutton(root, text="false", variable=z_motor_inv_var, value="false")
    z_motor_inv_false.place(x=260, y=offsetIncL * 50)
    offsetIncL += 1


    """##################################"""
    """##################################"""
    """######                      ######"""
    """######     Middle screen    ######"""
    """######                      ######"""
    """##################################"""
    """##################################"""

    x_axis_middle1 =(screenWidth/2)-110
    x_axis_middle2 =(screenWidth/2)-10



    # Printer dimensions title
    printer_label = Label(root, text="Printer Dimensions:",bg="cyan")
    printer_label.place(x=(screenWidth/2)-50, y=offsetIncM * 50)
    offsetIncM += 1

    # X bed size
    x_bed_size_label = Label(root, text="X Bed Size:")
    x_bed_size_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    x_bed_size_entry = Entry(root)
    x_bed_size_entry.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth/2)
    x_bed_dim_label = Label(root, text="mm")
    x_bed_dim_label.place(x=(screenWidth/2)+90, y=offsetIncM * 50)
    offsetIncM += 1

    # Y bed size
    y_bed_size_label = Label(root, text="Y Bed Size:")
    y_bed_size_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    y_bed_size_entry = Entry(root)
    y_bed_size_entry.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth/2)
    y_bed_dim_label = Label(root, text="mm")
    y_bed_dim_label.place(x=(screenWidth/2)+90, y=offsetIncM * 50)
    offsetIncM += 1

    # Z max height
    z_max_height_label = Label(root, text="Z Max Height:")
    z_max_height_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    z_max_height_entry = Entry(root)
    z_max_height_entry.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth/2)
    z_bed_dim_label = Label(root, text="mm")
    z_bed_dim_label.place(x=(screenWidth/2)+90, y=offsetIncM * 50)
    offsetIncM += 1

    # Probe selection
    probe_var = BooleanVar()
    probe_label = Label(root, text="Leveling :")
    probe_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    probe_combobox = Combobox(root, values=["NONE", "BlTouch", "Capacitive", "Inductive", "Z Endstop (Mesh bed leveling)"], state="readonly")
    probe_combobox.current(0)  # Set default selection to "NONE"
    probe_combobox.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth+50)
    probe_combobox.bind("<<ComboboxSelected>>", on_probe_select)
    offsetIncM += 1

    # Probing Points Entry
    probing_points_label = Label(root, text="Probing Points:")
    probing_points_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    probing_points_entry = Entry(root)
    probing_points_entry.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth/2)
    probing_points_entry.config(state="disabled") # Initialize probing points entry to be disabled
    offsetIncM += 1


    # LCD screen options
    lcd_label = Label(root, text="LCD Screen:")
    lcd_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    lcd_options = [
        "NONE",
        "REPRAP_DISCOUNT_FULL_GRAPHIC_SMART_CONTROLLER",
        "REPRAP_DISCOUNT_SMART_CONTROLLER",
        "REPRAPWORLD_GRAPHICAL_LCD",
        "MKS_MINI_12864",
        "MKS_MINI_12864_V3",
        "MKS_TS35_V2_0",
        "MKS_ROBIN_TFT24",
        "MKS_ROBIN_TFT28",
        "MKS_ROBIN_TFT32",
        "MKS_ROBIN_TFT35",
        "MKS_ROBIN_TFT43"
    ]
    lcd_combobox = Combobox(root, values=lcd_options, state="readonly")
    lcd_combobox.current(0)  # Set default selection
    lcd_combobox.place(x=x_axis_middle2, y=offsetIncM * 50, width=objectWidth+50)
    offsetIncM += 1


    # Home Direction Selection
    x_home_label = Label(root, text="X Home Direction:")
    x_home_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    x_home_direction_var = StringVar(value="min")
    x_home_min = Radiobutton(root, text="Min", variable=x_home_direction_var, value="min")
    x_home_min.place(x=x_axis_middle2 + 40, y=offsetIncM * 50)
    x_home_max = Radiobutton(root, text="Max", variable=x_home_direction_var, value="max")
    x_home_max.place(x=x_axis_middle2 + 100, y=offsetIncM * 50)
    offsetIncM += 1

    # Y Home Direction
    y_home_label = Label(root, text="Y Home Direction:")
    y_home_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    y_home_direction_var = StringVar(value="min")
    y_home_min = Radiobutton(root, text="Min", variable=y_home_direction_var, value="min")
    y_home_min.place(x=x_axis_middle2 + 40, y=offsetIncM * 50)
    y_home_max = Radiobutton(root, text="Max", variable=y_home_direction_var, value="max")
    y_home_max.place(x=x_axis_middle2 + 100, y=offsetIncM * 50)
    offsetIncM += 1

    # Z Home Direction
    z_home_label = Label(root, text="Z Home Direction:")
    z_home_label.place(x=x_axis_middle1, y=offsetIncM * 50)
    z_home_direction_var = StringVar(value="min")
    z_home_min = Radiobutton(root, text="Min", variable=z_home_direction_var, value="min")
    z_home_min.place(x=x_axis_middle2 + 40, y=offsetIncM * 50)
    z_home_max = Radiobutton(root, text="Max", variable=z_home_direction_var, value="max")
    z_home_max.place(x=x_axis_middle2 + 100, y=offsetIncM * 50)
    offsetIncM += 1




    """##################################"""
    """##################################"""
    """######                      ######"""
    """######     Right screen     ######"""
    """######                      ######"""
    """##################################"""
    """##################################"""

    x_axis_right =screenWidth - 270

    prefill_input_fields()

    # Start the periodic updates
    update_all_inputs()  # Call it once to kick off the process

    root.mainloop()


# First app named "Validation"
rootX = Tk()
rootX.title("Validation")

# Create and place the input field and button
entry_label = Label(rootX, text="Enter License Key:")
entry_label.pack(pady=5)

entry = Entry(rootX)
entry.pack(pady=5)

check_button = Button(rootX, text="Check License", command=check_license)
check_button.pack(pady=10)

result_label = Label(rootX, text="")
result_label.pack(pady=10)

rootX.mainloop()
