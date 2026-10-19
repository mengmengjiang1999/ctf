作者：黑蛋

# 一、漏洞简介

本次漏洞还是一个office溢出漏洞，漏洞编号cve-2017-11882。该漏洞是office一个组件EQNEDT32.EXE引起的栈溢出，通杀office版本2007-2016。

# 二、复现环境

系统版本

|

目标程序

|

调试工具

|

辅助工具  
  
---|---|---|---  
  
win7 sp1 x86

|

office2007

|

olldbg

|

Process-Monitor  
  
# 三、漏洞复现

在这里呢，我是使用了Ridter师傅的exp进行分析的，网址：https://github.com/Ridter/CVE-2017-11882/  
之后我们安装office2007，然后双击EXP，弹出计算器：

![](https://image.3001.net/images/20221220/1671550812_63a1d75c52183a8ebc589.png!small)

  
证明漏洞存在。

# 四、漏洞分析

首先我们需要找到溢出点，既然他弹出一个计算器，那么我们可以对CreateProcess函数或者WinExec下断点，尝试找到关键地方，用windbg附加office
2007，然后在CreateProcess函数和WinExec函数下断点：

![](https://image.3001.net/images/20221220/1671550814_63a1d75e55a3bcf7c98c7.png!small)

  
然后g起来，用word打开exp：

![](https://image.3001.net/images/20221220/1671550816_63a1d76000e3333deb240.png!small)

结果发现并没有断下来，思考许久，猜测计算器不是word弹出来的，我们打开PCHunter查看进程：

![](https://image.3001.net/images/20221220/1671550817_63a1d761dd153d5ec21b4.png!small)

  
可以看到计算器的父进程是cmd，但是cmd的父进程存在PID，但是在列表中却找不到PID为1404的进程，卡顿许久，猜测或许是cmd父进程隐藏了自己或者启动时间太短，启动完自己结束。想起了一个老软件Process-Monitor，使用Process-Monitor查看进程：

![](https://image.3001.net/images/20221220/1671550819_63a1d7636e4e6567c6511.png!small)

  
同样没有，这里我们需要开启Process-Monitor，然后再次用word打开exp：

![](https://image.3001.net/images/20221220/1671550821_63a1d76547f236a6b5a6e.png!small)

现在可以很清晰看到cmd父进程是EQNEDT32.exe，以及他的路径。所以我们需要在EQNEDT32.exe中下断点，而不是word里面下断点。在这里我们需要设置一下-注册表，因为EQNEDT32.exe这个程序是被word带起来的，而他又会很快的结束，所以需要设置此程序启动就被附加：

HKEY_LOCAL_MACHINE\SOFTWARE\MICROSOFT\WINDOWS NT\CURRENTVERSION\IMAGE FILE
EXECUTION OPTIONS

![](https://image.3001.net/images/20221220/1671550822_63a1d766cd8de9f4c683b.png!small)

  
这样，我们就完成了EQNEDT32.exe这个程序启动附加。接下来我们双击exp，olldbg成功附加EQNEDT32.exe，首先在对WinExce下断点，Ctrl+g(WinExec)，然后在首部下断点：

![](https://image.3001.net/images/20221220/1671550824_63a1d768668eebdfc53ab.png!small)

  
go起来，成功停在断点处，说明计算器就是通过WinExce启动的，F8单步走过函数初始化过程，开辟栈空间等步骤，然后我们观察堆栈EBP+4的位置，就是函数返回地址：

![](https://image.3001.net/images/20221220/1671550825_63a1d7698e8602234cf12.png!small)

  
跟进返回地址，可以看到这里调用了WinExec函数：

![](https://image.3001.net/images/20221220/1671550826_63a1d76a39c50698e3f72.png!small)

  
我们在call WinExec函数前面一句，以及call这条语句下断点：

![](https://image.3001.net/images/20221220/1671550826_63a1d76aecf89272f5b28.png!small)

  
然后关闭word，重新双击exp，然后在OD中运行起来：

![](https://image.3001.net/images/20221220/1671550827_63a1d76bbac74f65288a6.png!small)

  
可以看到他停在了call这条语句，并没有执行push
eax，在这里我们可以判断出应该是上个函数返回值直接跳到了WinExec上，我们查找堆栈，向高地址查找，可以看到上个函数返回地址：

![](https://image.3001.net/images/20221220/1671550828_63a1d76c730f296d12128.png!small)

在堆栈+40的位置回车跟到上一层函数：

![](https://image.3001.net/images/20221220/1671550829_63a1d76d2c00f4d6b0b43.png!small)

  
在此地点上方call函数下断点，然后重新运行，卡在断点处：

![](https://image.3001.net/images/20221220/1671550830_63a1d76e14cd908a00cf9.png!small)

![](https://image.3001.net/images/20221220/1671550830_63a1d76ee7b229814beaf.png!small)

我们F7跟进去单步调试，看看哪里覆盖了返回地址，我们注意F7进去的第一个call：

![](https://image.3001.net/images/20221220/1671550831_63a1d76f929f0d6d56a89.png!small)

首先给他下个断点，预防他是关键函数，然后再F8：

![](https://image.3001.net/images/20221220/1671550832_63a1d7704e1100c3fc755.png!small)

  
可以看到这里就是关键函数，刚走过这个函数就断在了WinExec函数上，我们重新调试，让断在刚才下的断点上，F7跟进去调试：

![](https://image.3001.net/images/20221220/1671550833_63a1d77125875a20eb466.png!small)

  
首先锁定堆栈返回地址，看看什么时候会被淹没，在这里我们已经找到关键地方，一串cmd字符，以及拷贝代码：

![](https://image.3001.net/images/20221220/1671550834_63a1d77232de0fee5ca87.png!small)

![](https://image.3001.net/images/20221220/1671550835_63a1d7732710ec21b9c54.png!small)

我们执行到返回，可以看到cmd这一串的地址正好是WinExec函数第一个参数：

![](https://image.3001.net/images/20221220/1671550836_63a1d77465adfed51d345.png!small)

  
也就是这里是通过淹没返回地址到WinExec上，然后通过修改字符串控制WinExec的参数，启动cmd打开计算器实现。通过启动cmd，打开了计算器，而之后的的AAAA等都是传给计算器参数，是无效的。我们可以在cmd测试一下：

![](https://image.3001.net/images/20221220/1671550837_63a1d77554609108a7ce9.png!small)

五、exp简单生成

我们修改一下exp：

![](https://image.3001.net/images/20221220/1671550838_63a1d77675e1244635346.png!small)

  
然后用010Editor打exp，找到cmd这串字符，修改为弹出截屏框：

![](https://image.3001.net/images/20221220/1671550839_63a1d7772bce5b3e0b377.png!small)

![](https://image.3001.net/images/20221220/1671550839_63a1d777e6849ca513c91.png!small)

  
接下来我们取消断点测试一下：

![](https://image.3001.net/images/20221220/1671550841_63a1d77968840c55eabef.png!small)

  
弹出了剪切屏，漏洞复现利用成功。

