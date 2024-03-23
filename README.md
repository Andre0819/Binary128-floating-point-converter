# IEEE-754 Binary-128 Floating Point Converter

This Python project implements an IEEE-754 Binary-128 floating-point converter, supporting conversions between binary and decimal representations, and including handling of special cases (NaN, Infinity, Zero, and Denormalized).

The code utilizes the Tkinter library to provide a graphical user interface (GUI) for use interactions

## Features
### Conversion Functionality
Converts binary and decimal values to IEEE-754 Binary-128 binary and hexadecimal representations.

### Special Case Handling:
Correctly represents and identifies:
- NaN (Not a Number)
- Infinity (Positive and Negative)
- Zero (Positive and Negative)
- Denormalized numbers

Graphical User Interface:
- User-friendly Tkinter GUI for inputting values and displaying results.

Output Formats:
- Displays converted results in binary, hexadecimal, and special case representations.

Output Export
- Option to export conversion results in a .txt file.

### Dependencies

- Python 3 (https://www.python.org/)
- Tkinter (Usually included in standard Python installations)
- Decimal (For high-precision decimal calculations) Install with 
> pip install tk

> pip install decimal

### Getting Started

1. Download: Download or clone the project files from this GitHub repository.
2. Install Dependencies: If you don't have the decimal module, install it using pip:
> pip install decimal
3. Run: Execute the main Python file: 
> python main.py

### Usage

1. Select Conversion Type: Choose between "Binary" or "Decimal" conversion using the radio buttons.
2. Enter Values:
- Input Field: Enter the binary or decimal number you want to convert.
- Exponent Field: Enter the corresponding base-2 or base-10 exponent.
3. Convert: Click the "Convert" button.
4. Results: The converted output will be displayed:
- Binary Output: Full IEEE-754 Binary-128 representation.
- Hexadecimal Output: Hexadecimal representation of the floating-point value.
- Special Case: Identifies if the result falls into a special case category.
5. Clear: Use the "Clear" button to reset the input fields.
6. Export Output: Click the "Output as .txt" button to save conversion details.