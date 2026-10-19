![](https://image.3001.net/images/20200229/1582973607_5e5a42a79d330.jpg!small)

## 工具介绍

 **PolyShell是一款功能强大的polyglot脚本，它可以同时适用于Bash、Windows Bash和PowerShell。**

这种特性使得PolyShell成了一渗透测试中一款非常有用的模板，因为它能够再无需目标特定的Payload的情况下在大多数目标系统中执行。除此之外，PolyShell还可以使用类似[
_USB Rubby Ducky_](https://shop.hak5.org/collections/usb-rubber-ducky/products/usb-rubber-ducky-deluxe)和[
_MalDuino_](https://malduino.com/)这样的设备并通过输入注入来进行传递和发送。

## 工具下载

广大研究人员可以使用下列命令将该项目的源码克隆至本地：

    
    
    git clone https://github.com/llamasoft/polyshell.git

## 如何使用

### 作为单独脚本使用：

> 1、拷贝/重命名脚本，配置正确的文件扩展名，例如.sh、.bat或.ps1；
>
> 2、以Batch文件或PowerShell文件的运行方式来运行脚本；

### 使用命令注入的方式使用脚本：

> 1、在目标设备上打开终端窗口；
>
> 2、运行Payload；
>
> 3、按下Ctrl-C，然后运行“exit”命令；

以输出注入的方式使用该脚本与脚本直接运行的使用方式有一些不同，当以单独脚本的方式运行时，一旦一种语言已经处理完成，那么Payload将会立即退出执行。如果是通过输入注入的方式运行的话，Payload将会以读取循环的方式运行。如果不以循环方式运行的话，Payload将会关闭当前终端窗口，并在一个未知窗口中继续输入执行。组合键Ctrl-C可以让脚本退出读取循环，并确保在运行的过程中不会产生任何意外情况。

除此之外，如果直接将脚本代码粘贴到终端中运行的话，可能会出现运行失败的情况。当脚本到达读取循环之处，某些终端会将剩下的粘贴文本当作读取循环的输入数据来处理，这就非常好了，但有的终端可能会在读取循环退出时继续执行脚本，这就不合适了。

## 脚本工作机制

当我们尝试运行指定代码语言的命令时，该工具会尝试对命令进行解析，分析因素包括参数引用、重定向和注释等等。大家可以参考下列这行代码：

    
    
    echo \" <<'BATCH_SCRIPT' >/dev/null ">NUL "\" \`" <#"

每一种语言都可以识别echo命令，但不同语言会以不同的方式来解析后续的命令。比如说：

    
    
    echo \" <<'BATCH_SCRIPT' >/dev/null ">NUL "\" \`" <#"
    
    Bash [-----] [---]
    
    Batch [-----------------------------] [-] [---]
    
    PS [-----------------------------] [-]

## 工具运行截图

![](https://image.3001.net/images/20200229/1582973655_5e5a42d7be13f.png!small)

![](https://image.3001.net/images/20200229/1582973655_5e5a42d7bedd4.png!small)

![](https://image.3001.net/images/20200229/1582973655_5e5a42d7c7179.png!small)

## 项目地址

> PolyShell：【[ _GitHub传送门_](https://github.com/llamasoft/polyshell)】

 *** 参考来源：[
_llamasoft_](https://github.com/llamasoft/polyshell)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

