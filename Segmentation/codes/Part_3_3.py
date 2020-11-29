#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from codes.pathset import *
'''
    3.3 正反向最大匹配分词效果分析
    输入文件：199801_seg&pos.txt（1998 年 1 月《人民日报》的分词语料库）
    seg_FMM.txt、seg_BMM.txt
    输出：score.txt(包括准确率（precision）、召回率（recall），F 值的结果文件)
'''



'''
    查找分词对应的下标
'''


def find_index(words):
    index = 0
    indexes = []
    for word in words:
        tmp_index = index
        indexes.append(tmp_index)
        index += len(word)
    return indexes


'''
    分词评价函数
'''


def evaluation(standard_path, train_path):
    right_number = 0
    standard_number = 0
    train_number = 0
    with open(standard_path, 'r', encoding='utf-8') as standard_file:
        with open(train_path, 'r', encoding='utf-8') as train_file:
            line1 = standard_file.readline()
            line2 = train_file.readline()
            error_lines = []  # 记录不匹配的行
            while line1 != '' and line2 != '':
                while line1 == '\n':
                    line1 = standard_file.readline()
                while line2 == '\n':
                    line2 = train_file.readline()
                standard_words = re.findall(r'[^\s[]+(?=/\w+)', line1)
                train_words = line2.strip('\n').split('/ ')[:-1]

                standard_indexes = find_index(standard_words)
                train_indexes = find_index(train_words)

                cnt = 0  # 该行正确分词的个数
                checked = 0  # 已检查的索引
                for i in range(len(train_indexes) - 1):  # 记录正确分词个数
                    for j in range(checked, len(standard_indexes) - 1):
                        if train_indexes[i] == standard_indexes[j] and train_indexes[i + 1] == standard_indexes[j + 1]:
                            cnt += 1
                            checked = j + 1
                            break
                if train_indexes[len(train_indexes) - 1] == standard_indexes[len(standard_indexes) - 1]:  # 单独判断最后一个分词
                    cnt += 1
                if len(train_indexes) != len(standard_indexes):  # 记录错误分词
                    error_lines.append(line1 + '\n' + line2 + '\n\n')

                right_number += cnt
                if line1 != '':
                    standard_number += len(standard_indexes)
                if line2 != '':
                    train_number += len(train_indexes)
                line1 = standard_file.readline()
                line2 = train_file.readline()
    return right_number, standard_number, train_number, error_lines


'''
    记录两种匹配方法效果分析
'''


def record_evaluation(title, right_number, standard_number, train_number, k=1):
    precision = right_number / train_number
    recall = right_number / standard_number
    F = (pow(k, 2) + 1) * precision * recall / (pow(k, 2) * precision + recall)
    with open(SCORE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(SCORE_PATH, 'w', encoding='utf-8') as file:
        file.writelines(lines)
        file.write(title)
        file.write('正确分词数: ' + str(right_number) + '\n')
        file.write('标准分词数: ' + str(standard_number) + '\n')
        file.write('模型分词数: ' + str(train_number) + '\n')
        file.write('准确率: ' + str(precision) + '\n')
        file.write('召回率: ' + str(recall) + '\n')
        file.write('F值: ' + str(F) + '\n')
        file.write('\n')
    file.close()


'''
    记录分词错误
'''


def record_errors(title, error_lines):
    with open(title, 'w', encoding='utf-8') as file:
        file.writelines(error_lines)
    file.close()



def main():
    FMM_right_number, FMM_standard_number, FMM_train_number, FMM_error_lines = evaluation(SEG_POS, SEG_FMM)
    record_evaluation('正向最大匹配效果分析: \n', FMM_right_number, FMM_standard_number, FMM_train_number)
    record_errors(ERROR_FMM, FMM_error_lines)

    BMM_right_number, BMM_standard_number, BMM_train_number, BMM_error_lines = evaluation(SEG_POS, SEG_BMM)
    record_evaluation('逆向最大匹配效果分析: \n', BMM_right_number, BMM_standard_number, BMM_train_number)
    record_errors(ERROR_BMM, BMM_error_lines)

    FMMB_right_number, FMMB_standard_number, FMMB_train_number, FMMB_error_lines = evaluation(SEG_POS, SEG_FMMB)
    record_evaluation('优化后的正向最大匹配效果分析: \n', FMMB_right_number, FMMB_standard_number, FMMB_train_number)
    record_errors(ERROR_BMM, BMM_error_lines)

    print("评价完成，请打开score.txt查看\n")


if __name__ == "__main__":
    sys.exit(main())