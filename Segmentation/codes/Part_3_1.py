# coding=utf-8

import sys
from codes.pathset import *
K = 10  # 表示将标准分词文件的9/10作为训练集
'''
    3.1 词典的构建
    输入文件：199801_seg&pos.txt
    输出：dic.txt（自己形成的分词词典)
'''

'''
Mydic用于1-4部分的实验
'''


class Mydic(object):
    def __init__(self, seg_path, dic_path):
        self.word_set, self.max_len = set(), 0
        with open(seg_path, 'r', encoding='utf8') as self.seg_text:
            lines = self.seg_text.readlines()
        with open(dic_path, 'w', encoding='utf8') as self.dic_text:
            for line in lines:
                for word in line.split():
                    if '/m' in word:
                        continue
                    word = word[1 if word[0] == '[' else 0:word.index('/')]
                    self.word_set.add(word)
                    self.max_len = len(word) if len(word) > self.max_len else self.max_len
            self.word_list = list(self.word_set)
            self.word_list.sort()
            self.dic_text.write('\n'.join(self.word_list))
            print('dic create over!\n')

    def get_max_len(self):
        return self.max_len

    def search(self, search_word):
        if search_word in self.word_list:
            return True
        else:
            return False





def gene_train_txt(std_seg_path=SEG_POS, train_path=TRAIN_FILE,
                   std_path=ANSWER_FILE, k=K):
    with open(std_seg_path, 'r', encoding='utf-8')as std_seg_file:
        std_seg_lines = std_seg_file.readlines()
    std_lines = []  # 用于输出标准分词答案
    with open(train_path, 'w', encoding='utf-8') as train_file:
        for idx, line in enumerate(std_seg_lines):
            if idx % k != 0:
                train_file.write(line)  # 按照行数模K将该行作为训练行
            else:
                std_lines.append(line)
    with open(std_path, 'w', encoding='utf-8') as std_file:
        std_file.write(''.join(std_lines))
    gene_test_txt()  # 相应的更改测试文本


# 将标准文本剩下的文本作为测试文本并生成标准对比文本，不需单独运行，已在训练文本改变的时候后默认修改测试文件
def gene_test_txt(std_test_path=SEG_POS, test_path=TEST_FILE, k=K):
    with open(std_test_path, 'r', encoding='utf-8')as std_seg_file:
        std_seg_lines = std_seg_file.readlines()
    with open(test_path, 'w', encoding='utf-8') as train_file:
        for idx, line in enumerate(std_seg_lines):
            if idx % k == 0:
                train_file.write(line)  # 按照行数模K将该行作为训练行





def main():
    Mydic(SEG_POS, GEN_DIC)     # 生成普通词典
    gene_train_txt()  # 生成测试机和训练集


if __name__ == '__main__':
    sys.exit(main())
