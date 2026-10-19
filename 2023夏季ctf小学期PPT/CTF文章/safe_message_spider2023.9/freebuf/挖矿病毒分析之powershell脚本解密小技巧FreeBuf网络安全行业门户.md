近几年挖矿病毒比较多，比较早的PowerGhost、驱动人生挖矿、近期还在继续活跃的MyKing，柠檬鸭等病毒关键部分就是powershell脚本，写这个文章也是在吾爱看到有人求助分析一个[柠檬鸭](https://www.52pojie.cn/thread-1519894-1-1.html)的样本，也算是对自己分析解密powershell脚本的总结。

## 一、powershell脚本混淆的主要方法

### 1、随机大小写

powershell的特性不区分大小写，这个只是让看着眼花，就不用说了。

### 2、字符串拼接

    
    
    [Ref].Assembly.GetType('Sys'+'tem.Mana'+'gement.Aut'+'omatio'+'n.Am'+'siUtils').GetField('am'+'siInitFai'+'led','NonP'+'ublic,Static').SetValue($null,$true)

这一行代码字符串用+截断，这个还好点，只是看着不爽，把'+'全部剪切掉就好了。

### 3、转义符(反引号)

PowerShell 能够识别的特殊字符：

    
    
    `0     Null
     `a    警报
     `b    退格
     `f    换页
     `n    换行
     `r    回车
     `t    水平制表
     `v    垂直制表

转义符号加在其他字符前不影响字符的意思，只要不在0,a,b,f,n,r,t,v的小写字母前出现就是无意义的可以直接剪切掉，目前见过的混淆脚本很少遇到有意义的转义字符。

### 4、Ascii编码

使用[char]xx 代替字符 如：[char]48代表0。

### 5、base64编码

这种用的最多一般都是把一些PE编码比如开始提到的柠檬鸭，m.ps1和m2.ps1就是把32位和64位的mimikatz编码到脚本中。![](https://image.3001.net/images/20211113/1636792875_618f7a2b24597343efd2d.jpg!small)

这个提取也比较简单010editor有个解密这个挺方便。

![](https://image.3001.net/images/20211113/1636793169_618f7b513389f993bc777.jpg!small)直接decode就好了。

### 6、逆序

![](https://image.3001.net/images/20211113/1636793437_618f7c5d7e3bf62998da0.png!small)这是柠檬鸭样本if.bin中间解密出来的部分代码很明显这部分应该主要都是char]xx，从网上找了几个逆序的东西都不行（可能是我太挫了没找到）只能自己python抄几行代码还原了主要代码如下。

    
    
    with open(in,'r') as f:
            k = f.read()
        y = list(k)
        y.reverse()
        de = ''.join(y)
    
        with open(out,'w') as fw:
            fw.write(de)

## 二、一个简单方便的解密方法

根据powershell的特性基本都是用 **Invoke-Expression**
来执行执行脚本，根据微软的说明。![](https://image.3001.net/images/20211113/1636794804_618f81b4ced2f91e0a7b5.png!small)

大多数脚本可以在文件头或者结尾发现这个。![](https://image.3001.net/images/20211113/1636794973_618f825d4af392b3dd566.png!small)

把这个Invoke-Expression删掉然后在脚本末尾加上|out-file “输出文件”，或者直接>>输出到文件就可以解密了。

基于powershell的特性Invoke-Expression的变形比较多，常见的有IEX、&( $psHOme[4]+$pshOme[34]+'x')
、$Env:ComSpec[4,26,25]-Join''、$ShellId[1]+$ShellId[13]+'x'
、$EnV:cOmSPeC[4,24,25]-jOIn''等，执行脚本的事要要注意。

## 三、总结

powershell还原其实并不太难，熟悉一下特性有点耐心基本还是都可以解出来的，就是有点费眼，有些没有脚本文件的直接通过命令行执行，提取命令行参数解密也一样，系统日志也有powershell日志，也可以从日志里提，碰到过一次命令行参数太长，日志都记录了十几条才提取完整，总的来说要有耐心。

