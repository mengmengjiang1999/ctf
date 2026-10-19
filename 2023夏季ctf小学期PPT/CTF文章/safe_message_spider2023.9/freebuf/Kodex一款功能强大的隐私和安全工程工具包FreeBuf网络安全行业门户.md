![](https://image.3001.net/images/20211114/1636901538_619122a253de962da76c2.png!small)

## 关于Kodex

Kodex是一款功能强大的隐私和安全工程工具包，该工具可以帮助广大研究人员对敏感数据和用户个人数据进行识别、扫描、理解、假名化、匿名化和加密处理，以实现敏感数据和个人数据的安全共享和保护。

## 功能介绍

Kodex是一个针对隐私和安全工程的开源工具包，可以用于自动化数据工程工作流中的数据安全和数据保护措施。该工具提供了以下几种功能：

  * 从各种源（如文件、数据库或消息队列）读取数据项。
  * 使用各种增强隐私和安全性的转换来保护这些数据项，如取消标识、屏蔽、假名化、匿名或加密。
  * 将受保护的项目发送到各种目的地址。

在Kodex的帮助下，我们可以使用简单的声明性配置语言描述数据保护和数据安全工作流程。就好比DevOps这样的工具，它可以允许我们使用代码的形式来描述基础设施，Kodex也是一样，同样允许我们以代码的形式描述隐私和安全策略。

Kodex可以帮助广大研究人员处理安全隐私中令人厌烦和困难的方面，比如说：

  * 密钥管理：Kodex可以帮助管理加密和匿名密钥；
  * 参数管理：Kodex可以跟踪每个数据项的处理方式，以便我们能够证明数据工作流的合规性并创建审计跟踪；
  * 数据转换：Kodex采用了现代加密和统计技术来保护我们的数据安全；

## 工具安装&下载

广大研究人员可以使用下列命令下载并安装Kodex：

    
    
    git clone https://github.com/kiprotect/kodex
    
    cd kiprotect
    
    make
    
    make install

## 数据转换

Kodex可以从蓝图中读取目标配置，我们可以通过Kodex来安装这些[
_蓝图_](https://github.com/kiprotect/blueprints)：

    
    
    kodex blueprints download

或者，我们也可以手动将其拷贝至本地设备【[
_参考资料_](https://heykodex.com/docs/blueprints)】。然后，运行假名化示例：

    
    
    kodex run pseudonymization/examples/data-types/pseudonymize
    
    kodex run pseudonymization/examples/data-types/depseudonymize

接下来，Kodex将负责生成并存储假名化所需的加密参数。如果你想要手动输入密钥而不需要生成密钥参数的话，可以直接运行下列命令：

    
    
    kodex run pseudonymization/examples/data-types/pseudonymize-with-key
    
    kodex run pseudonymization/examples/data-types/depseudonymize-with-key

## 运行测试

Kodex提供了很多自动化单元测试，我们可以使用Make来执行：

    
    
    make test

### 测试插件

如果用于编译主代码和插件的编译标志不同，插件测试可能会出现很多错误提示信息，比如说执行竞争条件检测测试。要解决此问题，请切换到plugin文件夹并运行下列命令：

    
    
    make clean
    
    make

### 运行基准测试

Kodex还提供了许多基准测试，我们可以按如下方式运行：

    
    
    make bench

## 许可证协议

本项目的开发与发布遵循[
_AGPL-3.0开源许可证协议_](https://github.com/kiprotect/kodex/blob/master/LICENSE)。

## 项目地址

 **Kodex：** 【[ _GitHub传送门_](https://github.com/kiprotect/kodex)】

## 参考资料

  * [ _https://heykodex.com/docs_](https://heykodex.com/docs)
  * [ _https://github.com/kiprotect/blueprints_](https://github.com/kiprotect/blueprints)

