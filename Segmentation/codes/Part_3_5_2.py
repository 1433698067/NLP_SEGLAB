
# -*- coding: utf-8 -*-

import re
import sys
from math import log
from codes.Part_3_3 import evaluation,record_errors,record_evaluation
from codes.Part_3_5_3 import HMM
from codes.Part_3_5_3 import process
from codes.pathset import *


class Word(object):
    def __init__(self, char, cnt):
        self.char = char
        self.cnt = cnt
        self.latter = {}  # 后一个词及其频率


class Dictionary(object):
    def __init__(self):
        self.words = {}
        self.max_length = 0
        self.total = 0
        self.first = {}  # 句首词及其频率

    '''
        生成二元模型分词词典
    '''

    def generate_bigram_dictionary(self, path=TRAIN_FILE):
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            words = re.findall(r'[^\s[]+(?=/\w+)', line)  # 去除词性标注
            punctuation = [i for i in range(len(words)) if
                           words[i] == '，' or words[i] == '。' or words[i] == '；' or words[i] == '！' or words[i] == '？']
            punctuation.insert(0, -1)
            sentences = [words[i + 1: j] for (i, j) in zip(punctuation[:-1], punctuation[1:])]  # 按标点划分句子
            sentences.append(words[punctuation[len(punctuation) - 1] + 1:])
            for sentence in sentences:
                if sentence:
                    pairs = list(zip(sentence[:-1], sentence[1:]))
                    for p in pairs:
                        if p[0] not in self.words:
                            self.words[p[0]] = Word(p[0], 1)
                        else:
                            self.words[p[0]].cnt += 1
                        self.max_length = max(self.max_length, len(p[0]), len(p[1]))  # 更新词典最大词长

                        if p[1] in self.words[p[0]].latter:  # 记录后一个词及其频率
                            self.words[p[0]].latter[p[1]] += 1
                        else:
                            self.words[p[0]].latter[p[1]] = 1

                    if sentence[0] in self.first:  # 记录句首词及其频率
                        self.first[sentence[0]] += 1
                    else:
                        self.first[sentence[0]] = 1

                    if sentence[-1] not in self.words:
                        self.words[sentence[-1]] = Word(sentence[-1], 1)
                    else:
                        self.words[sentence[-1]].cnt += 1

                    self.total += len(pairs) + 2
        with open(BI_DIC, 'w', encoding='utf-8') as dictionary:
            for word in self.words.keys():
                for latter_word in self.words[word].latter:
                    dictionary.write(word + ' ' + latter_word + ' ' + str(self.words[word].latter[latter_word]) + '\n')

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

    def bigram_caculate(self, sentence, DAG):
        length = len(sentence)
        log_total = log(self.total)  # 词典中词总数的对数
        route = [0] * (length + 1)
        route[length] = (0, 0)  # (频度得分值，词语第一个字的位置)
        for i in range(length):
            max_p = (float('-inf'), 0)
            for x in DAG[i]:
                freq = 1
                word = sentence[x: i + 1]

                if x == 0:  # 句首词
                    if word in self.first:
                        freq = self.first[word]
                else:
                    pre = sentence[route[x - 1][1]: x]  # 前一个词
                    if pre in self.words and word in self.words[pre].latter:
                        freq = self.words[pre].latter[word]
                max_p = max((log(freq) - log_total + route[x - 1][0], x), max_p)
            route[i] = max_p
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

    def bigram_cut(self, original_path, path=SEG_BI):
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
                    route = self.bigram_caculate(sentence, self.get_DAG(sentence))
                    cut = self.sentence_cut(sentence, route)
                    segment += cut + '/ ' + i.group() + '/ '
                    old = i.start() + 1
                if old < len(line) - 1:
                    route = self.bigram_caculate(line[old:], self.get_DAG(line[old:]))
                    cut = self.sentence_cut(line[old:], route)
                    segment += cut + '/ '
                if segment:
                    segment = process(segment, hmm.dictionary, hmm.A, hmm.B, hmm.Pi)
                file.write(segment + '\n')



def main():
    dictionary = Dictionary()
    dictionary.generate_bigram_dictionary()
    dictionary.bigram_cut(TEST_FILE)
    bigram_right_number, bigram_standard_number, bigram_train_number, bigram_error_lines = evaluation('../io_files/hmm/answer.txt',
                                                                                                      '../io_files/result/seg_bigram.txt')
    record_evaluation('二元语言模型效果分析: \n', bigram_right_number, bigram_standard_number, bigram_train_number)
    record_errors(ERROR_BI, bigram_error_lines)

    print("请打开score.txt查看\n")


if __name__ == "__main__":
    sys.exit(main())