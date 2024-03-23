import tkinter as tk
import decimal
import sys
sys.set_int_max_str_digits(20000)
decimal.getcontext().prec = 112
Decimal = decimal.Decimal

MATH_OPERATORS = ["+", "-", "*", "/", "^", "√"]
MAX_MANTISSA_LENGTH = 112

# Main Convert Logic
def convert():
    clear_output()
    if empty_input():
        return 0
    sign_bit = "0"
    # Get the selected conversion type 
    selected_conversion_type = conversion_type.get()

    number_input = str(input_mantissa_dec.get())
    if (number_input[0] == "-"):
        sign_bit = "1"
        number_input = number_input[1:]
    exponent_input = str(exp_input.get())

    if any(bit.isalpha() for bit in number_input) or any(bit.isalpha() for bit in exponent_input) or number_input.count('.') > 1:
        if "log(-" in number_input or "ln(-" in number_input or "log(-" in exponent_input or "ln(-" in exponent_input:
            output_NaN("qNaN")
            return 0
        output_NaN("sNaN")
        return 0
        
    if any(bit in MATH_OPERATORS for bit in number_input) or any(bit.isalpha() for bit in exponent_input):
        if any(bit in "∞" for bit in number_input) or any(bit in "∞" for bit in exponent_input):
            output_NaN("qNaN")
            return 0
        if number_input in ["0/0", "-0/0", "0/-0", "-0/-0"] or exponent_input in ["0/0", "-0/0", "0/-0", "-0/-0"]:
            output_NaN("qNaN")
            return 0
        if "√-" in number_input or  "√-" in exponent_input:
            if number_input[number_input.find("√-") + 2] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"] or exponent_input[exponent_input.find("√-") + 2] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                output_NaN("qNaN")
                return 0
            else:
                output_NaN("sNaN")
                return 0
        output_NaN("sNaN")
        return 0
    
    # Get the float input from the entry widget
    if selected_conversion_type == "Binary":
        binary_input = number_input

        if not all(bit in '01.' for bit in binary_input) : 
            error_message.config(text="Error: Invalid binary input.") 
            return 0
        
        exponent_input = int(exponent_input)
        

        mantissa, exponent = normalize_binary(binary_input, exponent_input)
        mantissa = limit_mantissa(mantissa)
        print("normalized: ", mantissa, exponent)
        convert_binary_to_floating_point(sign_bit, mantissa, exponent)
    else:
        float_input = number_input
        if float_input[0] == "-":
            sign_bit = "1"
            float_input = float_input[1:]
        exponent_input = int(exponent_input)
        
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
        if exponent == -16382 and not all(bit in "0" for bit in mantissa):
            binary_exponent = "000000000000000"
    elif exponent > 16383:
        binary_exponent = "111111111111111"
        infinite_flag = True
    elif exponent < -16382:
        binary_exponent = "000000000000000"
    
    # Compute binary of mantissa
    if infinite_flag == False:
        # Truncation logic remains the same
        binary_mantissa = mantissa[:MAX_MANTISSA_LENGTH] + "0" * (MAX_MANTISSA_LENGTH - len(mantissa))
        shortened_mantissa = mantissa[:MAX_MANTISSA_LENGTH] + ("0...0" * 1 if (MAX_MANTISSA_LENGTH - len(mantissa) > 3 ) else "0" * (MAX_MANTISSA_LENGTH - len(mantissa)))
    else:
        binary_mantissa = "0" * MAX_MANTISSA_LENGTH
        shortened_mantissa = "0...0"

    print("sign bit: ", sign)
    print("binary exponent: ", binary_exponent)
    print("binary mantissa: ", binary_mantissa)

    binary_output.config(text=sign + "  " + binary_exponent + "  " + shortened_mantissa)

    # Print hexadecimal output
    hex_output_text = hex_output_formatting(sign, binary_exponent, binary_mantissa)
    hex_output_text_formatted = ' '.join([hex_output_text[i:i+4] for i in range(0, len(hex_output_text), 4)]).upper()
    hex_output.config(text="0x"+hex_output_text_formatted)
    print("hex output: ", "0x"+hex_output_text_formatted)

    special_case_value = "Normal"
    if sign == "0" and binary_exponent == "111111111111111" and binary_mantissa == "01" + "0" * 110:
        special_case_value = "sNaN"
    elif sign == "0" and binary_exponent == "111111111111111" and binary_mantissa == "1" + "0" * 111:
        special_case_value = "qNaN"
    elif sign == "0" and binary_exponent == "000000000000000" and binary_mantissa == "0" * 112:
        special_case_value = "Zero"
    elif sign == "1" and binary_exponent == "000000000000000" and binary_mantissa == "0" * 112:
        special_case_value = "- Zero"
    elif sign == "1" and binary_exponent == "111111111111111" and binary_mantissa == "0" * 112:
        special_case_value = "- Infinity"
    elif sign == "0" and binary_exponent == "111111111111111" and binary_mantissa == "0" * 112:
        special_case_value = "+ Infinity"
    elif binary_exponent == "000000000000000" and binary_mantissa != "0" * 112:
        special_case_value = "Denormalized"

    special_case.config(text=special_case_value)

def convert_decimal_to_normalized_binary(decimal, exponent):
    # Converts decimal input to normalized IEEE-754 Binary128 binary representation.

    integer_part, fractional_part = adjust_decimal(decimal, exponent)

    # Convert to binary
    binary = decimal_to_binary(integer_part, fractional_part)
    print("final binary: ",binary)
    normalized_binary, new_exponent = normalize_binary(binary, 1)

    return normalized_binary, new_exponent-1

# ------------------ Helper Functions ------------------
def normalize_binary(binary, exponent):
    new_exponent = 0
    # if binary does not contain a decimal point
    if '.' not in binary:
        binary = binary + '.0'

    dot_position = binary.find('.')
    first_one_position = binary.find('1')
    if (first_one_position == -1):
        return "0"*112, -999999 # Exponent set to 999999 for special cases meant to have exponent bits 000 0000 0000 0000 0000
    print(dot_position, first_one_position)
     
    if exponent < -16382 :
        # Shift the decimal point to the left until exponent reaches -16382
        while exponent < -16382:
            if dot_position == 1:
                binary = '0.' + binary[0] + binary[2:]
            else:
                binary = binary[:dot_position-2] + '.' + binary[dot_position-1] + binary[dot_position+1:]
                dot_position -= 1
            exponent += 1

        normalized_binary = binary
    else:
        
        # Shift the decimal point until the string becomes 1.f where f is the other digits in the string
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
            new_exponent = -shift 

    new_exponent += exponent

    print("shifting: ", normalized_binary, exponent)

    return normalized_binary[2:], new_exponent

def adjust_decimal(decimal_str, exponent):
    print(decimal_str, exponent)
     # Set the decimal context for high precision
    context = decimal.getcontext()
    context.prec = 999999
    print(context)

    if '.' not in decimal_str:
        decimal_str = decimal_str + '.0'
    dot_position = decimal_str.find('.')

    if (exponent < 0 and abs(exponent) > dot_position) :
        decimal_str = "0." + "0" * (-exponent - dot_position) + decimal_str[:dot_position] + decimal_str[dot_position+1:]
        exponent = 0
        print(decimal_str)
        decimal_str = decimal.Decimal(decimal_str)
         # Extract the integer and fractional parts
        integer_part = int(decimal_str)
        fractional_part = decimal_str % 1
        print(integer_part, fractional_part)

        return integer_part, fractional_part
    else:
        # Convert the decimal string to a decimal object for accurate calculations
        adjusted_value = decimal.Decimal(decimal_str) * decimal.Decimal(10**exponent)

        # Handle zero case
        if adjusted_value == 0:
            return 0, 0

        # Extract the integer and fractional parts
        integer_part = int(adjusted_value)
        fractional_part = adjusted_value % 1
        print(integer_part, fractional_part)

        return integer_part, fractional_part

def decimal_to_binary(decimal, fraction):
    # Convert the integer part to binary (NumPy)
    binary_integer = bin(decimal)[2:]  # Remove '0b' prefix

    # Convert the fractional part (repeated division by 2)
    binary_fraction = ""
    while fraction > 0:
        fraction *= 2
        if fraction >= 1:
            binary_fraction += "1"
            fraction -= 1
            
        else:
            binary_fraction += "0"
        # Limit the number of fractional digits (adjust precision as needed)
        if len(binary_fraction) > 20000:
            break

    print("binary parts: ", binary_integer, binary_fraction)

    # Combine integer and fractional parts (handle potential leading zero in fraction)
    binary_string = binary_integer + (".0" if not binary_fraction else ".") + binary_fraction
    return binary_string

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

def output_NaN(NaN):
    if NaN == "sNaN":
        sign = "0"
        exponent = "111111111111111"
        mantissa = "01" + "0" * 110
    else:
        sign = "0"
        exponent = "111111111111111"
        mantissa = "1" + "0" * 111

    binary_output.config(text=sign + "  " + exponent + "  " + mantissa)

    print("sign bit: ", sign)
    print("binary exponent: ", exponent)
    print("binary mantissa: ", mantissa)

    # Print hexadecimal output
    hex_output_text = hex_output_formatting(sign, exponent, mantissa)
    hex_output_text_formatted = ' '.join([hex_output_text[i:i+4] for i in range(0, len(hex_output_text), 4)]).upper()
    hex_output.config(text="0x"+hex_output_text_formatted)

    print("hex output: ", "0x"+hex_output_text_formatted)

    special_case_value = "Normal"
    if sign == "0" and exponent == "111111111111111" and mantissa == "01" + "0" * 110:
        special_case_value = "sNaN"
    elif sign == "0" and exponent == "111111111111111" and mantissa == "1" + "0" * 111:
        special_case_value = "qNaN"

    special_case.config(text=special_case_value)

def hex_output_formatting(sign, exponent, mantissa):
    binary_rep = sign + exponent + mantissa

    hex_rep = ""

    hex_dict = {
        "0000" : "0",
        "0001" : "1",
        "0010" : "2",
        "0011" : "3",
        "0100" : "4",
        "0101" : "5",
        "0110" : "6",
        "0111" : "7",
        "1000" : "8",
        "1001" : "9",
        "1010" : "A",
        "1011" : "B",
        "1100" : "C",
        "1101" : "D",
        "1110" : "E",
        "1111" : "F"
    }

    for i in range(0, len(binary_rep), 4):
        hex_rep += hex_dict[binary_rep[i:i+4]]

    return hex_rep

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
title_label = tk.Label(title_frame, text="IEEE-754 Binary-128 floating point converter", font=("Franklin Gothic Medium", 20), foreground="white", bg="#544E61")
title_label.pack()

# Create a frame for the inputs
input_frame = tk.Frame(window)
input_frame.configure(bg="#D6BBC0", bd=1, relief="solid", highlightbackground="black")
input_frame.pack(pady=5)
input_title = tk.Label(input_frame, text="Input", font=("Franklin Gothic Medium", 15), foreground="black", bg="#D6BBC0")
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
button_convert = tk.Button(window, text="Convert", width=14, height=1, font=("Arial", 12), bg="#4E5166", foreground="white", command=convert)
button_convert.pack(pady=5)

# Create 2 output fields
output_frame = tk.Frame(window)
output_frame.configure(bg="#D6BBC0", bd=1, relief="solid", highlightbackground="black")
output_frame.pack(pady=5, fill="x", padx=20)
output_title = tk.Label(output_frame, text="Output", font=("Franklin Gothic Medium", 15), foreground="black", bg="#D6BBC0")
output_title.pack()

output_frame0 = tk.Frame(output_frame, bg="#EFEFEF", bd=1,  relief="solid", highlightbackground="black")
output_frame0.pack(side="top", pady=5)
output_frame1 = tk.Frame(output_frame, bg="#DEF6CA", bd=1,  relief="solid", highlightbackground="black")
output_frame1.pack(side="top", pady=5)
output_frame2 = tk.Frame(output_frame,  bg="#AEE5D8", bd=1,  relief="solid", highlightbackground="black")
output_frame2.pack(side="top", pady=5)


label_special = tk.Label(output_frame0, text="Special Case:", bg="#EFEFEF")
label_special.pack(side="left")
special_case = tk.Label(output_frame0, text="", bg="#EFEFEF")
special_case.pack(side="left")

label_binaryout = tk.Label(output_frame1, text="Binary Output:", bg="#DEF6CA")
label_binaryout.pack(side="left")
binary_output = tk.Label(output_frame1, text="", bg="#DEF6CA")
binary_output.pack(side="left")

label_hexout = tk.Label(output_frame2, text="Hexadecimal Output:", bg="#AEE5D8")
label_hexout.pack(side="left")
hex_output = tk.Label(output_frame2, text="", bg="#AEE5D8")
hex_output.pack(side="left")

# Create the clear button
button_clear = tk.Button(window, text="Clear", width=7, height=1, font=("Arial", 11), bg="#4E5166", foreground="white", command=clear)
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
        if (conversion_type.get() == "Binary"):
            file.write("Conversion Type: Binary\n")
            file.write("Input Binary: {}\n".format(input_mantissa_dec.get()))
            file.write("Input Base-2 Exponent: {}\n".format(exp_input.get()))
        else :
            file.write("Conversion Type: Decimal\n")
            file.write("Input Decimal: {}\n".format(input_mantissa_dec.get()))
            file.write("Input Base-10 Exponent: {}\n".format(exp_input.get()))

        special_case = "Normal"
        if sign_bit == "0" and binary_exponent == "111111111111111" and binary_mantissa == "01" + "0" * 110:
            special_case = "sNaN"
        elif sign_bit == "0" and binary_exponent == "111111111111111" and binary_mantissa == "1" + "0" * 111:
            special_case = "qNaN"
        elif sign_bit == "0" and binary_exponent == "000000000000000" and binary_mantissa == "0" * 112:
            special_case = "Zero"
        elif sign_bit == "1" and binary_exponent == "000000000000000" and binary_mantissa == "0" * 112:
            special_case = "- Zero"
        elif sign_bit == "1" and binary_exponent == "111111111111111" and binary_mantissa == "0" * 112:
            special_case = "- Infinity"
        elif sign_bit == "0" and binary_exponent == "111111111111111" and binary_mantissa == "0" * 112:
            special_case = "+ Infinity"
        elif binary_exponent == "000000000000000" and binary_mantissa != "0" * 112:
            special_case = "Denormalized"

        file.write("Special Case: {}\n".format(special_case))
        file.write("Sign Bit: {}\n".format(sign_bit))
        file.write("Binary Exponent: {}\n".format(binary_exponent))
        file.write("Binary Mantissa: {}\n".format(binary_mantissa))
        file.write("Full Binary Output: {}\n".format(binary_output.cget("text")))
        file.write("Hexadecimal Output: {}\n".format(hex_output.cget("text")))

    # Show success message
    error_message.config(text="Exported output as .txt successfully.")

# Create the export button
button_export = tk.Button(window, text="Output as .txt", width=10, height=1, font=("Arial", 11), bg="#4E5166", foreground="white", command=export_output)
button_export.pack(pady=5)


# Start the Tkinter event loop
window.mainloop()
