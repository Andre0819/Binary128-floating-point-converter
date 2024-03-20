import tkinter as tk
import decimal
import sys
sys.set_int_max_str_digits(5000)
decimal.getcontext().prec = 112
Decimal = decimal.Decimal

# Main Convert Logic
def convert():
    clear_output()
    sign_bit = "0"
    # Get the selected conversion type 
    selected_conversion_type = conversion_type.get()
    
    # Get the float input from the entry widget
    if selected_conversion_type == "Binary":
        binary_input = str(input_mantissa_dec.get())

        if binary_input[0] == "-":
            sign_bit = "1"
            binary_input = binary_input[1:]

        if not all(bit in '01.' for bit in binary_input) or binary_input.count('.') > 1: 
            error_message.config(text="Error: Invalid binary input.")
            return 0
         # Get the exponent integer input from the entry widget
        try:
            exponent_input = int(exp_input.get())
        except ValueError:
            error_message.config(text="Error: Invalid exponent input. Must be integer.")
            return 0
        mantissa, exponent = normalize_binary(binary_input, exponent_input)
        mantissa = limit_mantissa(mantissa)
        print("normalized: ", mantissa, exponent)
        binary_convert_to_floating_point(sign_bit, mantissa, exponent)
    else:
        float_input = str(input_mantissa_dec.get())
        if float_input[0] == "-":
            sign_bit = "1"
            float_input = float_input[1:]
        exponent_input = int(exp_input.get())
        mantissa, exponent = decimal_convert_to_normalized_binary(float_input, exponent_input)
        mantissa = limit_mantissa(mantissa)
        print("normalized: ", len(mantissa), mantissa, exponent)
        binary_convert_to_floating_point(sign_bit, mantissa, exponent)

def binary_convert_to_floating_point(sign, mantissa, exponent):
    infinite_flag = False
    # Set sign bit
    sign_bit = sign
    
    # Compute binary of exponent
    if exponent <= 16383 and exponent >= -16382:
        binary_exponent = bin((exponent + 16383))[2:].zfill(15)
    elif exponent > 16383:
        binary_exponent = "111111111111111"
        infinite_flag = True
    elif exponent < -16382:
        binary_exponent = "000000000000000"
    
    # Compute binary of mantissa
    if infinite_flag == False:
        if len(mantissa) < 112:
            mantissa = mantissa + "0" * (112 - len(mantissa))
            mantissa_output = mantissa + "0...0"
        binary_mantissa = mantissa
        print(mantissa)
        print(len(binary_mantissa), binary_mantissa)
        # Have another mantissa variable but with ellipsis for output
        mantissa_output = binary_mantissa
    else:
        binary_mantissa = "0" * 112
        mantissa_output = "0...0"

    print("sign bit: ", sign_bit)
    print("binary exponent: ", binary_exponent)
    print("binary mantissa: ", binary_mantissa)

    binary_output.config(text=sign_bit + "  " + binary_exponent + "  " + mantissa_output)

    # Print hexadecimal output
    hex_output_text = hex(int(sign_bit + binary_exponent + binary_mantissa, 2))[2:].zfill(16)
    hex_output_text_split = ' '.join([hex_output_text[i:i+4] for i in range(0, len(hex_output_text), 4)])
    hex_output.config(text="0x"+hex_output_text_split.upper())

def decimal_convert_to_normalized_binary(decimal, exponent):
    
    dec = adjust_decimal(decimal, exponent)
    print(dec)

    if "." not in dec:
        dec += ".0"
    # Split the decimal into integer and fractional parts
    integer_part, fractional_part = str(dec).split('.')

    # Convert the integer part to binary
    integer_binary = bin(int(integer_part))[2:]

    # Convert the fractional part to binary (with precision limitation)
    fraction = fraction_to_binary(float("0."+fractional_part))

    # Combine integer and fractional binary parts
    binary = integer_binary + '.' + fraction

    # Normalize the binary 
    normalized_binary, new_exponent = normalize_binary(binary, 0)

    print(normalized_binary, "  ", new_exponent)

    return normalized_binary, new_exponent

def normalize_binary(binary, exponent):
    # Find the position of the first '1' before the decimal point
    dot_position = binary.find('.')
    first_one_position = binary.find('1')
    print(first_one_position, " ", dot_position)

    # Shift the decimal point (adjusting the exponent) 
    if first_one_position < dot_position: 
        binary = binary[:dot_position]+binary[dot_position+1:]
        shift = dot_position - first_one_position - 1
        normalized_binary = '1.' + binary[dot_position-shift:]
        new_exponent = -shift
    else:  
        binary = binary[:dot_position]+binary[dot_position+1:]
        shift = first_one_position - dot_position
        normalized_binary = binary[first_one_position-1] + "." + binary[first_one_position:]
        new_exponent = shift 

    new_exponent += exponent

    print(normalized_binary)

    return normalized_binary[2:], new_exponent

def adjust_decimal(decimal_str, exponent):
    # Convert the decimal string to a Decimal object
    decimal_value = Decimal(decimal_str)
    print(decimal_value)
    # Multiply the decimal value by 10^exponent
    adjusted_value = Decimal(decimal_str) * Decimal(str(10 ** exponent))
    
    # Convert the adjusted value back to a string
    adjusted_str = str(adjusted_value)
    
    return adjusted_str

def limit_mantissa(mantissa):
    if len(mantissa) > 112:
        # Perform ROUND HALF TO EVEN
        if mantissa[112:] == ("1" + "0" * (len(mantissa) - 113)) and mantissa[111] == "1":
            mantissa = bin(int(mantissa[:112], 2) + 1)[2:]
        elif mantissa[112] == "1":
            mantissa = bin(int(mantissa[:112], 2) + 1)[2:]
        else:
            mantissa = mantissa[:112]
        return mantissa
    else:
        return mantissa

def fraction_to_binary(fraction, precision=112):
    binary = ""  # Initialize with "" for the fractional part
    while fraction > 0 and precision > 0:
        fraction *= 2
        int_part = int(fraction)
        binary += str(int_part)
        fraction -= int_part
        precision -= 1

    return binary  

# GUI LOGIC
def update_label():
    selected_conversion_type = conversion_type.get()
    print(selected_conversion_type)
    if selected_conversion_type == "Binary":
        label_mantissa_dec.config(text="Binary:")
        label_exponent.config(text="Base-2 Exponent:")
    else :
        label_mantissa_dec.config(text="Decimal:")
        label_exponent.config(text="Base-10 Exponent:")

def clear():
    clear_input()
    clear_output()

def clear_output():
    binary_output.config(text="")
    hex_output.config(text="")
    error_message.config(text="")

def clear_input():
    input_mantissa_dec.delete(0, "end")
    exp_input.delete(0, "end")
    error_message.config(text="")

# Create the Tkinter window
window = tk.Tk()
window.geometry("900x400")  # Set the window size to 400x300 pixels

# Create a frame for the radio buttons
radio_frame = tk.Frame(window)
radio_frame.pack()

# Create the radio buttons for selecting conversion type
conversion_type = tk.StringVar(window)
conversion_type.set("Binary")  # Set the default option

radio_binary = tk.Radiobutton(radio_frame, text="Binary", variable=conversion_type, value="Binary", command=update_label)
radio_binary.pack(side="left")

radio_decimal = tk.Radiobutton(radio_frame, text="Decimal", variable=conversion_type, value="Decimal", command=update_label)
radio_decimal.pack(side="left")

# sign_frame = tk.Frame(window)
# sign_frame.pack()
# inner_sign_frame = tk.Frame(sign_frame)
# inner_sign_frame.pack()
# # Create the sign option menu
# label_sign = tk.Label(inner_sign_frame, text="Sign:")
# label_sign.pack(side="top", padx=5)
# sign = tk.StringVar(inner_sign_frame)
# sign.set("Negative")
# sign_option_menu = tk.OptionMenu(inner_sign_frame, sign, "Negative", "Positive")
# sign_option_menu.pack(side="left")


# Create a frame for the inputs
input_frame = tk.Frame(window)
input_frame.pack(pady=5)

input_frame1 = tk.Frame(window)
input_frame1.pack( padx=10)
input_frame2 = tk.Frame(window)
input_frame2.pack( padx=10)



# Create the float input label and entry widget
label_mantissa_dec = tk.Label(input_frame1, text="Binary:")
label_mantissa_dec.pack(side="left")
input_mantissa_dec = tk.Entry(input_frame1, width=100)
input_mantissa_dec.pack(side="left")

# Create the integer input label and entry widget
label_exponent = tk.Label(input_frame2, text="Base-2 Exponent:")
label_exponent.pack(side="left")
exp_input = tk.Entry(input_frame2, width=100)
exp_input.pack(side="left")

# Create Error message
error_message = tk.Label(window, text="")
error_message.pack(pady=5)

# Create the convert button
button_convert = tk.Button(window, text="Convert", command=convert)
button_convert.pack(pady=5)

# Create 2 output fields
output_frame = tk.Frame(window)
output_frame.pack()

output_frame1 = tk.Frame(output_frame)
output_frame1.pack(side="top")
output_frame2 = tk.Frame(output_frame)
output_frame2.pack(side="bottom")

label_binaryout = tk.Label(output_frame1, text="Binary Output:")
label_binaryout.pack(side="left")
binary_output = tk.Label(output_frame1, text="")
binary_output.pack(side="left")

label_hexout = tk.Label(output_frame2, text="Hexadecimal Output:")
label_hexout.pack(side="left")
hex_output = tk.Label(output_frame2, text="")
hex_output.pack(side="left")

# Create the clear button
button_clear = tk.Button(window, text="Clear", command=clear)
button_clear.pack(pady=5)

def export_output():
    convert()
    # Get the details to export
    sign_bit = binary_output.cget("text").split()[0]
    binary_exponent = binary_output.cget("text").split()[1]
    binary_mantissa = binary_output.cget("text").split()[2]

    # Create the file path
    file_path = "./output.txt"

    # Write the details to the file
    with open(file_path, "w") as file:
        file.write("Sign Bit: {}\n".format(sign_bit))
        file.write("Binary Exponent: {}\n".format(binary_exponent))
        file.write("Binary Mantissa: {}\n".format(binary_mantissa))
        file.write("Full Binary Output: {}\n".format(binary_output.cget("text")))
        file.write("Hexadecimal Output: {}\n".format(hex_output.cget("text")))

    # Show success message
    error_message.config(text="Exported output as .txt successfully.")

# Create the export button
button_export = tk.Button(window, text="Output as .txt", command=export_output)
button_export.pack(pady=5)


# Start the Tkinter event loop
window.mainloop()
