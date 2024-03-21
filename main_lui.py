import tkinter as tk

# Main Convert Logic
def convert():
    sign_bit = ""
    # Get the selected conversion type
    selected_conversion_type = conversion_type.get()

    # Get the input from the entry widget
    input_value = input_mantissa_dec.get()

    # Split the input into integer and fractional parts
    parts = input_value.split('.')
    integer_part = parts[0]
    fractional_part = parts[1] if len(parts) > 1 else ""

    if selected_conversion_type == "Binary":
        if sign.get() == "Negative":
            sign_bit = "1"
        else:
            sign_bit = "0"

        # Convert binary input to floating-point
        binary_mantissa = integer_part + fractional_part
        if not (all(bit in ['0', '1'] for bit in binary_mantissa)):
            error_message.config(text="Error: Invalid binary mantissa input.")
            return

        try:
            exponent_input = int(exp_input.get())
        except ValueError:
            error_message.config(text="Error: Invalid exponent input. Must be integer.")
            return

        binary_convert_to_floating_point(sign_bit, binary_mantissa, exponent_input)
    else:
        if sign.get() == "Negative":
            sign_bit = "1"
        else:
            sign_bit = "0"

        try:
            exponent_input = int(exp_input.get())
            decimal_input = float(integer_part) + float("0." + fractional_part)
        except ValueError:
            error_message.config(text="Error: Invalid decimal input.")
            return

        mantissa, exponent = decimal_convert_to_normalized_binary(decimal_input, exponent_input)
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
    # Combine integer and fractional parts
    decimal = decimal * 10**exponent

    # Split the decimal into integer and fractional parts
    integer_part = int(decimal)
    fractional_part = decimal - integer_part

    # Convert the integer part to binary
    integer_binary = bin(integer_part)[2:]

    # Convert the fractional part to binary
    fractional_binary = fraction_to_binary(fractional_part)

    # Combine integer and fractional binary parts
    binary = integer_binary + '.' + fractional_binary

    # Normalize the binary
    normalized_binary, new_exponent = normalize_binary(binary)

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

def fraction_to_binary(fraction, precision=112):
    binary = ""
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
conversion_type = tk.StringVar(window)
conversion_type.set("Binary")  # Set the default option

radio_binary = tk.Radiobutton(radio_frame, text="Binary",bg="#D6BBC0", variable=conversion_type, value="Binary", command=update_label)
radio_binary.pack(side="left")

radio_decimal = tk.Radiobutton(radio_frame, text="Decimal",bg="#D6BBC0", variable=conversion_type, value="Decimal", command=update_label)
radio_decimal.pack(side="left")

sign_frame = tk.Frame(input_frame)
sign_frame.pack()
inner_sign_frame = tk.Frame(sign_frame, bg="#D6BBC0")
inner_sign_frame.pack()

# Create the sign option menu
label_sign = tk.Label(inner_sign_frame, text="Sign:",bg="#D6BBC0")
label_sign.pack(side="top", padx=5)
sign = tk.StringVar(inner_sign_frame)
sign.set("Negative")
sign_option_menu = tk.OptionMenu(inner_sign_frame, sign, "Negative", "Positive")
sign_option_menu.config(bg="#D6BBC0")
sign_option_menu.pack(side="left")


# Create a frame for the inputs
input_frame = tk.Frame(input_frame,bg="#D6BBC0")
input_frame.pack(pady=5)

input_frame1 = tk.Frame(input_frame,bg="#D6BBC0")
input_frame1.pack(side="left", padx=10)
input_frame2 = tk.Frame(input_frame,bg="#D6BBC0")
input_frame2.pack(side="left", padx=10)



# Create the float input label and entry widget
label_mantissa_dec = tk.Label(input_frame1, text="Binary Mantissa:",bg="#D6BBC0")
label_mantissa_dec.pack(side="top")
input_mantissa_dec = tk.Entry(input_frame1)
input_mantissa_dec.pack(side="left")

# Create the integer input label and entry widget
label_exponent = tk.Label(input_frame2, text="Base-2 Exponent:",bg="#D6BBC0")
label_exponent.pack(side="top")
exp_input = tk.Entry(input_frame2)
exp_input.pack(side="left")

# Create Error message
error_message = tk.Label(window, text="",bg="#CEEDDB")
error_message.pack(pady=5)

# Create the convert button
button_convert = tk.Button(window, text="Convert", command=convert)
button_convert.pack(pady=5)

# Create 2 output fields
output_frame = tk.Frame(window)
output_frame.configure(bg="#D6BBC0", bd=1, relief="solid", highlightbackground="black")
output_frame.pack()

output_frame1 = tk.Frame(output_frame,bg="#D6BBC0")
output_frame1.pack(side="top")
output_frame2 = tk.Frame(output_frame)
output_frame2.pack(side="bottom")

label_binaryout = tk.Label(output_frame1, text="Binary Output:",bg="#D6BBC0")
label_binaryout.pack(side="left")
binary_output = tk.Label(output_frame1, text="",bg="#D6BBC0")
binary_output.pack(side="left")

label_hexout = tk.Label(output_frame2, text="Hexadecimal Output:",bg="#D6BBC0")
label_hexout.pack(side="left")
hex_output = tk.Label(output_frame2, text="",bg="#D6BBC0")
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
