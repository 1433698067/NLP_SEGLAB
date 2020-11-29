
# !/usr/bin/env Python
# coding=utf-8
from codes import Part_3_1
import time
import sys
from codes.pathset import *
'''
    3.2 正反向最大匹配分词实现
    输入文件：199801_sent.txt（1998 年 1 月《人民日报》语料，未分词）
    dic.txt(自己形成的分词词典)
    输出：seg_FMM.txt 和 seg_BMM.txt
 '''



#  正向最大匹配
class FMM(object):
    def __init__(self, dic_path, seg_file_path):
        self.dictionary = set()
        self.maximum = 0
        self.fmm_seg = open(SEG_FMM, 'w', encoding='utf8')
        self.seg_file = open(seg_file_path, 'r', encoding='utf8')
        with open(dic_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                self.dictionary.add(line)
                if len(line) > self.maximum:
                    self.maximum = len(line)

    def cut(self):
        lines = self.seg_file.readlines()
        with open(SEG_FMM, 'w', encoding='utf8') as self.fmm_seg:
            for line in lines:
                seg_line, line = '', line[:len(line)-1]
                while len(line) > 0:
                    try_word = line[0:len(line) if len(line) < self.maximum else self.maximum]
                    while try_word not in self.dictionary:
                        if len(try_word) == 1:  # 字串长度为1，跳出循环
                            break
                        try_word = try_word[0:len(try_word) - 1]  # 继续减小词长
                    line = line[len(try_word):]  # 更新剩余的待分词行
                    seg_line += try_word + '/ '  # 得到一个分词结果
                self.fmm_seg.write(pre_line(seg_line) + '\n')  # 写入换行符
            print('FMM cut over!')


#  反向最大匹配算法
class BMM(object):
    def __init__(self, dic_path, seg_file_path):
        self.dictionary = set()
        self.maximum = 0
        self.bmm_seg = open(SEG_BMM, 'w', encoding='utf8')
        self.seg_file = open(seg_file_path, 'r', encoding='utf8')
        # 读取词典
        with open(dic_path, 'r', encoding='utf8') as f:
            for line in f:
                # 移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
                line = line.strip()
                if not line:
                    continue
                self.dictionary.add(line)
                if len(line) > self.maximum:
                    self.maximum = len(line)

    def cut(self):
        lines = self.seg_file.readlines()
        with open(SEG_BMM, 'w', encoding='utf8') as self.bmm_seg:
            for line in lines:
                seg_line, line = [], line[:len(line) - 1]
                while len(line) > 0:
                    word = line if len(line) < self.maximum else line[len(line)-self.maximum:]
                    while word not in self.dictionary:
                        if len(word) == 1:  # 字串长度为1，跳出循环
                            break
                        word = word[1:]  # 继续减小词长
                    seg_line.insert(0, word + '/ ')  # 得到一个分词结果
                    line = line[:len(line)-len(word)]  # 更新剩余的待分词行
                self.bmm_seg.write(pre_line(''.join(seg_line)) + '\n')  # 写入换行符
        print("BMM cut over!")


def pre_line(line):
    punctuation = '-./'
    buffer, result = '', ''
    word_list = line.split('/ ')
    word_list = word_list[:len(word_list) - 1]
    for idx, word in enumerate(word_list):
        if word.isascii() or word in punctuation:  # 若是字母、数字或者英文标点
            buffer += word
            if idx + 1 == len(word_list):
                result += buffer + '/ '
        else:
            if buffer:
                result += buffer + '/ '
                buffer = ''
            result += word + '/ '
    return result


def main():
    start_time = time.time()
    FMM(GEN_DIC, SEG_FILE).cut()
    end_time = time.time()
    cost_time = end_time - start_time
    print(cost_time)

    start_time2 = time.time()
    BMM(GEN_DIC, SEG_FILE).cut()
    end_time2 = time.time()
    cost_time2 = end_time2 - start_time2
    print(cost_time2)



if __name__ == '__main__':
    sys.exit(main())
