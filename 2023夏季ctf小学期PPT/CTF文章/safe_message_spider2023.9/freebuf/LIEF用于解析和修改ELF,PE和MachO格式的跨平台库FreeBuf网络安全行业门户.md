**今天给大家介绍的是一款名叫LIEF的跨平台库，大家可利用LIEF来对ELF、PE和MachO格式的文件进行解析和修改。**

![1.png](https://image.3001.net/images/20180619/15294079358919.png!small)

## 主要功能

1\. 解析：LIEF能够解析ELF、PE和MachO格式，并给用户提供了友好的API来访问文件格式内部数据。

2\. 修改：LIEF能够修改上述格式的部分数据。

3\. 抽象：这些格式拥有一些常见特征，例如数据段、符号和入口点等等，LIEF能够对这些特征进行抽象化处理。

4\. API：LIEF能够结合C、C++和Python使用。

## 下载与安装

运行下列命令安装更新组件：

    
    
    pip install setuptools –upgrade

运行下列命令安装最新版本的LIEF：

    
    
    pip install life

安装最新的commit：

    
    
    pip install https://github.com/lief-project/packages/raw/lief-master-latest/pylief-0.9.0.dev.zip

## 安装或整合LIEF

【[Python指南](https://lief.quarkslab.com/doc/installation.html#python)】

【[VisualStudio指南](https://lief.quarkslab.com/doc/installation.html#visual-studio-integration)】

【[XCode指南](https://lief.quarkslab.com/doc/installation.html#xcode-integration)】

【[CMake指南](https://lief.quarkslab.com/doc/installation.html#cmake-integration)】

## 开始使用

### Python

![2.png](https://image.3001.net/images/20180619/15294079765737.png!small)

### C++

![3.png](https://image.3001.net/images/20180619/15294079871549.png!small)

### C

![4.png](https://image.3001.net/images/20180619/15294079989805.png!small)

## 工具文档

【[使用文档](http://lief.quarkslab.com/doc/index.html)】

【[入门教程](http://lief.quarkslab.com/doc/tutorials/index.html)】

【[API开发文档](http://lief.quarkslab.com/doc/api/index.html)】

【[编程辅助工具](http://lief.quarkslab.com/doxygen/index.html)】

*** 参考来源：[LIEF](https://github.com/lief-project/LIEF)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

