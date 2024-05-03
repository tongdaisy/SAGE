# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# -*- coding:utf-8 -*-
import argparse
import bleu
import weighted_ngram_match
import syntax_match
import dataflow_match
import re
import os



def cal_code_bleu(predictions, answers, para):
    lang = 'python'
    alpha, beta, gamma, theta = para

    # preprocess inputs
    with open(predictions, 'r', encoding='utf-8') as f:
        hypothesis = [f.read()]
    with open(answers, 'r', encoding='utf-8') as f:
        references = [f.read()]

    # assert len(references) == len(pre_references) * len(hypothesis)

    # calculate ngram match (BLEU)
    tokenized_hyps = [x.split() for x in hypothesis]
    tokenized_refs = [[x.split() for x in references]]

    ngram_match_score = bleu.corpus_bleu(tokenized_refs, tokenized_hyps)

    # calculate weighted ngram match
    keywords = [x.strip() for x in open('keywords/' + lang + '.txt', 'r', encoding='utf-8').readlines()]

    def make_weights(reference_tokens, key_word_list):
        return {token: 1 if token in key_word_list else 0.2 \
                for token in reference_tokens}

    tokenized_refs_with_weights = [[[reference_tokens, make_weights(reference_tokens, keywords)] \
                                    for reference_tokens in reference] for reference in tokenized_refs]

    weighted_ngram_match_score = weighted_ngram_match.corpus_bleu(tokenized_refs_with_weights, tokenized_hyps)

    # calculate syntax match
    syntax_match_score = syntax_match.corpus_syntax_match([references], hypothesis, lang)
    # syntax_match_score = 0
    # calculate dataflow match
    dataflow_match_score = dataflow_match.corpus_dataflow_match([references], hypothesis, lang)
    # dataflow_match_score = 0

    code_bleu_score = alpha * ngram_match_score \
                      + beta * weighted_ngram_match_score \
                      + gamma * syntax_match_score \
                      + theta * dataflow_match_score

    return [ngram_match_score, weighted_ngram_match_score, syntax_match_score, dataflow_match_score, code_bleu_score]





def remove_comments(code):
    # remove singleline comments
    code = re.sub(r'(?<!\\)(#.*?$)', '', code, flags=re.MULTILINE)
    # remove multiline comments
    code = re.sub(r'(?<!\\)(""".*?""")', '', code, flags=re.DOTALL)
    code = re.sub(r'(?<!\\)(\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)
    code = re.sub(r'\n\s*\n', '\n', code)
    code = code.strip()
    return code




def all_score(folder_path_1, folder_path_2, para):
    files_info = []
    # folder_path_1: pred, folder_path_2: gts
    all_scores = []
    for file_name in os.listdir(folder_path_1):
        pred = os.path.join(folder_path_1, file_name)
        gt = os.path.join(folder_path_2, file_name)
        if os.path.isfile(os.path.join(folder_path_1, file_name)):
            with open(os.path.join(folder_path_1, file_name), 'r', encoding='utf-8') as f:
                code = f.read()
            code = remove_comments(code)
            with open(os.path.join(folder_path_1, file_name), 'w', encoding='utf-8') as f:
                f.write(code)
        if os.path.isfile(os.path.join(folder_path_2, file_name)):
            with open(os.path.join(folder_path_2, file_name), 'r', encoding='utf-8') as f:
                code = f.read()
            code = remove_comments(code)
            with open(os.path.join(folder_path_2, file_name), 'w', encoding='utf-8') as f:
                f.write(code)
        score = cal_code_bleu(pred, gt, para)
        all_scores.append([file_name, score])
    print(all_scores)
    return all_scores


def single_score(file_1, file_2, para):
    files_info = []
    # folder_path_1: pred, folder_path_2: gts
    if os.path.isfile(file_1):
        with open(file_1, 'r', encoding='utf-8') as f:
            code = f.read()
        code = remove_comments(code)
        with open(file_1, 'w', encoding='utf-8') as f:
            f.write(code)
    if os.path.isfile(file_2):
        with open(file_2, 'r', encoding='utf-8') as f:
            code = f.read()
        code = remove_comments(code)
        with open(file_2, 'w', encoding='utf-8') as f:
            f.write(code)
    score = cal_code_bleu(file_1, file_2, para)[-1]
    return score


if __name__ == "__main__":
    dir_path = ""
    preds_path = dir_path + "preds"
    gts_path = dir_path + "ground_truth"
    para = [0.01, 0.01, 0.9, 0.08]

    scores = []
    for pred in os.listdir(preds_path):
        index = (pred.split(".")[0]).split("_")[1]
        gt = str(index) + ".py" #sage
        gtp = os.path.join(gts_path, gt)
        predp = os.path.join(preds_path, pred)
        score = single_score(predp, gtp, para)
        print(index, score)
        scores.append(score)
    avg_score = sum(scores) / len(scores)
    print(avg_score)
