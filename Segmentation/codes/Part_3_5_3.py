#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from math import log
from codes.Part_3_3 import evaluation
from codes.Part_3_3 import record_evaluation
from codes.Part_3_3 import record_errors
from codes.pathset import *

States = ['B', 'M', 'E', 'S']
Pre_Status = {
    'B': 'ES',
    'M': 'MB',
    'S': 'SE',
    'E': 'BM'
}
MIN = -3.14e+100

'''
    主函数
'''



'''
    未登陆词处理
'''


def process(segment, dictionary, A, B, Pi):
    words = segment.split('/ ')[:-1]
    length = len(words)
    buf = ''
    answer = ''
    for i in range(length):
        if len(words[i]) == 1:
            if words[i] in dictionary:
                if buf:
                    answer += cut(buf, A, B, Pi)
                    buf = ''
                answer += words[i] + '/ '
            else:
                buf += words[i]
                if i == len(words) - 1 and buf:
                    answer += cut(buf, A, B, Pi)
        else:
            if buf:
                answer += cut(buf, A, B, Pi)
                buf = ''
            if i == len(words) - 1 and words[i]:
                answer += cut(words[i], A, B, Pi)
            else:
                answer += words[i] + '/ '
    return answer


'''
    未登陆词切分
'''


def cut(sentence, A, B, Pi):
    probability, pos_list = viterbi(sentence, A, B, Pi)
    begin = 0
    next_i = 0
    tmp = ''
    for i, char in enumerate(sentence):  # 最优路径回溯
        pos = pos_list[i]
        if pos == 'B':  # 字位于开始位置
            begin = i
        elif pos == 'E':  # 字位于结束位置
            tmp += sentence[begin: i + 1] + '/ '
            next_i = i + 1
        elif pos == 'S':  # 单字
            tmp += char + '/ '
            next_i = i + 1
    if next_i < len(sentence):  # 剩余直接作为一个分词返回
        tmp += sentence[next_i:] + '/ '
    return tmp


'''
    vertebi算法
'''


def viterbi(obs, A, B, Pi):
    V = [{}]
    path = {}
    for i in States:  # 初始化
        V[0][i] = Pi[i] + B[i].get(obs[0], MIN)
        path[i] = [i]

    for i in range(1, len(obs)):
        V.append({})
        new_path = {}
        for j in States:  # 当前时刻可能状态
            em = B[j].get(obs[i], MIN)  # 本时刻的状态的发射概率对数
            (probability, state) = max(
                [(V[i - 1][y0] + A[y0].get(j, MIN) + em, y0) for y0 in Pre_Status[j]])  # 上一时刻状态的概率对数以及该状态到本时刻状态的转移概率对数
            V[i][j] = probability
            new_path[j] = path[state] + [j]
        path = new_path
    (probability, state) = max((V[len(obs) - 1][y], y) for y in 'ES')  # 最后时刻
    return (probability, path[state])  # 最大概率对数，最优路径


'''
    生成训练集和测试集
'''


def generate_data(path=SEG_POS, test_path=SEG_FILE,
                  train_file=TRAIN_FILE,
                  test_file=TEST_FILE, answer_file=ANSWER_FILE, k=10):
    answer_lines = []
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(train_file, 'w', encoding='utf-8') as file:
        for i, line in enumerate(lines):
            if i % k != 0:
                file.write(line)
            else:
                answer_lines.append(line)
    with open(answer_file, 'w', encoding='utf-8') as file:
        file.writelines(answer_lines)

    lines = []
    with open(test_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(test_file, 'w', encoding='utf-8') as file:
        for i, line in enumerate(lines):
            if i % k == 0:
                file.write(line)
    file.close()


class HMM(object):
    def __init__(self):
        self.Pi = {}  # 状态集
        self.A = {}  # 状态转移概率
        self.B = {}  # 发射概率
        self.state_cnt = {}  # 状态出现次数
        self.dictionary = set()
        self.total = 0

        for i in States:
            self.Pi[i] = 0.0
            self.A[i] = {}
            self.B[i] = {}
            self.state_cnt[i] = 0
            for j in States:
                self.A[i][j] = 0.0

    def train(self, train_file=TRAIN_FILE):
        with open(train_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            if line == '\n':
                continue
            words = []
            pos = []
            for word in line.split():
                if word[0] == '[':  # 删除词性标注
                    word = word[1:word.index('/')]
                elif '/' in word:
                    word = word[0:word.index('/')]
                words.extend(list(word))
                self.dictionary.add(word)
                self.total += 1

                if len(word) == 1:  # 单字
                    pos.append('S')
                    self.Pi['S'] += 1
                else:
                    pos.append('B')
                    pos.extend(['M'] * (len(word) - 2))
                    pos.append('E')
                    self.Pi['B'] += 1

            for i in range(len(pos)):
                self.state_cnt[pos[i]] += 1
                self.B[pos[i]][words[i]] = self.B[pos[i]].get(words[i], 0) + 1
                if i != 0:
                    self.A[pos[i - 1]][pos[i]] += 1
        for i in States:
            if self.Pi[i] == 0:
                self.Pi[i] = MIN
            else:
                self.Pi[i] = log(self.Pi[i] / self.total)
            for j in States:
                if self.A[i][j] == 0:
                    self.A[i][j] = MIN
                else:
                    self.A[i][j] = log(self.A[i][j] / self.state_cnt[i])
            for j in self.B[i].keys():
                self.B[i][j] = log(self.B[i][j] / self.state_cnt[i])

    def record(self, pi_file='../io_files/hmm/pi.txt', a_file='../io_files/hmm/a.txt', b_file='../io_files/hmm/b.txt'):
        with open(pi_file, 'w', encoding='utf-8') as file:
            for i in States:
                file.write(i + ' ' + str(self.Pi[i]) + '\n')
        with open(a_file, 'w', encoding='utf-8') as file:
            for i in States:
                file.write(i + '\n')
                for j in States:
                    file.write(' ' + j + ' ' + str(self.A[i][j]) + '\n')
        with open(b_file, 'w', encoding='utf-8') as file:
            for i in States:
                file.write(i + '\n')
                for j in self.B[i].keys():
                    file.write(' ' + j + ' ' + str(self.B[i][j]) + '\n')
        file.close()


def main():
    generate_data()
    hmm = HMM()
    hmm.train()
    hmm.record()
    with open(TEST_FILE, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(SEG_HMM, 'w', encoding='utf-8') as file:
        for line in lines:
            tmp = process(line[0:len(line) - 1] + '/ ', hmm.dictionary, hmm.A, hmm.B, hmm.Pi)
            if tmp == '/ ':
                file.write('\n')
            else:
                file.write(tmp + '\n')
    hmm_right_number, hmm_standard_number, hmm_train_number, hmm_error_lines = evaluation('../io_files/hmm/answer.txt',
                                                                                          '../io_files/result/seg_HMM.txt')
    record_evaluation('HMM效果分析: \n', hmm_right_number, hmm_standard_number, hmm_train_number)
    record_errors(ERROR_HMM, hmm_error_lines)
    print("请打开score.txt查看.\n")


if __name__ == "__main__":
    sys.exit(main())
