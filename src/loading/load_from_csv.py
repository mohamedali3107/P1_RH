import pandas as pd

def load_csv(csv_file) :
    return pd.read_csv(csv_file)

def list_of_fields_csv(csv_file) :
    return list(csv_file)

def labels_from_csv(csv_file, label_field="Filename") :
    return list(csv_file[label_field].values)

def load_field_data_from_csv(csv_file, label, field) :
    '''Read a specified value in a csv'''
    table = csv_file[csv_file["Filename"]==label][field].values # should contain only one value
    try :
        return table[0]
    except IndexError :
        print("Error : association file name / field does not exist")
        return ""

def meta_of_file_from_csv(csv_file, label) :
    '''Output metadata to be used as key in dict_db'''
    fields = list_of_fields_csv(csv_file)
    field_first_name, field_family_name = fields[2], fields[3]
    first_name= load_field_data_from_csv(csv_file, label, field_first_name)
    family_name = load_field_data_from_csv(csv_file, label, field_family_name)
    if first_name == 'Unknown' or family_name == 'Unknown' :
        return label
    return first_name + ' ' + family_name

def update_pool_loaded_CV(all_loaded_CV, label, meta) :  # todo : meta ou label ?
    all_loaded_CV[label] = meta  # maybe pre-existant but ok

def update_dict_with_field_value(dict_db, field, value, meta) :  # keep tests ?
    '''Add a value from a structured CV to the corresponding field of the dictionary
    Ideally value_with_meta should contain a value and a metadata'''
    if field not in dict_db :
        dict_db[field] = {meta : value}
    else :
        dict_db[field][meta] = value

def update_dict_with_field_from_csv(dict_db, csv_file, field, all_loaded_CV) :
    labels = labels_from_csv(csv_file)
    for label in labels :
        if label in all_loaded_CV :
            meta = all_loaded_CV[label]
        else :
            meta = meta_of_file_from_csv(csv_file, label)
            all_loaded_CV[label] = meta
        value = load_field_data_from_csv(csv_file, label, field)
        update_dict_with_field_value(dict_db, field, value, meta)
        update_pool_loaded_CV(all_loaded_CV, label, meta)

## il est possible que des cv qui apparaissent dans
## all_loaded_cv et qq part dans dict_db n'aient pas tous les mêmes champs
## uploadés dans dict_db 
## d'où la fonction suivante pour egaliser
## plus flexible mais un peu moche

def equalize_loaded_data(dict_db, all_loaded_CV, csv_file) :
    for label in all_loaded_CV :
        meta = all_loaded_CV[label]
        for field in dict_db :
            if meta not in dict_db[field] :
                value = load_field_data_from_csv(csv_file, label, field)
                update_dict_with_field_value(dict_db, field, value, meta) # redundant test...

def update_dict_with_CV(dict_db, label, csv_file, all_loaded_CV, full=False) :
    '''If new CV added to the pool (csv file was updated)
    Update of already loaded fields with values from new CV
    If full, addition and/or update of all csv fields into dict'''
    meta = meta_of_file_from_csv(csv_file, label)
    if not full :
        for field in dict_db :
            data = load_field_data_from_csv(csv_file, label, field)
            update_dict_with_field_value(dict_db, field, data, meta)
    else :
        list_of_fields = list_of_fields_csv(csv_file)
        for field in list_of_fields :
            data = load_field_data_from_csv(csv_file, label, field)
            update_dict_with_field_value(dict_db, field, data, meta)
    update_pool_loaded_CV(all_loaded_CV, label, meta)

def update_dict_from_csv(dict_db, csv_file, all_loaded_CV, full=False) :
    '''Update with several new CVs (all fields if full, else only already loaded ones)'''
    labels = labels_from_csv(csv_file)
    for label in labels :
        if label not in all_loaded_CV :
            update_dict_with_CV(dict_db, label, csv_file, full=full)
            update_pool_loaded_CV(label)
    equalize_loaded_data(dict_db, all_loaded_CV, csv_file)

def load_full_csv_to_dict(csv_file, dict_db, all_loaded_CV) :
    labels = labels_from_csv(csv_file)
    for label in labels :
        update_dict_with_CV(dict_db, label, csv_file, all_loaded_CV, full=True)
        meta = meta_of_file_from_csv(csv_file, label)
        update_pool_loaded_CV(all_loaded_CV, label, meta)

# todo : prendre en charge la suppression de cv/data