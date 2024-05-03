###  “Source Code” Directory 

The source code of SAGE, which contains the 

- sage.py: The main program of SAGE (Here, we choose gpt-3.5-turbo as the example, you can select other LLMs).
- verifier_level2_function.py, answer.py: During SAGE runtime, the intermediate results generated by LLM are stored here.
- deal_with_text.py: Responsible for processing textual content. 
- template: The few-shot contents in Sage used to assist LLM in in-context learning. 
- evaluation: Some metrics evaluating the quality of generated code.

### “ABM Dataset” Directory 

The solution-oriented ABM evaluation dataset 

- scenario-model dataset: 
  -  001.py-050.py : ground truth models 
  - 001.txt-050.txt: conceptual representation-based scenario descriptions 
  - 001_NL.txt-050_NL.txt: natural language-based scenario descriptions 
  - total_description.md: Domain Classification for different samples

- problem-solution dataset:
  - criteria_defined problems: 
    - question_001.txt-question_012.txt: objective representation-based problems
    - original_model_001.py-original_model_012.py: original ABMs for problems
    - verification_level2_001.py-verification_level2_012.py: corresponding criteria function of above questions
    - answer_001.py-answer_012.py: corresponding modified ABMs (ground trutu solutions) for above questions.
  - open-ended problems: 
    - question_001.txt-question_018.txt: objective representation-based problems
    - original_model_001.py-original_model_018.py: original ABMs for problems