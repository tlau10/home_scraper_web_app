import json

def write_to_file(file_path, text):
    """
    writes text to given file
    @param file_path: relative path of file
    @param text: string to write into file
    """
    with open(file_path, "w", encoding = "utf-8") as file:
        file.write(text)

def read_json_file(file_path):
    """
    reads from given json file
    @param file path: relative path of file
    @return: dict object
    """
    with open(file_path, "r", encoding = "utf-8") as file:
        return json.load(file)

def write_json_file(file_path, json_object):
    """
    writes json object to given file
    @param file_path: relative path of file
    @param json_object: json object to write into file
    """
    json_object = json.dumps(json_object, indent = 2)
    print(json_object)
    write_to_file(file_path = file_path, text = json_object)
