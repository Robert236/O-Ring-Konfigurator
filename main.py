import tkinter as tk
from tkinter import ttk
import json
colors = ['rot', 'blau', 'grün', 'gelb']
supplier = ['Anyseals', 'Dichtomatik', 'Freudenberg', 'PDT']
sub_materials = ['NBR', 'FPM', 'PTFE', 'FFPM']
permission = ['FDA']


def create_matchco(data):
    def clean_number(n):
        n = n.replace(',', '.')
        n = n.rstrip('0').rstrip('.') if '.' in n else n
        n = n.replace('.', ',')
        return n
    template_match = 'or'
    insert_text = []
    for dataset in data:
        insert_text.append(dataset['variable'].get())
    insert_text = insert_text[:len(insert_text) - 2]
    code_book_color = {'rot': 'rt', 'blau': 'bl', 'grün': 'gn', 'gelb': 'gl'}
    code_book_supplier = {'Anyseals': 'any', 'Dichtomatik': 'dm', 'Freudenberg': 'fst', 'PDT': 'pdt'}
    for i, value in enumerate(insert_text):
        if i == 0:
            rv = clean_number(value)
            template_match += rv + '-'
        elif value in colors:
            rv_resolved_col = code_book_color[value]
            template_match += rv_resolved_col
        elif value in supplier:
            rv_resolved_sup = code_book_supplier[value]
            template_match += '-' + rv_resolved_sup
        elif value in permission:
            template_match += '-' + value.lower()
        elif ',' in value:
            rv2 = clean_number(value)
            template_match += rv2
        else:
            template_match += value.lower()
    return template_match


def create_shorttext(data):  # TODO noch den Kurztext in die richtige Reihenfolge bringen.
    template = 'OR'
    insert_text = []
    for dataset in data:
        insert_text.append(dataset['variable'].get())
    insert_text = insert_text[:len(insert_text) - 3]
    code_book_color = {'rot': 'rt', 'blau': 'bl', 'grün': 'gn', 'gelb': 'gl'}
    for i, value in enumerate(insert_text):
        if i == 0:
            template += ' ' + value + ' x'
        elif value in sub_materials:
            template += value
        elif value in colors:
            rv_resolved_col = code_book_color[value]
            template += ' ' + rv_resolved_col
        else:
            template += ' ' + value
    return template


def create_product_hierarchy(data):
    product_hierarchy = '53208'
    header = ['Material', 'Härte', 'Beschichtung', 'Farbe']
    values = {}
    code_book_level_3 = {'ummantelt': '46', 'EPDM': '59', 'FFPM': '60', 'FPM': '61', 'MVQ': '68', 'NBR': '69'}
    code_book_color = {'rot': 'rt', 'blau': 'bl', 'grün': 'gn', 'gelb': 'gl'}
    js = open('code_book_product_hierarchy.json')
    code_book_level_6 = json.load(js)
    for variable in data:
        if variable['description'] in header:
            value = variable['variable'].get()
            if value in code_book_color:
                value = code_book_color[value]
            if value == 'PC':
                value = value + '-'
            values[variable['description']] = value
    material = values['Material']
    code_book_level_3_rv = code_book_level_3[material]
    product_hierarchy += code_book_level_3_rv + '0922' + '1015'
    description_level_6 = material + ' ' + values['Härte'] + ' ' + values['Farbe']
    code_book_level_6_rv = code_book_level_6[description_level_6]
    product_hierarchy += code_book_level_6_rv
    print(code_book_level_3_rv)
    print(description_level_6)
    print(code_book_level_6_rv)
    print(product_hierarchy)
    print(values)


def check_input_syntax(data):
    help_list = ['Durchmesser', 'Schnurstärke', 'Härte', 'EK', 'Kalk.-Menge']
    error_log_correct = []
    error_log_incorrect = []
    for dataset in data:
        if dataset['description'] in help_list:
            if dataset['description'] != 'Härte' and dataset['description'] != 'Kalk.-Menge':
                try:
                    value = dataset['variable'].get()
                    decimal_places = value.split(',')[1]
                    if len(decimal_places) == 2:
                        error_log_correct.append('value correct')
                    else:
                        error_log_incorrect.append('{} - Nur 2-stellige Kommazahl'.format
                                                   (dataset['description'].upper()))
                except IndexError:
                    error_log_incorrect.append('{} - Nur Kommazahlen erlaubt'.format(dataset['description'].upper()))
            else:
                value2 = dataset['variable'].get()
                try:
                    if int(value2) > 9:
                        error_log_correct.append('value correct')
                    else:
                        error_log_incorrect.append('{} - Zahl ist zu klein'.format(dataset['description'].upper()))
                except ValueError:
                    error_log_incorrect.append('{} - nur Ganzzahl'.format
                                               (dataset['description'].upper()))
    check_digit = error_log_correct.count('value correct')
    if check_digit == 5:
        return [True]
    else:
        return False, error_log_incorrect


def process_data(variables, root):
    rv_data = check_input_syntax(variables)
    if rv_data[0]:
        rv_matchco = create_matchco(variables)
        rv_shorttext = create_shorttext(variables)
        rv_product_hierarchy = create_product_hierarchy(variables)
        print(rv_matchco)
        print(rv_shorttext)
    else:
        error_window = tk.Toplevel(root)
        error_window.title("Error")
        error_window.geometry("350x300")
        tk.Label(error_window, text="Eingabefehler", font=("Arial", 18), pady=25).pack()
        for error_message in rv_data[1]:                                            # TODO Was ist hier die Warnung?
            tk.Label(error_window, text=error_message, font=("Arial", 12)).pack()


def create_text_field(root, description, row):
    tk.Label(root, text=description + ": ", pady=3, padx=15).grid(row=row, column=0, sticky="W")
    rv = ttk.Entry(root, width=11)
    rv.grid(row=row, column=1)
    return description, rv


def create_dropdown(root, description, values, row):
    tk.Label(root, text=description + ": ", pady=3, padx=15).grid(row=row, column=0, sticky="W")
    var1 = tk.StringVar(root)
    (ttk.Combobox(root, width=10, textvariable=var1, values=values, state="readonly")
     .grid(row=row, column=1, sticky="W"))
    return description, var1


def load_o_ring(root):
    variables = []
    rv_diameter = create_text_field(root, 'Durchmesser', 1)
    variables.append({'description': rv_diameter[0], 'variable': rv_diameter[1]})
    rv_cord = create_text_field(root, 'Schnurstärke', 2)
    variables.append({'description': rv_cord[0], 'variable': rv_cord[1]})
    rv_material = create_dropdown(root, 'Material', sub_materials, 3)
    variables.append({'description': rv_material[0], 'variable': rv_material[1]})
    rv_hardness = create_text_field(root, 'Härte', 4)
    variables.append({'description': rv_hardness[0], 'variable': rv_hardness[1]})
    rv_coating = create_dropdown(root, 'Beschichtung', ['PC'], 5)
    variables.append({'description': rv_coating[0], 'variable': rv_coating[1]})
    rv_color = create_dropdown(root, 'Farbe', colors, 6)
    variables.append({'description': rv_color[0], 'variable': rv_color[1]})
    rv_permission = create_dropdown(root, 'FDA', permission, 7)
    variables.append({'description': rv_permission[0], 'variable': rv_permission[1]})
    rv_supplier = create_dropdown(root, 'Lieferant', supplier, 8)
    variables.append({'description': rv_supplier[0], 'variable': rv_supplier[1]})
    rv_ek = create_text_field(root, 'EK', 9)
    variables.append({'description': rv_ek[0], 'variable': rv_ek[1]})
    rv_kalk_amount = create_text_field(root, 'Kalk.-Menge', 10)
    variables.append({'description': rv_kalk_amount[0], 'variable': rv_kalk_amount[1]})
    (tk.Button(root, text="Bestätigen", command=lambda: process_data(variables, root))
     .grid(row=11, column=1, sticky="W"))


def collect_data(material_selection, win):
    data_window = tk.Toplevel(win)
    data_window.title("Dateneingabe")
    data_window.geometry("250x330")
    tk.Label(data_window, text="").grid(row=0, column=0)
    material = material_selection.get()
    if material == "O-Ring":
        load_o_ring(data_window)
    elif material == "Wellendichtring":
        print('Hier ist der Code noch nicht erweitert!')
        pass


materials = ['O-Ring', 'Wellendichtring']
main_window = tk.Tk()
main_window.title("Konfigurator")
main_window.geometry("250x200")
tk.Label(main_window, text="Hauptmenü", font=("Arial", 18), pady=25).pack()
var = tk.StringVar(main_window)
ttk.Combobox(main_window, width=15, textvariable=var, values=materials, state="readonly").pack()
tk.Label(main_window, text="").pack()
tk.Button(main_window, text="Bestätigen", command=lambda: collect_data(var, main_window)).pack()
main_window.mainloop()
