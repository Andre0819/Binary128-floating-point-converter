import tkinter as tk
import decimal
import sys
sys.set_int_max_str_digits(5000)
decimal.getcontext().prec = 112
Decimal = decimal.Decimal

MAX_MANTISSA_LENGTH = 112

# Main Convert Logic
def convert():
    clear_output()
    if empty_input():
        return 0
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
        convert_binary_to_floating_point(sign_bit, mantissa, exponent)
    else:
        float_input = str(input_mantissa_dec.get())
        if float_input[0] == "-":
            sign_bit = "1"
            float_input = float_input[1:]
        exponent_input = int(exp_input.get())
        mantissa, exponent = convert_decimal_to_normalized_binary(float_input, exponent_input)
        mantissa = limit_mantissa(mantissa)
        print("normalized: ", len(mantissa), mantissa, exponent)
        convert_binary_to_floating_point(sign_bit, mantissa, exponent)

def convert_binary_to_floating_point(sign, mantissa, exponent):
    # Converts normalized binary input to IEEE-754 Binary128 floating-point representation.
    infinite_flag = False
    
    # Compute binary of exponent (with special cases)
    if exponent <= 16383 and exponent >= -16382:
        binary_exponent = bin((exponent + 16383))[2:].zfill(15)
    elif exponent > 16383:
        binary_exponent = "111111111111111"
        infinite_flag = True
    elif exponent < -16382:
        binary_exponent = "000000000000000"
    
    # Compute binary of mantissa
    if infinite_flag == False:
        # Truncation logic remains the same
        binary_mantissa = mantissa[:MAX_MANTISSA_LENGTH] + "0" * (MAX_MANTISSA_LENGTH - len(mantissa))
    else:
        binary_mantissa = "0" * MAX_MANTISSA_LENGTH

    print("sign bit: ", sign)
    print("binary exponent: ", binary_exponent)
    print("binary mantissa: ", binary_mantissa)

    binary_output.config(text=sign + "  " + binary_exponent + "  " + binary_mantissa)

    # Print hexadecimal output
    hex_output_text = hex(int(sign + binary_exponent + binary_mantissa, 2))[2:].zfill(16)
    hex_output_text_formatted = ' '.join([hex_output_text[i:i+4] for i in range(0, len(hex_output_text), 4)]).upper()
    hex_output.config(text="0x"+hex_output_text_formatted)

def convert_decimal_to_normalized_binary(decimal, exponent):
    # Converts decimal input to normalized IEEE-754 Binary128 binary representation.

    dec = adjust_decimal(decimal, exponent)
    if "." not in dec:
        dec += ".0"

    integer_part, fractional_part = str(dec).split('.')
    integer_binary = bin(int(integer_part))[2:]
    fraction = fraction_to_binary(float("0."+fractional_part))

    binary = integer_binary + '.' + fraction
    normalized_binary, new_exponent = normalize_binary(binary, 0)

    return normalized_binary, new_exponent

# ------------------ Helper Functions ------------------
def normalize_binary(binary, exponent):
    # Normalizes a binary number (string) in the form '1.xxxx...' and returns the fractional part of the normalized version.
    
    # Find the position of the first '1' before the decimal point
    dot_position = binary.find('.')
    first_one_position = binary.find('1')

    shift = 0  # Shift used for adjusting the exponent
    if first_one_position < dot_position: 
        binary = binary[:dot_position]+binary[dot_position+1:]
        shift = dot_position - first_one_position - 1
        normalized_binary = '1.' + binary[dot_position-shift:]
        new_exponent = shift
    else:  
        binary = binary[:dot_position]+binary[dot_position+1:]
        shift = first_one_position - dot_position
        normalized_binary = binary[first_one_position-1] + "." + binary[first_one_position:]
        new_exponent = +shift 
    new_exponent += exponent

    return normalized_binary[2:], new_exponent

def adjust_decimal(decimal_str, exponent):
    # Multiply the decimal value by 10^exponent
    adjusted_value = Decimal(decimal_str) * Decimal(str(10 ** exponent))
    
    # Convert the adjusted value back to a string
    adjusted_str = str(float(adjusted_value))
    
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

# ------------------ GUI LOGIC ------------------
def update_label():
    selected_conversion_type = conversion_type.get()
    print(selected_conversion_type)
    if selected_conversion_type == "Binary":
        label_mantissa_dec.config(text="Binary:")
        label_exponent.config(text="Base-2 Exponent:")
    else :
        label_mantissa_dec.config(text="Decimal:")
        label_exponent.config(text="Base-10 Exponent:")

def empty_input():
    if not input_mantissa_dec.get() or not exp_input.get():
        error_message.config(text="Error: Fields are empty.")
        return True
    return False

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
window.geometry("1000x500")  # Set the window size to 400x300 pixels
window.configure(bg="#CEEDDB")

title_frame = tk.Frame(window)
title_frame.pack(fill="x")
title_frame.config(bg="#544E61", bd=1, relief="solid", highlightbackground="black")
title_label = tk.Label(title_frame, text="IEEE-754 Binary-128 floating point converter", font=("Arial", 20), foreground="white", bg="#544E61")
title_label.pack()

# Create a frame for the inputs
input_frame = tk.Frame(window)
input_frame.configure(bg="#D6BBC0", bd=1, relief="solid", highlightbackground="black")
input_frame.pack(pady=5)
input_title = tk.Label(input_frame, text="Input", font=("Arial", 15), foreground="black", bg="#D6BBC0")
input_title.pack()

# Create a frame for the radio buttons
radio_frame = tk.Frame(input_frame)
radio_frame.pack(side="top")

# Create the radio buttons for selecting conversion type
conversion_type = tk.StringVar(input_frame)
conversion_type.set("Binary")  # Set the default option

radio_binary = tk.Radiobutton(radio_frame, text="Binary", bg="#D6BBC0", foreground="black", variable=conversion_type, value="Binary", font=("Arial", 12) ,command=update_label)
radio_binary.pack(side="left")

radio_decimal = tk.Radiobutton(radio_frame, text="Decimal", bg="#D6BBC0", foreground="black", variable=conversion_type, value="Decimal", font=("Arial", 12), command=update_label)
radio_decimal.pack(side="left")

input_frame1 = tk.Frame(input_frame)
input_frame1.pack( padx=10, pady=5)
input_frame2 = tk.Frame(input_frame)
input_frame2.pack( padx=10, pady=5)



# Create the float input label and entry widget
label_mantissa_dec = tk.Label(input_frame1, text="Binary:", font=("Arial", 10), bg="#D6BBC0")
label_mantissa_dec.pack(side="left")
input_mantissa_dec = tk.Entry(input_frame1, width=100)
input_mantissa_dec.pack(side="left")

# Create the integer input label and entry widget
label_exponent = tk.Label(input_frame2, text="Base-2 Exponent:", font=("Arial", 10), bg="#D6BBC0")
label_exponent.pack(side="left")
exp_input = tk.Entry(input_frame2, width=100)
exp_input.pack(side="left")

# Create Error message
error_message = tk.Label(window, text="", bg="#CEEDDB")
error_message.pack(pady=5)

# Create the convert button
button_convert = tk.Button(window, text="Convert", command=convert)
button_convert.pack(pady=5)

# Create 2 output fields
output_frame = tk.Frame(window)
output_frame.configure(bg="#D6BBC0", bd=1, relief="solid", highlightbackground="black")
output_frame.pack(pady=5, fill="x", padx=20)
output_title = tk.Label(output_frame, text="Output", font=("Arial", 15), foreground="black", bg="#D6BBC0")
output_title.pack()

output_frame1 = tk.Frame(output_frame)
output_frame1.pack(side="top", pady=5)
output_frame2 = tk.Frame(output_frame)
output_frame2.pack(side="bottom", pady=5)

label_binaryout = tk.Label(output_frame1, text="Binary Output:", bg="#D6BBC0")
label_binaryout.pack(side="left")
binary_output = tk.Label(output_frame1, text="", bg="#D6BBC0")
binary_output.pack(side="left")

label_hexout = tk.Label(output_frame2, text="Hexadecimal Output:", bg="#D6BBC0")
label_hexout.pack(side="left")
hex_output = tk.Label(output_frame2, text="", bg="#D6BBC0")
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
