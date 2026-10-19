## 简介：

Crunch是一种创建密码字典工具，按照指定的规则生成密码字典，可以灵活的制定自己的字典文件。使用Crunch工具生成的密码可以输出到屏幕，保存到文件、或另一个程序。由其在渗透测试需要爆破的时候，字典的编排等直接影响到我们的爆破速度，对整个渗透测试流程起着十分重要的作用。

可以根据自己需要的字符自己编写密码库文件来完成对特殊字典的编写。

环境：kali2020虚拟机

#### 命令结构

    
    
    crunch minLen maxLen [option]  
      
    解释：crunch 密码的最小长度 密码的最大长度 【可选选项】

#### 参数详解

    
    
    min    设定最小字符串长度（必选）  
    max    设定最大字符串长度（必选）  
      
    oprions  
    -b     指定文件输出的大小，避免字典文件过大    
    -c     指定文件输出的行数，即包含密码的个数  
    -d     限制相同元素出现的次数  
    -e     定义停止字符，即到该字符串就停止生成  
    -f     调用库文件（/etc/share/crunch/charset.lst）  
    -i     改变输出格式，即aaa,aab -> aaa,baa  
    -I     通常与-t联合使用，表明该字符为实义字符  
    -m     通常与-p搭配  
    -o     将密码保存到指定文件  
    -p     指定元素以组合的方式进行  
    -q     读取密码文件，即读取pass.txt  
    -r     定义重某一字符串重新开始  
    -s     指定一个开始的字符，即从自己定义的密码xxxx开始  
    -t     指定密码输出的格式  
    -u     禁止打印百分比（必须为最后一个选项）  
    -z     压缩生成的字典文件，支持gzip,bzip2,lzma,7z  

#### 特殊字符

    
    
    %      代表数字  
    ^      代表特殊符号  
    @      代表小写字母  
    ,      代表大写字符

若字典中需要空格 ，;等用双引号来表示

## 命令类型和实例：

###  **类型1：**

crunch minLen maxLen -o输出到的文件名

说明： 默认由小写字母来组成密码 （不加输出文件名会生成后直接打印在屏幕）

生成 1 - 3 位由小写字母组成的密码并保存的cruntest.txt

生成 1 - 3 位由小写字母组成的密码并保存的cruntest.txt

    
    
    crunch 1 3 >> crunchtext.txt //创建从1位到3位的所有小写字母的密码本

![1621256787_60a26a53f3debd80d1f56.png!small?1621256789196](https://image.3001.net/images/20210517/1621256787_60a26a53f3debd80d1f56.png!small?1621256789196)

    
    
    输入：cat crunchtext.txt  //进行查看

![1621256816_60a26a700a58dde50a253.png!small](https://image.3001.net/images/20210517/1621256816_60a26a700a58dde50a253.png!small)

### 类型2：

crunch minLen maxLen xxxxx -o输出到的文件名

说明： 生成由xxxx组成的minLen–maxLen的密码。

生成3位纯数子的密码并保存的cruntest.txt

    
    
    crunch 3 3 0123456789 -o crunchtext.txt //创建3位全部为数字的密码本

![1621256858_60a26a9a7a759cc449c3d.png!small?1621256859339](https://image.3001.net/images/20210517/1621256858_60a26a9a7a759cc449c3d.png!small?1621256859339)

    
    
    输入：cat crunchtext.txt  //进行查看

![1621256865_60a26aa16051f98551673.png!small?1621256866507](https://image.3001.net/images/20210517/1621256865_60a26aa16051f98551673.png!small?1621256866507)

### 类型3:

crunch minLen maxLen -t xxxx%% -o输出到的文件名

说明 已知‘xxxx’，未知’%%‘，生成minLen-maxLen密码

生成5位的纯数字，前3个数字固定，后两位依次数字的密码并保存的cruntest.txt（默认补的是数字）

    
    
    crunch 5 5 -t 092%% -o crunchtext.txt  //%是随机数字

![1621256875_60a26aaba007be8d905a8.png!small?1621256876483](https://image.3001.net/images/20210517/1621256875_60a26aaba007be8d905a8.png!small?1621256876483)

    
    
    输入：cat crunchtext.txt  //进行查看

![1621256882_60a26ab2deee7012ad7ce.png!small?1621256883915](https://image.3001.net/images/20210517/1621256882_60a26ab2deee7012ad7ce.png!small?1621256883915)

### 类型4:

crunch minLen maxLen -p xxxxx >>输出到的文件名

说明： minLen与maxLen不再起作用，但是这两个参数必须要有 生成xxxxx的全排列

生成4位纯数字，由abcdef随机组成的密码并保存的cruntest.txt（默认补的是数字）

    
    
    crunch 4 4 -p abcdef >> crunchtext.txt //在原有的基础上进行添加(>>)

![1621256891_60a26abb57b3d69b2f71d.png!small?1621256892517](https://image.3001.net/images/20210517/1621256891_60a26abb57b3d69b2f71d.png!small?1621256892517)

    
    
    输入：cat crunchtext.txt  //进行查看

![1621256897_60a26ac199641e8bfa46e.png!small?1621256898609](https://image.3001.net/images/20210517/1621256897_60a26ac199641e8bfa46e.png!small?1621256898609)

### 类型5:

crunch minLen maxLen -f aaa.lst bbb -s ccc >>输出到的文件名

说明： 输入 调用密码库 aaa.lst 中的 bbb 项 并以ccc开头的密码 到目标文件

未完待续......

