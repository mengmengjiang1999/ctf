![TIM截图20200502165754.png](https://image.3001.net/images/20200502/1588413001_5ead42491bdf8.png!small)**ROADtools是一款针对Azure
AD的漏洞利用框架，它可以直接跟Azure
AD进行交互，并尝试探测和利用其中可能存在的安全漏洞。ROADtools当前主要由roadlib库和ROADrecon Azure
AD漏洞利用工具组成。**

## ROADlib

ROADlib这个库可以用来完成Azure
AD的验证任务，或与包含了ROADrecon数据的数据库工具进行整合或构建新的工具。ROADlib中的数据库模型将会根据Azure
AD内部API中定义的元数据进行自动生成。ROADlib存在于ROADtools的命名空间中，因此我们可以使用下列命令将其导入至我们自己的脚本中：

    
    
    from roadtools.roadlib import X

## ROADrecon

ROADrecon这款工具可以帮助研究人员从红队或蓝队视角来探测Azure AD中的信息。简而言之，该工具的功能如下：

1、使用自动生成的元数据模型在磁盘上创建SQLAlchemy后台数据库。

2、在Python中使用异步HTTP调用将Azure AD图中的所有可用信息转储到此数据库。

3、提供插件以查询此数据库并将其输出为其他实用的格式。

4、提供一个内置的Angular扩展接口，可以直接查询脱机数据库以进行分析。

ROADrecon使用了Python的async功能，并只兼容Python v3.6-3.8版本。

## 工具安装

### 使用Pypi发布版本安装

广大研究人员可以使用下列命令安装ROADrecon的稳定版本，下列命令将会自动把roadrecon命令添加至执行路径之中：

    
    
    pip install roadrecon

### 使用GitHub安装

广大研究人员可以从Azure
Pipeline直接下载roadlib和roadrecon的压缩文件，并在解压之后在正确的目录下进行安装。请记住，首先需要安装roadlib：

    
    
    pip install roadlib/  
    
    
    pip install roadrecon/

你还可以使用下列命令在开发模式下安装该工具：

    
    
    pip install -e roadlib/

## 前端开发

如果你想要修改Angular前端，你还需要安装node和npm。接下来，使用Git安装其他的依赖组件：

    
    
    git clone https://github.com/dirkjanm/roadtools.git
    
    pip install -e roadlib/
    
    pip install -e roadrecon/
    
    cd roadrecon/frontend/
    
    npm install

你可以使用npm start命令或在roadrecon/frontend/目录中通过Angular命令行工具和ng
serve命令来运行Angular前端。如需将JavaScript文件构建至ROADrecon的dist_gui目录之中，可以运行下列命令：

    
    
    npm build

## 项目地址

ROADtools：【[ _GitHub传送门_](https://github.com/dirkjanm/ROADtools)】

 ***参考来源：[
_dirkjanm_](https://github.com/dirkjanm/ROADtools)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

