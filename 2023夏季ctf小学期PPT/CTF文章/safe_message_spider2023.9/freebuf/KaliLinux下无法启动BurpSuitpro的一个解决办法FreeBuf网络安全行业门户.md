BurpSuit是一款非常强大的工具，前段时间在Kali Linux上无法正常打开BurpSuit共（po）享（jie）版。我是萌新一名，大佬勿喷。

![image.png](https://image.3001.net/images/20210601/1622533064_60b5e3c8ad88a39863c13.png!small)点击“RUN”始终没有反应，在查阅了一些资料过后，发现可能是JDK版本的原因。原来，在JDK9以及JDK9之后的版本就不再支持了，所以我们选择使用JDK8尝试能不能打开BurpSuit。

①我们先来查看当前JDK的版本。终端输入命令“java -version”,回车即可查看。  
![image.png](https://image.3001.net/images/20210601/1622533093_60b5e3e50311694f40551.png!small)当前版本的JDK是11.0.9版本的。接下来切换版本试一下。

②终端输入命令“update-alternatives --config java”,查看当前系统中的所有JDK版本。  
![image.png](https://image.3001.net/images/20210601/1622533130_60b5e40a39057a9848299.png!small)可以看到，当前系统中有三个版本供选择（1号是我自己安装的JDK），这里我们选择最后一个，即Java-8。首先需要切换到管理员su
root）才能切换版本，然后键入选择的编号：3。

③验证版本是否切换成功。终端输入命令“java -version”,回车即可查看。  
![image.png](https://image.3001.net/images/20210601/1622533153_60b5e421474f6020f76a1.png!small)由图可以看出，版本已经成功切换。接下来我们试试打开BurpSuit。

![image.png](https://image.3001.net/images/20210601/1622533188_60b5e44402adc569b7916.png!small)大功告成。  
![image.png](https://image.3001.net/images/20210601/1622533222_60b5e46668ef07413df96.png!small)Kali
Linux安装BurpSuit
Pro可以点击[这里](https://blog.csdn.net/haoxuexiaolang/article/details/103933866)，查看大神详细教程。

