## 前言：

最近负责的任务是批量页面检测的工作，工作内容是负责检测信息泄露相关的内容，甲方一下就是给几万个ip进行检测，里面很多可能就是404这样的，一个一个访问的话这很浪费时间，抽空编写了这个webcode脚本。  

## 介绍：  

第一步安装需要的库  

> pip install -r requirements.txt

我们首先需要将检测的ip端口放到ipport.xlsx里面，放到工具的同一路径下面  

![1693067683_64ea29a3ba95dcbfd5b18.png!small?1693067685529](https://image.3001.net/images/20230827/1693067683_64ea29a3ba95dcbfd5b18.png!small?1693067685529)

ipport.xlsx格式如下，第一列是协议，第二列ip加端口  

![1693067934_64ea2a9e945e9eb953500.png!small?1693067935710](https://image.3001.net/images/20230827/1693067934_64ea2a9e945e9eb953500.png!small?1693067935710)

这里有两个参数-th，扫描线程设置，这里默认50线程，-ti请求页面等待时间设置，这里我们使用request模块去请求，这里默认是5s，超过了这个时间就是访问不通的404，最后会将页面的title保留下来  

![1693068341_64ea2c35a27804f4c0dd1.png!small?1693068343238](https://image.3001.net/images/20230827/1693068341_64ea2c35a27804f4c0dd1.png!small?1693068343238)

如果工作中有用到的小伙伴可以尝试下载使用下，还是很方便的，使用到多线程速度还是很快的  

github：https://github.com/nineforfox/webcode

个人csdn地址：https://blog.csdn.net/qq_58000413?spm=1011.2415.3001.5343

  

