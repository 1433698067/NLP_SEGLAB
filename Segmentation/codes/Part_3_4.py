#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
from codes import Part_3_2
from codes.pathset import *
'''
3.4 基于机械匹配的分词系统的速度优化
任选前向/后向最大匹配算法进行优化
这里选择了前向最大匹配算法进行优化
输入文件：199801_sent.txt（1998 年 1 月《人民日报》语料，未分词）
输出：TimeCost.txt（分词所用时间）
'''


class Node:
    def __init__(self, is_word=False, char='', init_list_size=60):
        self.char = char
        self.is_word = is_word
        self.now_words = 0  # 表示填充的字数
        self.child_list = [None] * init_list_size

    def add_child(self, child):
        if self.now_words / float(len(self.child_list)) > float(2 / 3):
            self.now_words = 0
            self.rehash(child)
        index = self.hash_char(char=child.char)
        while self.child_list[index] is not None:
            index = (index + 1) % len(self.child_list)
        self.child_list[index] = child
        self.now_words += 1

    def get_node_by_char(self, char):
        index = self.hash_char(char)
        while True:
            child = self.child_list[index]
            if child is None:
                return None
            if child.char == char:
                return child
            index = (index + 1) % len(self.child_list)

    def hash_char(self, char):
        return ord(char) % len(self.child_list)

    def rehash(self, child):
        old_child_list = self.child_list
        self.child_list = [None] * (2 * len(self.child_list))
        for every_child in old_child_list:
            if every_child is not None:
                index = self.hash_char(char=every_child.char)
                while self.child_list[index] is not None:
                    index = (index + 1) % len(self.child_list)
                self.child_list[index] = every_child
                self.now_words += 1
        self.add_child(child)


class DicAction:
    Words_List = []

    @staticmethod
    def get_fmm_dic(dic_path=GEN_DIC, choice=True):
        if choice:  # 为真表示需要再初始化词列表
            for line in open(dic_path, 'r', encoding='UTF-8'):
                DicAction.Words_List.append(line.split()[0])
        root = Node(init_list_size=7000)
        for word in DicAction.Words_List:
            DicAction.insert_fmm(word, root)
        return root


    @staticmethod
    def insert_fmm(word, root):
        length = len(word)
        count = 1
        node = root.get_node_by_char(word[0])
        before_node = root
        while node is not None:
            if count == length:
                node.is_word = True
                return
            before_node = node
            node = node.get_node_by_char(word[count])
            count += 1
        count -= 1
        while count < length:
            node = Node()
            node.char = word[count]
            count += 1
            before_node.add_child(node)
            before_node = node
        node.is_word = True


class StrMatch:
    @staticmethod
    def fmm(root, txt_path=SEG_FILE, fmm_path=SEG_FMMB):
        seg_result = ''
        file = open(txt_path, 'r', encoding='utf-8')
        of = open(fmm_path, 'w', encoding='UTF-8')
        for line in file:
            seg_line, line = '', line[:len(line) - 1]  # 去掉读取的换行符
            while len(line) > 0:
                count = 0
                terminal_word = line[0]
                node = root.get_node_by_char(line[0])
                while node is not None:
                    count += 1
                    if node.is_word:
                        terminal_word = line[:count]
                    if count == len(line):
                        break
                    node = node.get_node_by_char(line[count])
                line = line[len(terminal_word):]
                seg_line += terminal_word + '/ '
            seg_result += Part_3_2.pre_line(seg_line) + '\n'
        of.write(seg_result)
        of.close()





def main():
    start_time = time.time()
    Part_3_2.FMM(GEN_DIC, SEG_FILE).cut()
    end_time = time.time()
    cost_time = end_time - start_time
    print(cost_time)

    start_time2 = time.time()
    Part_3_2.BMM(GEN_DIC, SEG_FILE).cut()
    end_time2 = time.time()
    cost_time2 = end_time2 - start_time2
    print(cost_time2)

    fmm_root = DicAction.get_fmm_dic(choice=True, dic_path=GEN_DIC)
    start_time3 = time.time()
    StrMatch.fmm(fmm_root)  # 前向最大匹配
    end_time3 = time.time()
    cost_time3 = end_time3 - start_time3
    print(cost_time3)

    time_cost = open('../io_files/result/TimeCost.txt', 'w', encoding='utf-8')
    time_cost.write("优化前\n")
    time_cost.write('FMM时间花销为：' + str(cost_time) + '\n')
    time_cost.write('BMM时间花销为：' + str(cost_time2) + '\n')
    time_cost.write("优化后\n")
    time_cost.write("时间花销为：" + str(cost_time3) + '\n')
    time_cost.write("FMM优化比例为：" + str((1-cost_time3/cost_time)*100) + "%")
    time_cost.close()
    print("请打开TimeCost.txt查看.\n")


if __name__ == "__main__":
    sys.exit(main())
