## 0x01.前言

写这篇文章的起因是，在学习java代码审计入门篇的过程中，其中有一部分关于IDEA对jar包的远程调试，其中作者动态调试用的是冰蝎jar包，但是在复现过程中，我发现调试中打的断点一直没有成功，刚开始以为是冰蝎包的版本太高，所以后面选择最低版本的冰蝎包来调试，发现还是不成功，而且在实际调试的入口类和书里面的类还是有一定差别。  
java代码审计入门篇书中的入口类：

![image](https://image.3001.net/images/20211221/1640057319_61c149e79207b51831420.png!small)

github 冰蝎包 反汇编的入口类：  
![image](https://image.3001.net/images/20211221/1640057485_61c14a8dcac945b22fa59.png!small)

所以我选择自己写一个简单的jar包并用IDEA动态调试。

## 0X02.IDEA 导出可执行的jar包

在IDEA的菜单中选择File–>Project Structure,如下图所示：  
![image](https://image.3001.net/images/20211221/1640056575_61c146ff19497a9972e5a.png!small)

选择“Artifacts“在出现的图中点击加号  
![image](https://image.3001.net/images/20211221/1640056641_61c14741b7a20ee1bb423.png!small)

> 1） 需要选择jar包默认运行的入口类  
> 2）
> 需要设置MANIFEST.MF的位置，在选择好入口类后系统会将MANIFEST.MF默认放在src/main/java下，需要将其放在/src/main/resources下

然后到这里还没有结束，继续点击Build–>Build Artifacts

![image](https://image.3001.net/images/20211221/1640057608_61c14b0831cad4a910a56.png!small)  
![image](https://image.3001.net/images/20211221/1640057632_61c14b209e8ba449aa572.png!small)

上述步骤后，你会在相应工程的目录下看到一个名称为out的文件夹。其中可以找到对应的jar文件  
![image](https://image.3001.net/images/20211221/1640057653_61c14b354d7b5b7184e0d.png!small)

## 0x03.动态调试导出的jar包

用IDEA 创建一个新的java项目，然后创建一个lib文件夹将jar包放入，右键选择lib文件夹的“Add as
Library…”，将lib文件夹添加进项目依赖。成功添加后可以看到Jar包中反编译后的源代码。  
![image](https://image.3001.net/images/20211221/1640057781_61c14bb531a906e499a5f.png!small)

调试选项的配置  
![image](https://image.3001.net/images/20211221/1640057698_61c14b62094481fe4bf60.png!small)

通过右上角的“Add Configurations”，选择remote JVM debug，并单击“+”来添加。

默认配置界面，单击“Apply”提交并保存即可。其中“-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005”将作为运行时的启动参数。

> suspend表示是否暂停程序等待调试器的连接，“y”表示暂停，“n”表示不暂停。建议选择暂停，避免程序执行过快导致一些断点无法拦截程序。

启动命令：

    
    
    java -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005 -jar demo3.jar
    Listening for transport dt_socket at address: 5005
    

![image](https://image.3001.net/images/20211221/1640057871_61c14c0fbd808cab38fbe.png!small)

单击IntelliJ IDEA右上角的Debug按钮，即可发现程序在断点处暂停，然后就可以进行逐步的调试.

![image](https://image.3001.net/images/20211221/1640057888_61c14c20933d3e2f0adb2.png!small)

源码链接：https://pan.baidu.com/s/1DiXTv2DuEhbGO9xZtbQJUQ  
提取码：3c8l

## 0x04.总结

通过最近java代码审计的学习，发现平时复现工作做的还是不够好，代码水平还是不行，导致学的不够深，浅尝辄止，希望在新的一年自己可以沉下心来好好提高自己的代码审计水平，欢迎大家关注我的公众号。

![image](https://image.3001.net/images/20211221/1640058417_61c14e3186fa68a2fc122.jpg!small)

