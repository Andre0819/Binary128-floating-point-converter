import tkinter as tk


# Main Convert Logic
def convert():
    sign_bit = ""
    # Get the selected conversion type 
    selected_conversion_type = conversion_type.get()
    
    # Get the float input from the entry widget
    if selected_conversion_type == "Binary":
        if sign.get() == "Negative":
            sign_bit = "1"
        else:
            sign_bit = "0"
        binary_input = str(input_mantissa_dec.get())

        if not (all(bit in ['0', '1'] for bit in binary_input)):
            error_message.config(text="Error: Invalid binary mantissa input.")
            return 0
         # Get the exponent integer input from the entry widget
        try:
            exponent_input = int(exp_input.get())
        except ValueError:
            error_message.config(text="Error: Invalid exponent input. Must be integer.")
            return 0
        binary_convert_to_floating_point(sign_bit, binary_input, exponent_input)
    else:
        float_input = float(input_mantissa_dec.get())
        if sign.get() == "Negative":
            sign_bit = "1"
        else:
            sign_bit = "0"
        exponent_input = int(exp_input.get())
        mantissa, exponent = decimal_convert_to_normalized_binary(float_input, exponent_input)
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
        binary_mantissa = mantissa + str(bin(0)[2:].zfill(112-len(mantissa)))
        # Have another mantissa variable but with ellipsis for output
        mantissa_output = mantissa + "0...0"
    else:
        binary_mantissa = "0"*112
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
    # Multiply decimal by 10 raised to the exponent
    decimal = decimal * 10**exponent

    # Split the decimal into integer and fractional parts
    integer_part, fractional_part = str(decimal).split('.')

    # Convert the integer part to binary
    integer_binary = bin(int(integer_part))[2:]

    # Convert the fractional part to binary (with precision limitation)
    fraction = fraction_to_binary(float("0."+fractional_part))

    # Combine integer and fractional binary parts
    binary = integer_binary + '.' + fraction

    print(binary)

    # Normalize the binary 
    normalized_binary, new_exponent = normalize_binary(binary)

    print(normalized_binary, "  ", new_exponent)

    return normalized_binary, new_exponent

def normalize_binary(binary):
    # Find the position of the first '1' before the decimal
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

    return normalized_binary[2:], new_exponent 

def fraction_to_binary(fraction, precision=32):
    binary = ""  # Initialize with "0." for the fractional part
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
        label_mantissa_dec.config(text="Binary Mantissa:")
        label_exponent.config(text="Base-2 Exponent:")
    else :
        label_mantissa_dec.config(text="Decimal:")
        label_exponent.config(text="Base-10 Exponent:")

def clear():
    input_mantissa_dec.delete(0, "end")
    exp_input.delete(0, "end")
    binary_output.config(text="")
    hex_output.config(text="")

# Create the Tkinter window
window = tk.Tk()
window.geometry("600x400")  # Set the window size to 400x300 pixels

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

sign_frame = tk.Frame(window)
sign_frame.pack()
inner_sign_frame = tk.Frame(sign_frame)
inner_sign_frame.pack()
# Create the sign option menu
label_sign = tk.Label(inner_sign_frame, text="Sign:")
label_sign.pack(side="top", padx=5)
sign = tk.StringVar(inner_sign_frame)
sign.set("Negative")
sign_option_menu = tk.OptionMenu(inner_sign_frame, sign, "Negative", "Positive")
sign_option_menu.pack(side="left")


# Create a frame for the inputs
input_frame = tk.Frame(window)
input_frame.pack(pady=5)

input_frame1 = tk.Frame(input_frame)
input_frame1.pack(side="left", padx=10)
input_frame2 = tk.Frame(input_frame)
input_frame2.pack(side="left", padx=10)



# Create the float input label and entry widget
label_mantissa_dec = tk.Label(input_frame1, text="Binary Mantissa:")
label_mantissa_dec.pack(side="top")
input_mantissa_dec = tk.Entry(input_frame1)
input_mantissa_dec.pack(side="left")

# Create the integer input label and entry widget
label_exponent = tk.Label(input_frame2, text="Base-2 Exponent:")
label_exponent.pack(side="top")
exp_input = tk.Entry(input_frame2)
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


# Start the Tkinter event loop
window.mainloop()
