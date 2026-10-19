## GDB使用-小技巧

参考：[《100个gdb小技巧》](https://wizardforcel.gitbooks.io/100-gdb-tips/content/index.html)

链接中的文档有许多关于GDB的使用小技巧；

> $info functions - 列出函数的名称
>
> $s/step - 步入，进入带有调试信息的函数
>
> $n/next - 下一个要执行的程序代码
>
> $call/print - 直接调用函数执行
>
> $i/info - 打印函数堆栈帧信息
>
> $frame [addr] - 选择函数堆栈帧
>
> $i frame - 获取选择的函数堆栈帧的地址
>
> $b []- 设置断点
>
> $p - 打印静态变量的值
>
> $x/s\- 打印ASCII字符串
>
> $x/ws\- 打印ASCII字符串，宽字节长度为4个字节
>
> $x/hs\- 打印ASCII字符串，2个字节长度

gdb中使用“x”命令来打印内存的值，格式为“x/nfu addr”。含义为以f格式打印从addr开始的n个长度单元为u的内存值。参数具体含义如下：

a）n：输出单元的个数。

b）f：是输出格式。比如x是以16进制形式输出，o是以8进制形式输出,等等。

c）u：标明一个单元的长度。b是一个byte，h是两个byte（halfword），w是四个byte（word），g是八个byte（giant word）。

## GDB使用-插件

### GDB-.gdbinit

gdbinit配置的公共仓库：<https://github.com/gdbinit/Gdbinit>

这个是别人配置的好gdbinit文件库，非常的大，自己用的话还是重新构建一个，这样自己也可以熟悉整个配置，以及了解自己所需要的配置的内容；

在使用插件之前，先看看本地的gdbinit配置文件，如果没有，则新建一个；

> vim ~/.gdbinit

![1668162018_636e21e226aee3def4ab2.png!small](https://image.3001.net/images/20221111/1668162018_636e21e226aee3def4ab2.png!small)

> #保存历史命令
>
> set history filename ~/.gdb_history
>
> set history save on
>
>  
>
>
> #退出时不显示提示信息
>
> set confirm off
>
>  
>
>
> #按照派生类型打印对象
>
> set print object on
>
>  
>
>
> #打印数组的索引下标
>
> set print array-indexes on
>
>  
>
>
> #每行打印一个结构体成员
>
> set print pretty on

## GDB-peda

<https://github.com/longld/peda>

安装：git clone <https://github.com/longld/peda.git>~/peda  
echo "source ~/peda/peda.py" >> ~/.gdbinit

![1668162068_636e2214083a72b24dd1f.png!small?1668162067924](https://image.3001.net/images/20221111/1668162068_636e2214083a72b24dd1f.png!small?1668162067924)

### 特性介绍

增强gdb的显示：调试时着色显示反汇编代码、寄存器、内存信息。

添加命令以支持调试和漏洞利用开发（有关命令的完整列表，请使用peda help）：

  * aslr -- 显示/设置 GDB 的 ASLR 设置
  * checksec -- 检查二进制的各种安全选项
  * dumpargs -- 在调用指令处停止时显示传递给函数的参数
  * dumprop -- 转储特定内存范围内的所有 ROP 小工具
  * elfheader -- 从调试的 ELF 文件中获取头信息
  * elfsymbol -- 从 ELF 文件中获取非调试符号信息
  * lookup -- 搜索属于内存范围的所有地址/对地址的引用
  * patch -- 补丁内存从字符串/十六进制字符串/整数的地址开始
  * pattern -- 生成、搜索或将循环模式写入内存
  * procinfo -- 显示来自 /proc/pid/ 的各种信息
  * pshow -- 显示各种 PEDA 选项和其他设置
  * pset -- 设置各种 PEDA 选项和其他设置
  * readelf -- 从 ELF 文件中获取头信息
  * ropgadget -- 获取二进制或库的常用 ROP gadgets
  * ropsearch -- 在内存中搜索 ROP 小工具
  * searchmem|find-- 在内存中搜索模式；支持正则搜索
  * shellcode -- 生成或下载常用的shellcode。
  * skeleton -- 生成python漏洞利用代码模板
  * vmmap -- 获取调试过程中段的虚拟映射地址范围
  * xormem -- XOR 内存区域与密钥

## GDB-pwndbg

<https://github.com/pwndbg/pwndbg>

安装：

> git clone <https://github.com/pwndbg/pwndbg>
>
> cd pwndbg
>
> ./setup.sh

![1668162099_636e2233b576e72b0de75.png!small](https://image.3001.net/images/20221111/1668162099_636e2233b576e72b0de75.png!small)

使用说明：<https://github.com/pwndbg/pwndbg/blob/dev/FEATURES.md>

## GDB-gef

<https://github.com/hugsy/gef>

安装：

> wget -q -O-> [https://github.com/hugsy/gef/raw/master/gef.sh](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fhugsy%2Fgef%2Fraw%2Fmaster%2Fgef.sh)|
> sh
>
> wget -q -O ~/[.gdbinit-> gef.py](https://links.jianshu.com/go?to=http%3A%2F%2F.gdbinit-> gef.py)[https://github.com/hugsy/gef/raw/master/gef.py](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fhugsy%2Fgef%2Fraw%2Fmaster%2Fgef.py)
>
> echo source ~/.gdbinit-gef.py >> ~/.gdbinit

![1668162128_636e2250f123322f9d941.png!small?1668162128657](https://image.3001.net/images/20221111/1668162128_636e2250f123322f9d941.png!small?1668162128657)

使用说明：<https://gef.readthedocs.io/en/master/>

安装完以上三个插件，我们再执行gdb，会发现只会到gef，到不了其他两个插件，想用的时候只能到.gdbinit里边注释掉其他两个，这样比较麻烦，简单写一个脚本来选择要使用的插件；

> #!/bin/bash
>
> function Mode_change {
>
> name=$1
>
> gdbinitfile=~/.gdbinit #这个路径按照你的实际情况修改
>
> # gdbinitfile=/root/Desktop/mode
>
>  
>
>
> peda="source ~/peda/peda.py" #这个路径按照你的实际情况修改
>
> gef="source /home/kali/.gdbinit-gef.py" #这个路径按照你的实际情况修改
>
> pwndbg="source /home/kali/pwndbg/gdbinit.py" #这个路径按照你的实际情况修改
>
>  
>
>
> sign=$(cat $gdbinitfile | grep -n "#this place is controled by user's
> shell")
>
> #此处上面的查找内容要和你自己的保持一致
>
>  
>
>
> pattern=":#this place is controled by user's shell"
>
> number=${sign%$pattern}
>
> location=$[number+2]
>
>  
>
>
> parameter_add=${location}i
>
> parameter_del=${location}d
>
>  
>
>
> message="TEST"
>
>  
>
>
> if [ $name -eq "1" ];then
>
> sed -i "$parameter_del" $gdbinitfile
>
> sed -i "$parameter_add $peda" $gdbinitfile
>
> echo -e "Please enjoy the peda!\n"
>
> elif [ $name -eq "2" ];then
>
> sed -i "$parameter_del" $gdbinitfile
>
> sed -i "$parameter_add $gef" $gdbinitfile
>
> echo -e "Please enjoy the gef!\n"
>
> else
>
> sed -i "$parameter_del" $gdbinitfile
>
> sed -i "$parameter_add $pwndbg" $gdbinitfile
>
> echo -e "Please enjoy the pwndbg!\n"
>
> fi
>
>  
>
>
> }
>
>  
>
>
> echo -e "Please choose one mode of GDB?\n1.peda 2.gef 3.pwndbg"
>
>  
>
>
> read -p "Input your choice:" num
>
>  
>
>
> if [ $num -eq "1" ];then
>
> Mode_change $num
>
> elif [ $num -eq "2" ];then
>
> Mode_change $num
>
> elif [ $num -eq "3" ];then
>
> Mode_change $num
>
> else
>
> echo -e "Error!\nPleasse input right number!"
>
> fi
>
>  
>
>
> gdb $1 $2 $3 $4 $5 $6 $7 $8 $9

脚本执行效果如下：

![1668162171_636e227bc5373c04b43d9.png!small?1668162171080](https://image.3001.net/images/20221111/1668162171_636e227bc5373c04b43d9.png!small?1668162171080)

![1668162181_636e22859e930b0e25fa6.png!small?1668162181173](https://image.3001.net/images/20221111/1668162181_636e22859e930b0e25fa6.png!small?1668162181173)

![1668162192_636e22905a6ed98ac0fb1.png!small?1668162191707](https://image.3001.net/images/20221111/1668162192_636e22905a6ed98ac0fb1.png!small?1668162191707)

## 其他

经过上面的安装部署，我们执行gdb来进行调试已经没有问题了；但是当我们需要用到gdbserver的时候会发现kali是没有带gdbserver的；比如当我们用pwntools来执行gdb的时候，会提示gdbserver
is not installed

![1668162227_636e22b38eb4a4672381b.png!small](https://image.3001.net/images/20221111/1668162227_636e22b38eb4a4672381b.png!small)

第一次连接，python会提示没有gdbserver的环境，kali环境下sudo apt-get install
gdbserver，装一个就完事了；当然如果是嵌入式设备的话，需要对应的环境编译一个

环境准备好后，就可以开始用pwntools来执行本地的调试了。

【参考】：<https://blog.csdn.net/aptx4869_li/article/details/81566541>

【参考】：<https://wizardforcel.gitbooks.io/100-gdb-tips/content/index.html>

