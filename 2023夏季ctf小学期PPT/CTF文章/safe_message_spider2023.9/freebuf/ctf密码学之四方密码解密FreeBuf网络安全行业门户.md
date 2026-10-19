## 前言

前几日刷题遇到一道密码学的四方解密题：

题目如下：四方门主东方青木看着四面八方涌过来的极客，非常震惊，转头便进入了祖祠中的地下室，发现这丫传自唐朝的密室还设计了英文密码。旁边的石头上（附件中有拓本）刻着密码和密文，大家快帮助门主解出密码(答案为一串通顺语义字符串)

key1:security

key2:information

密文啊这是，骚年加油：zhnjinhoopcfcuktlj

## 了解四方密码

首先来了解一下四方密码：

四方密码是一种对称式加密法，由法国人Felix Delastelle（1840年–1902年）发明。

这种方法将字母两个一组，然后采用多字母替换密码。

四方密码用4个5×5的矩阵来加密。每个矩阵都有25个字母（通常会取消Q或将I,J视作同一样，或改进为6×6的矩阵，加入10个数字）。

首先选择两个英文字作密匙，例如example和keyword。对于每一个密匙，将重复出现的字母去除，即example要转成exampl，然后将每个字母顺序放入矩阵，再将余下的字母顺序放入矩阵，便得出加密矩阵。

将这两个加密矩阵放在左上角和右下角，余下的两个角放a到z顺序的矩阵：

![1604217336_5f9e69f82f6880f1d15b5.png!small?1604217337053](https://image.3001.net/images/20201101/1604217336_5f9e69f82f6880f1d15b5.png!small?1604217337053)

### 加密的步骤

  

两个字母一组地分开讯息：（例如hello world变成he ll ow or ld）

找出第一个字母在左上角矩阵的位置

![1604217413_5f9e6a4550e40d84a603b.png!small?1604217413969](https://image.3001.net/images/20201101/1604217413_5f9e6a4550e40d84a603b.png!small?1604217413969)

同样道理，找第二个字母在右下角矩阵的位置：

![1604217445_5f9e6a65ba05b1e74c338.png!small?1604217446322](https://image.3001.net/images/20201101/1604217445_5f9e6a65ba05b1e74c338.png!small?1604217446322)

找右上角矩阵中，和第一个字母同行，第二个字母同列的字母：

![1604217534_5f9e6abe1e38e680f324a.png!small?1604217534788](https://image.3001.net/images/20201101/1604217534_5f9e6abe1e38e680f324a.png!small?1604217534788)

找左下角矩阵中，和第一个字母同列，第二个字母同行的字母：

![1604217561_5f9e6ad9c7971e13b4c86.png!small?1604217562644](https://image.3001.net/images/20201101/1604217561_5f9e6ad9c7971e13b4c86.png!small?1604217562644)

FY这两个字母就是加密过的讯息。

循环后hello world的加密结果：

FY HG HZ HS JE

脚本：

    
    
    import collections
    import re
    
    
    matrix = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
    pla = 'abcdefghijklmnoprstuvwxyz'
    key1 = '[EXAMPLE]'
    key2 = '[KEYWORD]'
    key1 = ''.join(collections.OrderedDict.fromkeys(key1))
    key2 = ''.join(collections.OrderedDict.fromkeys(key2))
    
    
    matrix1 = re.sub('[\[\]]','',key1) + re.sub(key1,'',matrix)
    matrix2 = re.sub('[\[\]]','',key2) + re.sub(key2,'',matrix)
    
    
    matrix_list1 = []
    matrix_list2 = []
    pla_list = []
    for i in range(0,len(matrix1),5):
    matrix_list1.append(list(matrix1[i:i+5]))
    #print matrix_list1
    
    
    for i in range(0,len(matrix2),5):
    matrix_list2.append(list(matrix2[i:i+5]))
    #print matrix_list2
    
    
    for i in range(0,len(pla),5):
    pla_list.append(list(pla[i:i+5]))
    #print pla_list
    
    
    
    
    #查询明文字母位置
    def find_index(x):
    for i in range(len(pla_list)):
    for j in range(len(pla_list[i])):
    if pla_list[i][j] == x:
    return i,j
    
    
    def gen_cip(letter):
    
    
    #两个子母中第一个字母位置
    first = find_index(letter[0])
    
    
    #两个子母中第二个字母位置
    second = find_index(letter[1])
    
    
    cip = ''
    cip += matrix_list1[first[0]][second[1]]
    cip += matrix_list2[second[0]][first[1]]
    
    
    return cip
    
    
    def encrypt(pla):
    #pla = 'whereismysecretkey'
    cip = ''
    for i in range(0,len(pla),2):
    cip += gen_cip(pla[i:i+2])
    return cip
    
    
    def main():
    pla = 'hello world'
    pla = pla.replace(' ','')
    print (encrypt(pla))
    
    
    if __name__ == '__main__':
    main()

结果：![1604217790_5f9e6bbea7624adf0d617.png!small?1604217791105](https://image.3001.net/images/20201101/1604217790_5f9e6bbea7624adf0d617.png!small?1604217791105)

### 解密的步骤

同样是将密文分组，找出分组中第一个字母在右上角矩阵的位置F，第二个字母在左下角矩阵的位置Y，第一个明文为第一个字母的行号和第二个字母的列号h，第二个明文为第一个字母的列号和第二个字母的行号e，依次循环即可

## 解题

再回到本题

由key1:security和 key2:information可以确认阵图

abcde SECUR

fghij ITYAB

klmno DFGHJ

prstu KLMNO

vwxyz PVWXZ

INFOR abcde

MATBC fghij

DEGHJ klmno

KLPSU prstu

VWXYZ vwxyz

要解密的密文为zh nj in ho op cf cu kt lj

按照刚才的方法解密为：yo un ga nd su cc es sf ul

young and successful

脚本：

    
    
    import collections
    import re
     
    matrix = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
    pla = 'abcdefghijklmnoprstuvwxyz'
    key1 = '[SECURITY]'
    key2 = '[INFORMATION]'
    key1 = ''.join(collections.OrderedDict.fromkeys(key1))
    key2 = ''.join(collections.OrderedDict.fromkeys(key2))
     
    matrix1 = re.sub('[\[\]]','',key1) + re.sub(key1,'',matrix)
    matrix2 = re.sub('[\[\]]','',key2) + re.sub(key2,'',matrix)
     
    matrix_list1 = []
    matrix_list2 = []
    pla_list = []
    for i in range(0,len(matrix1),5):
    matrix_list1.append(list(matrix1[i:i+5]))
    #print matrix_list1
     
    for i in range(0,len(matrix2),5):
    matrix_list2.append(list(matrix2[i:i+5]))
    #print matrix_list2
     
    for i in range(0,len(pla),5):
    pla_list.append(list(pla[i:i+5]))
    #print pla_list
     
    #查询两个密文字母位置
    def find_index1(x):
    for i in range(len(matrix_list1)):
    for j in range(len(matrix_list1[i])):
    if matrix_list1[i][j] == x:
    return i,j
    def find_index2(y):
    for k in range(len(matrix_list2)):
    for l in range(len(matrix_list2[k])):
    if matrix_list2[k][l] == y:
    return k,l
     
    def gen_pla(letter):
     
    #两个子母中第一个字母位置
    first = find_index1(letter[0])
     
    #两个子母中第二个字母位置
    second = find_index2(letter[1])
     
    pla = ''
    pla += pla_list[first[0]][second[1]]
    pla += pla_list[second[0]][first[1]]
     
    return pla
     
    def main():
    cip = 'ZHNJINHOOPCFCUKTLJ'
    pla = ''
    for i in range(0,len(cip),2):
    pla += gen_pla(cip[i:i+2])
    print (pla)
     
    if __name__ == '__main__':
    main()

![1604218027_5f9e6cab86ebdd6b7cceb.png!small?1604218027859](https://image.3001.net/images/20201101/1604218027_5f9e6cab86ebdd6b7cceb.png!small?1604218027859)

