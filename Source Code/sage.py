import ast
import inspect
import subprocess
import openai
import sys
import importlib
import re
import os
import json
from deal_with_text import extract_python_code,get_description_comments, check_empty, remove_comments


os.environ["HTTP_PROXY"] = "Your settings if needed"
os.environ["HTTPS_PROXY"] = "Your settings if needed"
openai.api_key = "Your API_key"


class Chatgpt():
    def __init__(self):
        # initialize message
        self.init_message = [
            {"role": "system",
             "content": "If your answer contains python code, python code should be stated in ```python ```.  \n"}]
        # A python code generator, you can just provide code, no natural language.

    def ask(self, msg):
        current_msg = self.init_message + msg
        # get api
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=current_msg
        )
        answer = rsp.get("choices")[0]["message"]["content"]
        return answer


class ABM_generate():

    def __init__(self, template_dir, gpt, tol_regen, solving_iter_max):
        self.gpt = gpt
        self.prompt = ""
        self.answer = ""
        self.answer_file = "answer.py"
        self.critier = []
        self.template_dir = template_dir
        self.priors = []
        self.tol_regen = tol_regen
        self.solving_iter_max=solving_iter_max
        pass

    def ask_prompt(self, prior_num, extract=True):
        """

        :param gpt:
        :param prior_num:
        :param extract: bool, default extract=True, wheter extract python code from LLM answer
        :return:
        """
        n_prior = min(prior_num, len(self.priors))
        prior_messages = []
        for i in range(n_prior):
            prior_messages += self.priors[len(self.priors) - n_prior + i]
        prior_messages.append({"role": "user", "content": self.prompt})

        gpt = Chatgpt()
        self.gpt = gpt
        answer = gpt.ask(prior_messages)
        if extract:
            self.answer = extract_python_code(answer)
        else:
            self.answer = answer
        self.priors.append([
            {"role": "user", "content": self.prompt},
            {"role": "assistant", "content": answer},
        ])
        self.prompt = ""
        return self.answer

    def exec_generation(self, python_file=None):
        """
        for checking "compilation error
        """
        # file: xx.py
        sys.stdout = open(os.devnull, 'w')
        if python_file is None:
            python_file = self.answer_file
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
                if error_lines[i].find(self.answer_file) != -1:
                    last_line_number = i
                    break
            if error_lines[last_line_number].find("Warning") >= 0:
                return [0, None]
            line_number = re.search(r'line (\d+)', error_lines[last_line_number]).group(1)
            line_content = error_lines[last_line_number + 1].strip()
            error_detail = error_lines[-1].strip()
            return [1, [line_number, line_content, error_detail]]

    def error_prompt(self, error_info, file):
        with open(file, 'r', encoding='utf-8') as f:
            code = f.read()
        prompt = "There is an execution error in the original code. The error is in Line " + error_info[
            0] + ": " + error_info[1]
        """if error_info[2] != "":
            prompt += ", which is in the function " + error_info[2]"""
        prompt += ". The error reason is: " + error_info[2] + ". Please correct this error.\r\n"
        prompt += "The original complete model program:\r\n"
        prompt += code
        prompt += "\r\n"
        prompt += "The modified complete model program:"
        # print(prompt)
        return prompt


    def extract_class_functions(self, file_path):
        """
        for checking "lacking detail"
        """

        module_name = (file_path.split(".")[-2]).split("/")[-1]
        # do not output load information
        sys.stdout = open(os.devnull, 'w')
        spec = importlib.util.spec_from_file_location(module_name, file_path)
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


    def complete_pass_prompt(self, empty_function, code_file):
        """
        :param pass_template: file path, template will be complated
        :param empty_function: functions only have pass
        :param descriptions: for each empty function
        :return:
        """
        pass_template = self.template_dir + "complete_pass_template.txt"
        with open(pass_template, 'r') as f:
            template = f.read()
        req = []
        for i, func in enumerate(empty_function):
            req.append({"class": func[0], "method": func[1], "description": func[2]})
        template += ("Requirements: ")
        req = json.dumps(req)
        template += req
        template += ("\nOriginal agent-based model:\n")
        with open(code_file, 'r') as f:
            code = f.read()
        template += code
        template += ("\nModified Model:\n")
        self.prompt = template
        return self.prompt

    def verifier_level_1_regen(self, whether_pass):
        num_regen = 0
        while (True):
            error = self.exec_generation()
            num_pass = 0
            if not whether_pass and error[0] == 0:
                empty_functions = self.extract_class_functions(self.answer_file)
                num_pass = len(empty_functions)
            if (error[0] == 0 and num_pass == 0) or num_regen >= self.tol_regen:
                if num_regen >= self.tol_regen and (error[0] == 1 or num_regen > 0):
                    print("Generation Failed")
                    return 0
                if num_regen <= self.tol_regen and (error[0] == 0 and num_regen == 0):
                    return 1
                break
            else:
                while error[0] == 1 and num_regen < self.tol_regen:
                    error_info = error[1]
                    self.prompt = self.error_prompt(error_info, self.answer_file)
                    print("compile error", num_regen)
                    answer = self.ask_prompt(0)
                    with open(self.answer_file, 'w') as f:
                        f.write(answer)
                    num_regen += 1
                    error = self.exec_generation()
                if not whether_pass and num_regen < self.tol_regen and error[0] == 0:
                    empty_functions = self.extract_class_functions(self.answer_file)
                    while len(empty_functions) > 0 and num_regen < self.tol_regen:
                        self.prompt = self.complete_pass_prompt(empty_functions, self.answer_file)
                        print("pass error", num_regen)
                        answer = self.ask_prompt(0)
                        with open(self.answer_file, 'w') as f:
                            f.write(answer)
                        error = self.exec_generation()
                        if error[0] != 0:
                            break
                        empty_functions = self.extract_class_functions(self.answer_file)
                        num_regen += 1
        return 1

    def model_generation(self, abm_info, total_des, whether_pass):
        """
        :param abm_info: one sentence to describe the ABM
        :param total_des: json that describe the structure and schedule of the abm
        :param whether_pass: whether_pass==1 can have pass; 0: can not have pass
        :return:
        """

        with open(self.template_dir+"model_generation_template.txt", 'r') as f:
            prompt = f.read()
        prompt += abm_info
        prompt += (" according to the following requirements.\n")
        prompt += ("Programming Language: Python;\nRequirements:\n")
        prompt += (total_des + "\n")
        prompt += ("Program:\n")
        self.prompt = prompt
        answer = self.ask_prompt(0)
        print(answer)
        with open(self.answer_file, 'w') as f:
            f.write(answer)
        gen_flag = self.verifier_level_1_regen(whether_pass)
        return gen_flag

    def verfier_level2_function_generation(self, objectives_rep_file):
        with open(objectives_rep_file, 'r') as f:
            objectives_rep = f.read()
        objectives_rep = json.loads(objectives_rep)
        criteria = objectives_rep["criteria"]
        criteria = json.dumps(criteria)
        template_path = self.template_dir + "criteria_generation_template.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        template += ("Objectives Representation:" + criteria + "\n")
        template += "Program:\n"
        self.prompt = template
        answer = self.ask_prompt(0)
        print(answer)
        with open("verifier_level2_function.py", 'w') as f:
            f.write(answer)

    def CD_Solving(self, original_program_file, objectives_rep_file, whether_pass=1):
        iter_num_max=self.solving_iter_max
        iter_num = 0
        gen.verfier_level2_function_generation(objectives_rep_file)
        with open(objectives_rep_file, 'r') as f:
            objectives_rep = f.read()
        with open(original_program_file, 'r') as f:
            original_program = f.read()
        objectives_rep = json.loads(objectives_rep)
        model_des = objectives_rep["model"]
        problem = objectives_rep["problem"]
        requirements = objectives_rep["criteria"]
        final_solutions = ""
        final_program = ""
        while_iter = 0
        while (True):
            with open(self.answer_file, 'w') as f:
                f.write(original_program)
            self.verifier_level_1_regen(whether_pass)
            with open(self.answer_file, 'r') as f:
                original_program = f.read()
            loc = {}
            sys.stdout = open(os.devnull, 'w')
            exec(original_program, loc)
            sys.stdout = sys.__stdout__
            real_value = []
            for req in requirements:
                v_name = req["variable_name"]
                if v_name in loc.keys():
                    real_value.append(loc[v_name])
                else:
                    real_value.append(None)
            ite_flag = False
            try:
                external_file = "verifier_level2_function.py"
                spec = importlib.util.spec_from_file_location("external_module", external_file)
                external_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(external_module)
                veri_results = external_module.verification(real_value)
                print("veri_results:",veri_results )
                while_iter = 0
            except:
                print("verifier_level2_function_generate_error")
                while_iter += 1
                with open(original_program_file, 'r') as f:
                    original_program = f.read()
                if while_iter > 1:
                    exit()
                continue

            for vr in veri_results:
                if vr == False:
                    ite_flag = True
                    break
            if not ite_flag or iter_num > iter_num_max:
                break
            if ite_flag:
                template_path = self.template_dir + "CD_result_prompt_template.txt"
                with open(template_path, 'r') as f:
                    template = f.read()
                template += model_des + ". "
                template += "The problem we want to address is \"" + problem + "\". The desired performance of the original program is: "
                for r_num, r in enumerate(requirements):
                    if veri_results[r_num] == False:
                        template += "as variable" + "\"" + r["variable_name"] + "\", " + r["requirement"] + ", "
                        template += "however, the simulation value is " + str(real_value[r_num]) + ". "

                template += "\nPlease first find relevant methods and variables corresponding to the variable "
                for r_num, r in enumerate(requirements):
                    if veri_results[r_num] == False:
                        template += "\"" + r["variable_name"] + "\","

                # template += "Then analysis reasons that did not satisfy the desired performance, and provide some new solutions through utilizing inherent domain knowledge of "
                # template += "\"" + model_des + "\" to " + "\"" + problem + "\".\n"
                template += "Then please utilize your domain knowledge of " + "\"" + model_des + "\" "
                template += "to analyze the reasons that did not satisfy the desired performance of addressing the problem" + "\"" + problem + "\",  "
                template += "especially analyze what is missing in the existing models that has led to this failure. "
                template += "At last, according to the reasons and domain knowledge, please propose new policies as solutions to the problem we want to address. "
                template += "While providing solutions, do not remove existing methods or change existing parameters, and these solutions need to have practical significance and should not be limited to simple modifications of certain variable values.\n "
                template += "Original program:\n"
                template += original_program
                template += "\nRelevant Relations & Reasons & Solutions:\n"
                self.prompt = template
                answer = self.ask_prompt(0, False)
                final_solutions = answer
                solutions_start = answer.index("Solutions:")
                solutions_text = answer[solutions_start:]
                print(solutions_text)
                template_path = self.template_dir + "solution_2_template.txt"
                with open(template_path, 'r') as f:
                    template = f.read()
                template += (
                        solutions_text + "\n" + "Please notice that your modification need to have practical significance and should not be limited to simple modifications of certain variable values.\n ")
                template += ("Original agent-based model:\n" + original_program + "\n")
                template += ("Modified agent-based model (complete):" + "\n")
                self.prompt = template
                modified_code = self.ask_prompt(0)
                with open(self.answer_file, 'w') as f:
                    f.write(modified_code)
                iter_num += 1
                print("  sub_iter: ", iter_num)
                x = self.verifier_level_1_regen(1)
                with open(self.answer_file, 'r') as f:
                    final_program = f.read()
                if x == 1:
                    original_program = final_program
        if not ite_flag:
            # success
            return [True, final_solutions, final_program]
        return [False, final_solutions, final_program]

    def OE_Solving(self, original_program_file, question_file, whether_pass=1):
        with open(question_file, 'r') as f:
            question = f.read()
        objectives_rep = json.loads(question)
        model_des = objectives_rep["model"]
        problem = objectives_rep["problem"]
        with open(original_program_file, 'r') as f:
            original_program = f.read()
        template_path = self.template_dir + "OE_result_prompt_template.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        gen.prompt = template + "Task:\nThere is a agent-based model that simulates " + model_des + ".  The original model is provided following"
        gen.prompt += ". The problem we want to address is \"" + problem + "\"."
        gen.prompt += "Please utilize your domain knowledge of " + "\"" + model_des + "\" "
        gen.prompt += "to propose some solutions to the problem we want to address. While providing solutions, do not remove existing methods or changing existing parameters in the original model, and these solutions need to have practical significance and should not be limited to simple modifications of certain variable values.\n "
        gen.prompt += ("Original Model:\n" + original_program)
        gen.prompt += ("\n Please try to use natrual language to give solutions" )
        gen.prompt += ("\nSolutions:\n")
        answer = self.ask_prompt(0, False)
        solutions_text = answer
        print(solutions_text)
        template_path = self.template_dir + "solution_2_template.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        gen.prompt = template + "\"" + question + "\".\n"
        gen.prompt += ("Solutions:\n"+solutions_text + "\n")
        gen.prompt += ("\n" + "Note: Please provide a complete modified agent-based model, do not delete any existing classes, functions or parameters of the original model, and all new functions and logics in the modified model should have specific program, do not use comment to replace any logics. \n")
        gen.prompt += ("Original agent-based model:\n" + original_program + "\n")
        gen.prompt += ("Modified agent-based model (complete):" + "\n")
        modified_code = self.ask_prompt(0)
        print(modified_code)
        with open(self.answer_file, 'w') as f:
            f.write(modified_code)
        x = self.verifier_level_1_regen(whether_pass)
        with open(self.answer_file, 'r') as f:
            final_program = f.read()
        return x, solutions_text, final_program








if __name__ == "__main__":
    gpt = Chatgpt()
    template_dir="template/"
    tol_regen=4 #max iterations for "modeling stage"
    solving_iter_max=3 #max iterations for "sovling stage"
    gen = ABM_generate(template_dir, gpt,tol_regen,solving_iter_max)
    #generate ABM: the generate answer is stored in the answer.py
    gen_flag=gen.model_generation("your abm description in one sentence","Your conceptual_representation in json format",0)
    #generate solutions: the generate answer is return
    gen_flag, final_solutions, final_program=gen.CD_Solving("your original program file","your objective_representation file",1)




