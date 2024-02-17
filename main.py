import tkinter as tk
from tkinter import ttk
import json
# import pandas as pd

colors = ['rot', 'blau', 'grün', 'gelb']
supplier = ['Anyseals', 'Dichtomatik', 'Freudenberg', 'PDT', 'Arcus']
sub_materials = ['NBR', 'FPM', 'PTFE', 'FFPM', 'EPDM', 'MVQ']
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
    insert_text = insert_text[:len(insert_text) - 3]
    code_book_color = {'rot': 'rt', 'blau': 'bl', 'grün': 'gn', 'gelb': 'gl'}
    code_book_supplier = {'Anyseals': 'any', 'Dichtomatik': 'dm', 'Freudenberg': 'fst', 'PDT': 'pdt',
                          'Arcus': 'arc'}
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


def create_shorttext(data):
    template = 'OR'
    code_book_color = {'rot': 'rt', 'blau': 'bl', 'grün': 'gn', 'gelb': 'gl'}
    insert_text = []
    for dataset in data:
        insert_text.append(dataset['variable'].get())
    insert_text = insert_text[:len(insert_text) - 4]
    if '' in insert_text:
        x = insert_text.count('')
        for e in range(x):
            insert_text.remove('')
    if 'PC' in insert_text:
        x = insert_text.index('PC')
        value_pc = insert_text.pop(x)
        insert_text.insert(3, value_pc)
    for i, value in enumerate(insert_text):
        if i == 0:
            template += ' ' + value + ' x'
        elif value in colors:
            rv_resolved_col = code_book_color[value]
            template += ' ' + rv_resolved_col
        elif value == 'PC':
            template += value
        else:
            template += ' ' + value
    return template


def create_product_group(data):
    product_group = None
    material = data['Material']
    hardness = data['Härte']
    if material == 'NBR':
        attachment = material + hardness
        if attachment == 'NBR70':
            product_group = '147001000'
        else:
            product_group = '147002000'
    elif material == 'FPM':
        hardness_short = hardness[0]
        if int(hardness_short) <= 7:
            product_group = '147005000'
        else:
            product_group = '147006000'
    elif material == 'EPDM':
        product_group = '147007000'
    elif material == 'MVQ':
        product_group = '147008000'
    return product_group


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
                value = '-' + value
            values[variable['description']] = value
    rv_product_group = create_product_group(values)
    material = values['Material']
    code_book_level_3_rv = code_book_level_3[material]
    product_hierarchy += code_book_level_3_rv + '09221015'
    status = {'Material': None, 'Härte': None, 'Beschichtung': None, 'Farbe': None}
    for value_e in values:
        if values[value_e] != '':
            status[value_e] = True
    try:
        if status['Material'] and status['Beschichtung'] and status['Härte'] and status['Farbe'] is None:
            key = values['Material'] + values['Beschichtung'] + ' ' + values['Härte']
            code_book_level_6_rv = code_book_level_6[key]
            product_hierarchy += code_book_level_6_rv
        elif status['Material'] and status['Härte'] and status['Farbe'] and status['Beschichtung'] is None:
            key = values['Material'] + ' ' + values['Härte'] + ' ' + values['Farbe']
            code_book_level_6_rv = code_book_level_6[key]
            product_hierarchy += code_book_level_6_rv
        elif status['Material'] and status['Härte'] and status['Farbe'] and status['Beschichtung']:
            key = values['Material'] + ' ' + values['Härte'] + ' ' + values['Farbe']
            code_book_level_6_rv = code_book_level_6[key]
            product_hierarchy += code_book_level_6_rv
        else:
            key = values['Material'] + ' ' + values['Härte']
            code_book_level_6_rv = code_book_level_6[key]
            product_hierarchy += code_book_level_6_rv
        return product_hierarchy, rv_product_group, values['Material']
    except KeyError:
        return 'error'


def check_input_syntax(data):
    help_list = ['Durchmesser', 'Schnurstärke', 'Härte', 'EK', 'Kalk.-Menge', 'PLZ']
    error_log_correct = []
    error_log_incorrect = []
    for dataset in data:
        if dataset['description'] in help_list:
            if dataset['description'] != 'Härte' and dataset['description'] != 'Kalk.-Menge'\
                    and dataset['description'] != 'PLZ':
                try:
                    value = dataset['variable'].get()
                    decimal_places = value.split(',')[1]
                    if len(decimal_places) == 2:
                        error_log_correct.append('value correct')
                    else:
                        error_log_incorrect.append('{} - Nur 2-stellige Kommazahl'.format
                                                   (dataset['description'].upper()))
                except IndexError:
                    error_log_incorrect.append('{} - Nur Kommazahlen'.format(dataset['description'].upper()))
            else:
                value2 = dataset['variable'].get()
                try:
                    if int(value2):
                        error_log_correct.append('value correct')
                    else:
                        error_log_incorrect.append('{} - Wert eintragen'.format(dataset['description'].upper()))
                except ValueError:
                    error_log_incorrect.append('{} - nur Ganzzahl'.format
                                               (dataset['description'].upper()))
    check_digit = error_log_correct.count('value correct')
    if check_digit == 6:
        return False
    else:
        return error_log_incorrect


def calculate_ek(data):
    price_container = ['EK', 'Preiseinheit']
    multipliers = [10, 15, 20, 25]
    ek = None
    for dataset in data:
        if dataset['description'] == 'EK':
            ek = dataset['variable'].get()
    ek = ek.replace(',', '.')
    ek_per_piece = float(ek) / 100
    if ek_per_piece < 0.10:
        for multi in multipliers:
            ek_per_piece_new = ek_per_piece * multi
            if ek_per_piece_new >= 0.10:
                xx = [round(ek_per_piece_new, 2), multi]
                xx = dict(zip(price_container, xx))
                return xx
            else:
                pass
    else:
        xx = [round(ek_per_piece, 2), 1]
        xx = dict(zip(price_container, xx))
        return xx


def overhead_group(data):
    code_book_supplier = {'Anyseals': '0', 'Dichtomatik': '0', 'Freudenberg': '1,5', 'PDT': '0', 'Arcus': '1,5'}
    supplier_name = None
    for dataset in data:
        if dataset['description'] == 'Lieferant':
            supplier_name = dataset['variable'].get()
    return code_book_supplier[supplier_name]


def get_plz(data):
    for dataset in data:
        if dataset['description'] == 'PLZ':
            return dataset['variable'].get()


def get_kalk_amount(data):
    for dataset in data:
        if dataset['description'] == 'Kalk.-Menge':
            return dataset['variable'].get()


def process_data(variables, root):
    rv_data = check_input_syntax(variables)
    if rv_data:
        error_window = tk.Toplevel(root)
        error_window.title("Error")
        error_window.geometry("350x300")
        tk.Label(error_window, text="Eingabefehler", font=("Arial", 18), pady=25).pack()
        for error_message in rv_data:
            tk.Label(error_window, text=error_message, font=("Arial", 12)).pack()
    else:
        rv_product_hierarchy = create_product_hierarchy(variables)
        if rv_product_hierarchy == 'error':
            error_window = tk.Toplevel(root)
            error_window.title("Error")
            error_window.geometry("200x100")
            tk.Label(error_window, text="Hierarchie Fehler", font=("Arial", 18), pady=25).pack()
        else:
            rv_matchco = create_matchco(variables)
            rv_shorttext = create_shorttext(variables)
            rv_ek = calculate_ek(variables)
            rv_overhead_group = overhead_group(variables)
            rv_plz = get_plz(variables)
            rv_kalk_amount = get_kalk_amount(variables)
            temp = open('template.json', 'r')
            temp = json.load(temp)
            temp['Materialkurztext'] = rv_shorttext
            temp['Warengruppe'] = rv_product_hierarchy[1]
            temp['Produkthierarchie'] = rv_product_hierarchy[0]
            temp['Texteditor Textzeile'] = rv_shorttext
            temp['Matchcode'] = rv_matchco
            temp['Werkstoff'] = rv_product_hierarchy[2]
            temp['Planlieferzeit in Tagen'] = rv_plz
            temp['Gleitender Durchschnittspreis/Periodischer Verrechnungspreis'] = rv_ek['EK']
            temp['Preiseinheit'] = rv_ek['Preiseinheit']
            temp['Preiseinheit der steuerr. und handelsr. Bewertungspreise'] = rv_ek['Preiseinheit']
            temp['Gemeinkostengruppe der Kalkulation'] = rv_overhead_group
            temp['Losgröße der Erzeugniskalkulation'] = rv_kalk_amount
            out_put_file = open('Output_O_Ring.json', 'w')
            json.dump(temp, out_put_file)
            out_put_file.close()


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
    planned_delivery_time = create_text_field(root, 'PLZ', 11)
    variables.append({'description': planned_delivery_time[0], 'variable': planned_delivery_time[1]})
    (tk.Button(root, text="Bestätigen", command=lambda: process_data(variables, root))
     .grid(row=12, column=1, sticky="N"))


def collect_data(material_selection, win):
    data_window = tk.Toplevel(win)
    data_window.title("Dateneingabe")
    data_window.geometry("250x350")
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
