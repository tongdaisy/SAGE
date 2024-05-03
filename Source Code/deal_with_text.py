import inspect
import subprocess
import sys
import importlib
import re
import os
import json
from verifier_level2_function import verification


def extract_python_code(text):
    pattern = r"```python\s+(.*?)\s+```"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    clean_text = ""
    if len(matches) == 0:
        clean_text = text
    else:
        clean_text = matches[0]
    return clean_text


def get_description_comments(code):
    source_lines = code.splitlines()
    start_line = 1
    comments = []

    in_multiline_comment = False

    for line in source_lines[start_line:]:
        line = line.strip()
        if line == "":
            continue
        if (line.startswith('"""') and line.endswith('"""') and len(line) > 3) or (
                line.startswith('\'\'\'') and line.endswith('\'\'\'') and len(line) > 3):
            comments.append(line[3:-3])
            continue
        elif (line.startswith('"""') or line.startswith('\'\'\'')) and in_multiline_comment == False:
            in_multiline_comment = True
            comments.append(line[3:])
            continue
        elif (line.startswith('"""') or line.startswith('\'\'\'')) and in_multiline_comment == True:
            in_multiline_comment = False
            continue
        elif (line.endswith('"""') or line.endswith('\'\'\'')) and in_multiline_comment == True:
            in_multiline_comment = False
            comments[-1] += line[:-3]
            continue
        elif line.startswith('#'):
            comments.append(line[1:])
            continue
        if in_multiline_comment:
            comments[-1] += (" " + line)
        else:
            break
    description = "".join(comments)
    return description


def replace_function_code(filename, class_name, function_name, new_code):
    # through replace the new_code into pass
    with open(filename, 'r') as file:
        lines = file.readlines()

    class_start_line = None
    class_end_line = None

    for i, line in enumerate(lines):
        if line.strip().startswith('class ' + class_name):
            class_start_line = i
        elif class_start_line is not None:
            x = line.strip()
            if x[0] == line[0]:
                class_end_line = i
                break

    if class_start_line is not None and class_end_line is not None:
        function_start_line = None
        function_end_line = None

        for i in range(class_start_line + 1, class_end_line):
            line = lines[i]
            if line.strip().startswith('def ' + function_name):
                function_start_line = i
            elif function_start_line is not None and line.strip().startswith('def'):
                function_end_line = i
                break
            elif function_start_line is not None and i == class_end_line:
                function_end_line = i + 1
                break

        if function_start_line is not None and function_end_line is not None:
            lines[function_start_line + 1:function_end_line] = new_code.splitlines(keepends=True)

            with open(filename, 'w') as file:
                file.writelines(lines)
        else:
            print(f"Function '{function_name}' not found in class '{class_name}'.")
    else:
        print(f"Class '{class_name}' not found.")


def check_empty(code):
    match = re.search(r"pass", code)
    lines = code.splitlines()
    context = lines[1]
    text_without_tabs = re.sub(r'\s+', '', context)
    if text_without_tabs == "pass" or text_without_tabs == "..." or text_without_tabs == "_" or match:
        # no specific code
        return True
    if text_without_tabs == "return":
        return True
    return False


def remove_comments(code):
    # remove singleline comments
    code = re.sub(r'(?<!\\)(#.*?$)', '', code, flags=re.MULTILINE)
    # remove multiline comments
    code = re.sub(r'(?<!\\)(""".*?""")', '', code, flags=re.DOTALL)
    code = re.sub(r'(?<!\\)(\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)
    code = re.sub(r'\n\s*\n', '\n', code)
    code = code.strip()
    return code

def solution_modified_extract(text, gen):
    solutions_match = re.search(r"Solutions(.*?)Modified Program:", text, re.DOTALL)
    solutions_content = ""
    if solutions_match:
        solutions_content = solutions_match.group(1).strip()

    modified_program_content = gen.extract_python_code(text)
    return solutions_content, modified_program_content


def get_self_variables(code):
    # will involve
    all_variables = re.findall(r'self\.(\w+)', code)
    regex_pattern = r"self\.(\w+)\s*=\s*.*?\#\s*(.*)"
    matches = re.findall(regex_pattern, code, re.MULTILINE)  # [match_name,match comment]
    # 使用正则表达式提取函数调用的名称
    error_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\('
    error_match = re.findall(error_pattern, code)
    # error_match=[]
    self_variables = []
    self_variables_dict = []
    # 去重并添加到结果列表中
    for [v, v_comment] in matches:
        if v not in error_match and v not in self_variables:
            self_variables.append(v)
            self_variables_dict.append({"name": v, "description": v_comment})
    for v in all_variables:
        if v not in self_variables:
            self_variables_dict.append({"name": v, "description": ""})

    return self_variables_dict
    # return self_variables


def extract_class_functions_2(file_path):
    module_name = (file_path.split(".")[-2]).split("/")[-1]
    classes = []
    funcs = []
    schedule = ""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    # do not output load information
    sys.stdout = open(os.devnull, 'w')
    # try:
    spec.loader.exec_module(module)
    # except:
    # pass
    # recover output info
    sys.stdout = sys.__stdout__
    # 获取模块中所有的成员
    class_line_info = {}
    with open(file_path, 'r', encoding="gbk", errors="replace") as file:
        lines = file.readlines()
        """except:
            text = file.read()
            print(len(text))
            print(text[3900:4119])
            exit()"""
        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith('class'):
                class_start_line = line_num
                class_name = (line.split('class ')[1].split(':')[0].strip()).split("(")[0]
                class_line_info[class_name] = class_start_line
    members = inspect.getmembers(module)
    class_members = []
    function_members = []
    for name, member in members:
        t = (name, member)
        if inspect.isclass(member) and member.__module__ == module_name:
            class_members.append(t)
        elif inspect.isfunction(member) and member.__module__ == module_name:
            function_members.append(t)
    class_members = sorted(class_members, key=lambda m: class_line_info[m[0]])
    function_members = sorted(function_members, key=lambda m: inspect.getsourcelines(m[1])[1])
    # 根据源代码行排序成员列表
    # members = inspect.getmembers(module)
    empty_functions = []
    for name, member in class_members:
        class_info = {
            'name': name,
            'states': [],
            'interactions & activities': [],
        }
        # 获取类中所有的成员
        one_class_members = inspect.getmembers(member)
        method_members = [item for item in one_class_members if
                          (inspect.isfunction(item[1]) and item[1].__module__ == module_name)]
        method_members = sorted(method_members, key=lambda m: inspect.getsourcelines(m[1])[1])
        for method_name, method_member in method_members:
            if method_name == "__init__":
                source = inspect.getsource(method_member)
                class_info['states'] = get_self_variables(source)
                continue
            method = {"name": method_name}
            source = inspect.getsource(method_member)
            description = get_description_comments(source)
            method["description"] = ""
            source = remove_comments(source)
            empty = check_empty(source)
            if empty:
                empty_functions.append([name, method_name])
            class_info['interactions & activities'].append(method)
        if name == "simulation":
            schedule = class_info
            continue
        classes.append(class_info)
    for name, member in function_members:
        func_info = {
            'name': name,
        }
        source = inspect.getsource(member)
        description = get_description_comments(source)
        func_info["description"] = ""
        if name == "simulation":
            schedule = func_info
            continue
        funcs.append(func_info)
    return classes, funcs, schedule, empty_functions


def get_files_in_folder(folder_path):
    files_info = []
    # file_info: file_name, file_description, mesa true, info
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)) and file_name.endswith(".py"):
            file_info = []
            file_info.append(file_name)
            print(file_name)
            with open(os.path.join(folder_path, file_name), 'r', encoding='gbk', errors="replace") as f:
                lines = f.readlines()
                file_info.append(lines[0].split("#", 1)[-1].strip())
                mesa = lines[1].split("#", 1)[-1].strip()
                if mesa == "mesa":
                    file_info.append(True)
                else:
                    file_info.append(False)
        files_info.append(file_info)
        # extract_class_functions(os.path.join(folder_path, file_name))
    return files_info


def generate_prompt_4_each_file(python_file):
    classes, funcs, schedule, empty = extract_class_functions_2(python_file)
    total_des = {"Objects Definition": classes, "Functions": funcs, "Simulation & Schedules": schedule,
                 "Example Usage": ""}
    total_des = json.dumps(total_des)
    hint = False
    with open(python_file, 'r', encoding='gbk', errors="replace") as f:
        lines = f.readlines()
        abm_info = lines[0].split("#", 1)[-1].strip()
        mesa = lines[1].split("#", 1)[-1].strip()
        if mesa == "mesa":
            hint = True
    with open("template/model_generation_template.txt", 'r') as f:
        prompt = f.read()
    prompt += abm_info
    if hint:
        prompt += (" according to the following requirements. You should use package \"mesa\" to program the model. \n")
    else:
        prompt += (" according to the following requirements.\n")
    prompt += ("Programming Language: Python;\nRequirements:\n")
    prompt += (total_des + "\n")
    prompt += ("Program:\n")
    # print(prompt)
    file_path = python_file.split(".")[0]
    file_path += (".txt")
    with open(file_path, 'w') as f:
        f.write(prompt)


def transform_NL(python_file):
    classes, funcs, schedule, empty = extract_class_functions_2(python_file)
    total_des = {"Objects Definition": classes, "Functions": funcs, "Simulation & Schedules": schedule,
                 "Example Usage": ""}
    hint = False
    with open(python_file, 'r', encoding='gbk', errors="replace") as f:
        lines = f.readlines()
        abm_info = lines[0].split("#", 1)[-1].strip()
        mesa = lines[1].split("#", 1)[-1].strip()
        if mesa == "mesa":
            hint = True
    with open("template/NL_model_generation_template.txt", 'r') as f:
        NL_des = f.read()
    NL_des += abm_info + ". This ABM should compose "
    for c in classes:
        NL_des += c["name"] + ", "
    for c in classes:
        if len(c["states"]) > 0:
            NL_des += "The " + c["name"] + " are described by "
            for v in c["states"]:
                NL_des += v["name"] + ", "
        if len(c["interactions & activities"]) > 0:
            NL_des += "The " + c["name"] + " should have activities: "
            for m in c["interactions & activities"]:
                NL_des += m["name"] + ", "
    if len(funcs) > 0:
        NL_des += "You can build "
        for f in funcs:
            NL_des += f["name"] + ", "
        NL_des += "to help model. "
    if hint:
        NL_des += "You can also use package mesa to help model."
    NL_des += "\nProgramming Language: Python.\n"
    NL_des += "Progam:\n"

    file_path = python_file.split(".")[0]
    nl_file_path = file_path + ("_NL.txt")
    with open(nl_file_path, 'w') as f:
        f.write(NL_des)
    return NL_des


def transform_question_NL(question_file, original_model_file, write_file):
    with open(question_file, 'r') as f:
        objectives_rep = f.read()
    objectives_rep = json.loads(objectives_rep)
    model_des = objectives_rep["model"]
    problem = objectives_rep["problem"]
    requirements = objectives_rep["criteria"]
    with open("template/NL_solving_template.txt",'r') as f:
        template=f.read()

    template += "\nTask: There is an agent-based model that simulates the " + model_des + ". "
    template += "The problem we want to address is \"" + problem + "\". The desired performance of the original program is: "
    for r_num, r in enumerate(requirements):
        template += "as variable" + "\"" + r["variable_name"] + "\", " + r["requirement"] + ", "
    template += "Please give some solutions to address this problem, and then modify the original program according to the solutions.\n"
    template += "Original_Program: \n"
    with open(original_model_file, 'r') as f:
        original_model = f.read()
    template += original_model
    template += "\n\nSolutions & Modified Problem:\n"
    with open(write_file,'w') as f:
        f.write(template)


# for open-ended solution generation sage
    """for file_path in os.listdir(folder_path):
        if file_path.startswith("question"):
            file_index = (file_path.split(".")[0]).split("_")[1]
            if int(file_index) <13:
                continue
            iter_num = 3
            original_program_path=folder_path + "/" + "original_model_" + file_index + ".py"
            question_path=folder_path + "/" + file_path
            while iter_num > 0:
                x,solutions,modified_program=gen.OE_Solving(original_program_path,question_path)
                with open(folder_path + "/sage_gpt4/" + "answer_" + file_index + "_" + str(iter_num) + ".py", 'w') as f:
                    f.write(modified_program)
                with open(folder_path + "/sage_gpt4/" + "solution_" + file_index + "_" + str(iter_num) + ".py", 'w') as f:
                    f.write(solutions)
                if x==1:
                    with open(folder_path + "/sage_gpt4/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + str(iter_num) + "\t" + "Success" + "\n")
                else:
                    with open(folder_path + "/sage_gpt4/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + str(iter_num) + "\t" + "Compilation Error" + "\n")
                iter_num-=1"""
    """# for open-ended solution generation
    for file_path in os.listdir(folder_path):
        if file_path.startswith("question"):
            file_index = (file_path.split(".")[0]).split("_")[1]
            if int(file_index) != 15:
                continue
            with open(folder_path + "/" + file_path, 'r') as f:
                des = json.loads(f.read())
                model_des = des["model"]
                problem = des["problem"]

            iter_num = 3
            while iter_num > 0:
                print(file_index + ":\t" + str(3 - iter_num))
                iter_num -= 1
                gen.prompt = "Task:\nThere is a agent-based model that simulates " + model_des
                gen.prompt += ". Please modify the original model to address this problem: \"" + problem + "\".\n"
                gen.prompt += "Original model:\n"
                with open(folder_path + "/" + "original_model_" + file_index + ".py", 'r') as f:
                    original_model = f.read()
                gen.prompt += original_model
                gen.prompt += "\nModified Model:"
                answer = gen.ask_prompt(gen.prompt, 0)
                # solutions, modified_program = solution_modified_extract(answer, gen)
                with open(folder_path + "/NL_gpt4/" + "answer_" + file_index + "_" + str(iter_num) + ".py", 'w') as f:
                    f.write(answer)
                try:
                    errors = gen.exec_generation(
                        python_file=folder_path + "/NL_gpt4/" + "answer_" + file_index + "_" + str(iter_num) + ".py")
                except:
                    print("execution error")
                    with open(folder_path + "/NL_gpt4/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + str(iter_num) + "\t" + "False: execution errors" + "\n")
                    continue
                if errors[0] == 1:
                    print("execution error")
                    with open(folder_path + "/NL_gpt4/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + str(iter_num) + "\t" + "False: execution errors" + "\n")"""

    """for file_path in os.listdir(folder_path):
        if file_path.startswith("NL_prompt"):
            file_index = (file_path.split(".")[0]).split("_")[-1]
            if int(file_index) <1 :
                continue
            with open(folder_path + "/" + file_path, 'r') as f:
                gen.prompt = f.read()
            with open("ABM_dataset/Problems_Solutions/verification_level2_" + file_index + ".py", 'r') as f:
                vl = f.read()
            with open("verification_level22.py", 'w') as f:
                f.write(vl)
            with open(folder_path + "/" + "question_" + file_index + ".txt", 'r') as f:
                objectives_rep = f.read()
            iter_num = 5
            while iter_num > 0:
                print(file_index + ":\t" + str(6 - iter_num))
                iter_num -= 1
                with open(folder_path + "/" + file_path, 'r') as f:
                    gen.prompt = f.read()
                answer = gen.ask_prompt(0, False)
                solutions, modified_program = solution_modified_extract(answer, gen)
                with open(folder_path + "/gpt_4_NL/" + "answer_" + file_index +"_"+str(iter_num) +".py", 'w') as f:
                    f.write(modified_program)
                with open(gen.answer_file, 'w') as f:
                    f.write(modified_program)
                with open(folder_path + "/gpt_4_NL/" + "solutions_" + file_index + ".txt", 'w') as f:
                    f.write(solutions)
                errors = gen.exec_generation()
                if errors[0] == 1:
                    print("execution error")
                    with open(folder_path + "/gpt_4_NL/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + "False: execution errors" + "\n")
                    continue
                loc = {}
                sys.stdout = open(os.devnull, 'w')
                exec(modified_program, loc)
                sys.stdout = sys.__stdout__
                real_value = []
                objectives_rep = json.loads(objectives_rep)
                requirements = objectives_rep["criteria"]
                for req in requirements:
                    v_name = req["variable_name"]
                    if v_name in loc.keys():
                        real_value.append(loc[v_name])
                    else:
                        real_value.append(None)
                if None in real_value:
                    print("verifier error")
                    with open(folder_path + "/gpt_4_NL/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + "False: veri_errors" + "\n")
                    continue
                ite_flag = False
                while_iter = 0
                try:
                    veri_results = choose_veri(int(file_index),real_value)
                    print(veri_results)
                except:
                    print("veri_error")
                    while_iter += 1
                    if while_iter > 10:
                        exit()
                    continue
                for vr in veri_results:
                    if vr == False:
                        ite_flag = True
                        break
                if ite_flag:
                    with open(folder_path + "/gpt_4_NL/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + "False: veri_errors" + "\n")
                    continue
                else:
                    with open(folder_path + "/gpt_4_NL/" + "results.txt", 'a') as f:
                        f.write(file_index + "\t" + "True" + "\n")
                    break"""
    """for file_path in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_path)) and file_path.startswith("question_"):
            file_name = file_path.split(".")[0]
            file_index = file_name.split("_")[1]
            print("file:", file_index)
            if int(file_index) != 9:
                continue
            with open("ABM_dataset/Problems_Solutions/original_model_" + file_index + ".py", 'r') as f:
                original_model = f.read()
            iter_time = 0
            with open("ABM_dataset/Problems_Solutions/verification_level2_" + file_index + ".py", 'r') as f:
                vl = f.read()
            with open("verification_level2.py", 'w') as f:
                f.write(vl)
            while iter_time < 4:
                results = gen.iterative_generation_2("ABM_dataset/Problems_Solutions/original_model_" + file_index + ".py", os.path.join(folder_path, file_path),
                                                     whether_pass=1,file_index=int(file_index))
                iter_time += 1
                print("iter: ", iter_time)
                solution_file = folder_path + "/gpt_4_sage/solutions_" + str(file_index) + ".txt"
                with open(solution_file, 'w') as f:
                    f.write(results[1])
                program_file = folder_path + "/gpt_4_sage/answer_" + str(file_index) + ".py"
                with open(program_file, 'w') as f:
                    f.write(results[2])
                results_file = folder_path + "/gpt_4_sage/results.txt"
                with open(results_file, 'a') as f:
                    f.write(file_index + "\t" + str(results[0]) + "\n")
                if results[0]:
                    break"""

    """folder_path = "ABM_dataset"
    for file_path in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_path)) and file_path.endswith(".txt") and not file_path.endswith("NL.txt"):
            file_index = file_path.split(".")[0]
            if file_index == "result" or int(file_index) <42:
                continue
            with open(os.path.join(folder_path, file_path), 'r', encoding='gbk', errors="replace") as f:
                prompt = f.read()
            regen = 0
            print(file_index)
            while (regen < 3):
                print("\t" + str(regen))
                with open(os.path.join("ABM_dataset/gpt4_answer", "result.txt"), 'a') as f:
                    f.write(file_index + "\t" + str(regen) + "\n")
                gen_flag = gen.model_generation(None, None, 0, prompt)
                with open(gen.answer_file, 'r') as f:
                    anwser = f.read()
                answer_path = "answer_" + file_index + "_" + str(regen) + ".py"
                with open(os.path.join("ABM_dataset/gpt4_answer", answer_path), 'w') as f:
                    f.write(anwser)
                with open(os.path.join("ABM_dataset/gpt4_answer", "result_2.txt"), 'a') as f:
                    f.write(file_index + "\t" + str(gen_flag) + "\n")
                regen += 1
                if regen == 3 or gen_flag==1:
                    break"""
    # folder_path = "ABM_dataset/gpt4_answer"
    """folder_path = "evaluation_test/pred_sage_llama"
    total_file = 0
    no_pass_file = 0
    no_error_file = 0
    for file_path in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_path)) and file_path.endswith("py"):
            file_index = (file_path.split(".")[0]).split("_")[1]
            if int(file_index)<37:
                continue
            total_file += 1
            with open(os.path.join(folder_path, file_path), 'r') as f:
                anwser = f.read()
            with open(gen.answer_file, 'w') as f:
                f.write(anwser)
            error_flag = gen.exec_generation()[0]
            try:
                pass_flag = len(gen.extract_class_functions(gen.answer_file))
            except:
                pass_flag = check_empty(anwser)
            if error_flag == 0:
                error_flag = True
                no_error_file += 1
            else:
                error_flag = False
            if pass_flag == 0 or pass_flag==False:
                pass_flag = True
                no_pass_file += 1
            else:
                pass_flag = False
            print(file_path + "\t" + str(error_flag) + "\t" + str(pass_flag))
            print("current_num" + "\t" + str(no_error_file) + "\t" + str(no_pass_file))"""
    # print(gen.exec_generation())
