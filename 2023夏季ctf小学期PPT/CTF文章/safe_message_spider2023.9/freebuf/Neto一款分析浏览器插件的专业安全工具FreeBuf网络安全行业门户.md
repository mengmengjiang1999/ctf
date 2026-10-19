![a.png](https://image.3001.net/images/20180814/1534220208_5b7257b0cbc65.png!small)

## 工具介绍

 **Neto项目采用Python
3开发，可用于寻找和分析热门浏览器（例如Firefox和Chrome）插件及扩展的隐藏特性。它可以自动化实现对数据包文件的解压操作，并从扩展和插件的相关资源中提取出功能代码，例如manifest.json、JavaScript和HTML源文件。**

## 功能介绍

Neto可以给研究人员提供如下功能：

1.Manifest分析；

2.内部文件哈希；

3.利用正则表达式提取实体数据：IPv4、电子邮件、加密货币地址和URL等等；

4.从HTML、CSS和JS文件中提取注释；

5.基于已知矿池域名和表达式的加密货币劫持检测引擎；

6.检测可疑JavaScript代码，例如eval()；

7.对之前已下载的扩展进行Batch分析。

## 工具安装

用户可以使用pip3命令安装数据包：

    
    
    pip3 install -e . –user

除此之外，用户也可以利用sudo命令和管理员权限来完成工具的安装：

    
    
    sudo pip3 install -e .

安装完成之后，可以使用下列命令验证安装结果：

    
    
    python3 -c "import neto; print(neto.__version__)"

## 工具使用

大家可以使用下列命令对一个扩展进行分析：

    
    
    neto analysis -u https://yoururl.com/extension-name.xpi

接下来，Neto将会自动下载该扩展，并默认将其解压到系统的临时目录中。当然了，你也可以直接对本地存储的扩展进行分析：

    
    
    neto analysis -e ./my-extension-name.xpi

静态分析执行完毕之后，工具还会生成一个JSON文件，并将其存储在一个名叫output的文件夹中。

如果你会使用python，你还可以将自己的Python模块数据包以“库”的形式导入进去：

    
    
    >>>from neto.lib.extensions import Extension
    
    >>>my_extension = Extension ("./sample.xpi")
    
    >>>my_extension.filename
    
    'adblock_for_firefox-3.8.0-an+fx.xpi'
    
    >>>my_extension.digest
    
    '849ec142a8203da194a73e773bda287fe0e830e4ea59b501002ee05121b85a2b'

除了利用property来来访问扩展元素之外，还可以通过字典结构来对扩展进行分析：

    
    
    >>>my_extension.__dict__
    
    {'_analyser_version':'0.0.1', '_digest':'849ec142a8203da194a73e773bda287fe0e830e4ea59b501002ee05121b85a2b'…

当然了，你也可以不使用Python，下面给出的是JSON RPC使用样例：

![b.png](https://image.3001.net/images/20180814/1534220304_5b7258107b9e4.png!small)

接下来，你就可以使用JSON RPC库来编写客户端了（本项目的bin目录中提供了一个简单的demo）：

    
    
    curl--data-binary '{"id":0, "method":"remote","params":["https://example.com/myextension.xpi"],"jsonrpc": "2.0"}' -H 'content-type:text/json;' http://localhost:14041

***参考来源：[neto](https://github.com/elevenpaths/neto)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

