import inspect
import subprocess
import sys
import importlib
import re
import os
import json
sys.path.append('../')
from deal_with_text import extract_python_code,get_description_comments, check_empty, remove_comments

def exec_generation(python_file):
        """
        for checking "compilation error
        """
        # file: xx.py
        sys.stdout = open(os.devnull, 'w')
        p = subprocess.Popen(['python', python_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        sys.stdout = sys.__stdout__
        error = error.decode()
        if error == "":
            return [0, None]
        else:
            error_lines = error.splitlines()
            els = error_lines.copy()
            for l in error_lines:
                if l.strip() == "":
                    els.remove(l)
            error_lines = els
            last_line_number = None
            for i in range(len(error_lines) - 1, -1, -1):
                if error_lines[i].find(python_file) != -1:
                    last_line_number = i
                    break
            if error_lines[last_line_number].find("Warning") >= 0:
                return [0, None]
            line_number = re.search(r'line (\d+)', error_lines[last_line_number]).group(1)
            line_content = error_lines[last_line_number + 1].strip()
            error_detail = error_lines[-1].strip()
            return [1, [line_number, line_content, error_detail]]


def extract_class_functions(python_file):
        """
        for checking "lacking detail"
        """

        module_name = (python_file.split(".")[-2]).split("/")[-1]
        # do not output load information
        sys.stdout = open(os.devnull, 'w')
        spec = importlib.util.spec_from_file_location(module_name, python_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # recover output info
        sys.stdout = sys.__stdout__
        members = inspect.getmembers(module)
        empty_functions = []

        class_members = []
        function_members = []
        for name, member in members:
            t = (name, member)
            if inspect.isclass(member) and member.__module__ == module_name:
                class_members.append(t)
            elif inspect.isfunction(member) and member.__module__ == module_name:
                function_members.append(t)

        for name, member in class_members:
            # if inspect.isclass(member):
            class_own_members = inspect.getmembers(member)
            for class_member_name, class_member in class_own_members:
                if inspect.isfunction(class_member) and class_member.__module__ == module_name:
                    source = inspect.getsource(class_member)
                    description = get_description_comments(source)
                    source = remove_comments(source)
                    empty = check_empty(source)
                    if empty:
                        # return empty functions (class name, function name)
                        empty_functions.append([name, class_member_name, description])
        for name, member in function_members:
            # if inspect.isfunction(member) and not inspect.isbuiltin(member) and member.__module__ == module_name:
            source = inspect.getsource(member)
            description = get_description_comments(source)
            source = remove_comments(source)
            empty = check_empty(source)
            if empty:
                # return empty functions (class name, function name)
                empty_functions.append(["", name, description])
        return empty_functions