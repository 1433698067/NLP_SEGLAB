#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from math import log
from codes.Part_3_3 import evaluation
from codes.Part_3_3 import record_evaluation
from codes.Part_3_3 import record_errors
from codes.Part_3_5_3 import process
from codes.Part_3_5_3 import HMM
from codes.pathset import *
'''
    主函数
'''





class Word(object):
    def __init__(self, char, cnt):
        self.char = char
        self.cnt = cnt


class Dictionary(object):
    def __init__(self):
        self.words = {}
        self.max_length = 0
        self.total = 0

    '''
        生成一元模型分词词典
    '''

    def generate_uni_dictionary(self, path=TRAIN_FILE):
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            words = re.findall(r'[^\s[]+(?=/\w+)', line)  # 去除词性标注
            for word in words:
                if word not in self.words:
                    self.words[word] = Word(word, 1)
                else:
                    self.words[word].cnt += 1
                self.total += 1
                self.max_length = max(self.max_length, len(word))  # 更新词典最大词长
        with open(UNI_DIC, 'w', encoding='utf-8') as dictionary:
            for word in self.words.keys():
                dictionary.write(word + ' ' + str(self.words[word].cnt) + '\n')

            dictionary.close()

    '''
        建立词图
    '''

    def get_DAG(self, sentence):
        length = len(sentence)  # 句子长度
        DAG = {}
        for k in range(length):
            tmp = []  # 记录第k位置上字的路径情况
            i = k
            while i >= 0 and k - i < self.max_length:
                frag = sentence[i: k + 1]
                if frag in self.words:
                    tmp.append(i)
                i -= 1
            if not tmp:  # 分词词典中没有该词
                tmp.append(k)  # 加入单字
            DAG[k] = tmp
        return DAG

    '''
        动态规划查找最大概率路径
    '''

    def unigram_caculate(self, sentence, DAG):
        length = len(sentence)
        log_total = log(self.total)  # 词典中词总数的对数
        route = [0] * (length + 1)
        route[length] = (0, 0)  # (频度得分值，词语第一个字的位置)
        for i in range(length):
            route[i] = max([(log(1 if sentence[x: i + 1] not in self.words else self.words[sentence[x: i + 1]].cnt)
                             - log_total + route[x - 1][0], x) for x in DAG[i]])  # log(词的概率) - log(总词数) + 上一个字的成词概率
        return route

    '''
        切分句子
    '''

    def sentence_cut(self, sentence, route):
        length = len(sentence)
        tmp = []
        start = length - 1
        end = length - 1
        while end >= 0:
            start = route[end][1]
            word = sentence[start: end + 1]
            tmp.insert(0, word)
            end = start - 1
        return '/ '.join(tmp)

    '''
        切分文件
    '''

    def unigram_cut(self, original_path, path=SEG_UNI):
        hmm = HMM()
        hmm.train()
        with open(original_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(path, 'w', encoding='utf-8') as file:
            for line in lines:
                line = line.strip('\n')
                old = 0
                segment = ''
                for i in re.finditer(r'[，。；！？]', line):  # 根据标点符号分割句子
                    sentence = line[old: i.start()]
                    route = self.unigram_caculate(sentence, self.get_DAG(sentence))
                    cut = self.sentence_cut(sentence, route)
                    segment += cut + '/ ' + i.group() + '/ '
                    old = i.start() + 1
                route = self.unigram_caculate(line[old:], self.get_DAG(line[old:]))
                cut = self.sentence_cut(line[old:], route)
                segment += cut
                if segment:
                    segment = process(segment, hmm.dictionary, hmm.A, hmm.B, hmm.Pi)
                file.write(segment + '\n')
        file.close()


def main():
    dictionary = Dictionary()
    dictionary.generate_uni_dictionary()
    dictionary.unigram_cut(TEST_FILE)
    unigram_right_number, unigram_standard_number, unigram_train_number, unigram_error_lines = evaluation(
        ANSWER_FILE, SEG_UNI)
    record_evaluation('一元语言模型效果分析: \n', unigram_right_number, unigram_standard_number, unigram_train_number)
    record_errors(ERROR_UNI, unigram_error_lines)

    print("请打开score.txt查看\n")



if __name__ == "__main__":
    sys.exit(main())