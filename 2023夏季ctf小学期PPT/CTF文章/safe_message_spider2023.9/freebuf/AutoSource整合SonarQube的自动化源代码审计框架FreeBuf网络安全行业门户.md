**今天给大家介绍的这款开源工具名叫AutoSource，它是一款整合了SonarQube的自动化源代码审计框架。**

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597677_5cd70dedb0646.jpg!small)

## AutoSource

AutoSource是一款整合了SonarQube的自动化源代码审计框架，广大研究人员可以利用该工具来进行静态代码分析与审计。除此之外，在AutoSource的帮助下，我们还可以在SDLC（软件开发生命周期）的各个阶段中对目标项目进行高效率的漏洞扫描。代码扫描的过程也非常简单，我们只需要将给定的GIT代码库链接到框架中，AutoSource就可以完成剩下的自动化扫描任务了。

AutoSource框架目前支持在大部分常见计算机平台上执行源代码审计，其中包括macOS、Linux和Windows。

## 工具安装

1、 使用下列命令将AutoSource框架代码库克隆到本地设备：  

    
    
    git clone https://github.com/Securityautomation/autoSource.git

2、 读取prerequisites.txt文件，并安装所有框架依赖组件。

3、
运行downloadSonar.py文件，该文件将下载并安装SonarQube框架，安装完成后可以直接在浏览器地址栏中输入“<http://127.0.0.1:9000>“来访问工具：

    
    
    python3 downloadSonar.py

4、 接下来，运行executeScanner.py文件，该文将会要求你输入需要扫描的GIT代码库地址：

    
    
    python3 executeScanner.py

5、 扫描完成后，可以直接访问下列地址来查看SonarQube界面：

    
    
    http://127.0.0.1:9000

## 工具运行截图

### 下载SonarQube和SonarScanner：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597731_5cd70e237a103.png!small)

### SonarQube运行：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597736_5cd70e284d196.png!small)

### 运行扫描器：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597741_5cd70e2df0d57.png!small)

### 自动化扫描过程：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597748_5cd70e3421598.png!small)

### 扫描成功：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597753_5cd70e399dca9.png!small)

### SonarQube仪表盘：

![AutoSource
：整合SonarQube的自动化源代码审计框架](https://image.3001.net/images/20190512/1557597759_5cd70e3f974b0.png!small)

## 项目地址

AutoSource：【[GitHub传送门](https://github.com/Securityautomation/autoSource)】

 ***
参考来源：[Securityautomation](https://github.com/Securityautomation/autoSource)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

