![11111111.png](https://image.3001.net/images/20190723/1563816372_5d35f1b495efe.png!small)

## SneakyEXE

 **SneakyEXE是一款能够帮助我们在自定义Win32 Payload中嵌入UAC绕过功能的强大工具，该工具目前支持x86_64架构。**

### 工具特性

1、该工具目前已在Windows 7、8、10（64位）上成功测试。

2、免费，开源，并提供了完整源代码。

3、工具演示视频：<https://www.youtube.com/watch?v=12efahUc-nU>

4、参考文档：【[README](https://github.com/Zenix-Blurryface/SneakyEXE/blob/master/README.md)】

### 工具要求

**** |  **Linux** |  **Windows**  
---|---|---  
架构 |  Optional |  x86_64  
Python 3.x > |  支持 |  不支持  
模块 |  termcolor |  不支持  
发行版本 |  任意 |  Windows  
版本 |  任意 |  Windows 7,8,10  
  
## 工具使用

### Linux

这款工具的正常运行需要一个名叫termcolor的Python模块，当你在运行脚本时，它会自动安装这个模块，不过考虑到性能方面的问题，我建议大家手动安装这个模块：

    
    
    $pip3 install termcolor #installing termcolor
    
    $#Temporary usage only, installation below
    
    $ git clone <https://github.com/Zenix-Blurryface/SneakyEXE.git>
    
    $ cd SneakyEXE/Linux
    
    $chmod +x sneakyexe.py
    
    $./sneakyexe <option>=<path to payload/code> out=<where you wannasave>

### Windows

1、 访问该项目的[GitHub主页](https://github.com/Zenix-Blurryface/SneakyEXE)；

2、 下载代码库，点击“克隆或下载”->“下载ZIP“；

3、 选择目标文件夹并解压文件；

4、 切换到目录\SneakyEXE\Win32\下；

5、 执行sneakyexe.exe（或sys\sneakyexe.exe）

请注意，只有在使用带有管理员权限的账户时，Payload才可以执行成功。

## 工具安装

### Linux：

    
    
    $ git clone <https://github.com/Zenix-Blurryface/SneakyEXE.git>
    
    $ cd SneakyEXE
    
    $chmod +x install.sh
    
    $sudo ./install.sh

### Windows：

即将上线…

## 项目构建

> 1、 基于Opensuse Leap 15.0
>
> 2、 使用Python 3.6.5开发
>
> 3、 使用gcc MinGW.orgGCC-8.2.0-3) 8.2.0编译Payload

### Payload嵌入

如果你想从源码构建Payload，你需要用到gcc v8.2.0(C11)以及一台安装了64位Windows10（7/8）的AMD64设备。构建命令如下：

    
    
    #Windows 10/7/8 (AMD64)
    
    #Open cmd.exe / powershell.exe
    
    >>gcc -mwindows -o <output>.exe /source/main.c

### GUI版本

如果你想从源码构建GUI版本，你需要安装Python
3.5.6或更高版本，以及Pyinstaller和Pillow模块，再加上一台安装了64位Windows 7的AMD64设备。构建命令如下：

    
    
    #Assume we already had  Pythonpreinstalled
    
    #Open cmd.exe / powershell.exe
    
    >>pip install pillow      # InstallingPillow
    
    >>pip install pyinstaller # Installing Pyinstaller
    
    >>mkdir compile           # Optionaldirectory name
    
    >>cd compile
    
    >>pyinstaller --windowed --onefile --icon=Icon.ico /source/Win32/GUI.py # Forsysematic version ( /sys ), remove --onefile
    
    >>cd dist
    
    >>GUI.exe                 # The compiledexecutable :}

## 项目地址

SneakyEXE：【[GitHub传送门](https://github.com/Zenix-Blurryface/SneakyEXE)】

* 参考来源：[Zenix-Blurryface](https://github.com/Zenix-Blurryface/SneakyEXE)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM

