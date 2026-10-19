## Part1 安装阶段

###
1.注意将文件夹下载至C盘之外，亲身经历报错到怀疑人生![1634281661_616928bdf322a258e8823.png!small](https://image.3001.net/images/20211015/1634281661_616928bdf322a258e8823.png!small)

###
2.注意一同下载汇编工具（如下图）![1634282982_61692de63ab5d1752c007.png!small](https://image.3001.net/images/20211015/1634282982_61692de63ab5d1752c007.png!small)

网上很多资源，这里放一个师傅的网盘链接

> 链接：https://pan.baidu.com/s/1UwSpoh9mU0PtJ00BF63zRA  
> 提取码：hiaj

之后新建一个asm文件夹放汇编工具以及之后的文件![1634283465_61692fc9601f76b63199c.png!small](https://image.3001.net/images/20211015/1634283465_61692fc9601f76b63199c.png!small)

![1634283410_61692f925914391793093.png!small](https://image.3001.net/images/20211015/1634283410_61692f925914391793093.png!small)

最后打开可执行文件：![1634283502_61692fee2de909ca9cf3d.png!small](https://image.3001.net/images/20211015/1634283502_61692fee2de909ca9cf3d.png!small)

第一步就完成了~

## Part2 使用阶段

### step1：虚拟一个C盘出来

 **方法1：每次进入dosbox时使用命令**

> mount c d:\dosbox\asm

上图命令中 **d:\dosbox\asm** 依个人盘及dosbox位置而定

![1634283750_616930e68f85b321329b8.png!small](https://image.3001.net/images/20211015/1634283750_616930e68f85b321329b8.png!small)

出现这句话即虚拟成功， **c:**
即可![1634284110_6169324e22159fa8724de.png!small](https://image.3001.net/images/20211015/1634284110_6169324e22159fa8724de.png!small)

**方法2：直接在conf文件中加，避免每次操作繁琐**![1634284111_6169324f695e33ba8d742.png!small](https://image.3001.net/images/20211015/1634284111_6169324f695e33ba8d742.png!small)

打开程序即可找到配置文件位置![1634284110_6169324e708f32e8845f3.png!small](https://image.3001.net/images/20211015/1634284110_6169324e708f32e8845f3.png!small)

添加即可：

![1634285834_6169390aa921e97d302a5.png!small](https://image.3001.net/images/20211015/1634285834_6169390aa921e97d302a5.png!small)

### step2：在asm文件夹下写入第一个汇编程序1.asm

> masm 1.asm

得到1.obj

> link 1.obj

得到 1.exe

> debug 1.exe

完成！！

## Part3 问题解决

### 1.masm，link等命令无效

解决：将汇编工具放置在asm文件夹下

### 2.打不开obj文件

解决：修改文件夹权限为完全访问

 **新手上路欢迎师傅们斧正**

