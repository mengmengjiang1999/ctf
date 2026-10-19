**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210329/1616996572_606168dc78f04d2dbcb74.jpg!small)

## 关于Limelighter

Limelighter是一款能够帮助我们创建伪造代码签名证书和代码签名的强大工具，除此之外，它还可以帮助我们创建DLL文件以实现EDR产品绕过等等。Limelighter还可以使用有效的代码签名证书来对文件进行签名。当然了，Limelighter也可以使用类似acme.com这样的完全具备资格的有效域名。

## 贡献代码&工具安装

Limelighter基于Golang开发，请确保已在你的操作系统上安装好了下列组件包：

    
    
    openssl
    
    osslsigncode

第一步就是将该项目代码克隆至本地，但是在编译Limelighter之前，我们必须要安装好相关的依赖组件，安装仅需运行下列命令：

    
    
    go get github.com/fatih/color

接下来，克隆项目代码库，并运行项目构建命令：

    
    
    git clone https://github.com/Tylous/Limelighter.git
    
    go build LimeLighter.go

## 工具使用

    
    
    ./LimeLighter -h       
    
     
    
            .____    .__               .____    .__       .__     __                
    
            |    |   |__| _____   ____ |    |   |__| ____ |  |___/  |_  ___________
    
            |    |   |  |/     \_/ __ \|    |   |  |/ ___\|  |  \   __\/ __ \_  __ \
    
            |    |___|  |  Y Y  \  ___/|    |___|  / /_/  >   Y  \  | \  ___/|  | \/
    
            |_______ \__|__|_|  /\___  >_______ \__\___  /|___|  /__|  \___  >__|   
    
                    \/        \/     \/        \/ /_____/      \/          \/         
    
                                                            @Tyl0us
    
     
    
     
    
    [*] A Tool for Code Signing... Real and fake
    
    Usage of ./LimeLighter:
    
      -Domain string
    
            需要创建伪造代码签名的域名
    
      -I string
    
            待签名的文件名
    
      -O string
    
            签名文件名
    
      -Password string
    
            真实证书的密码
    
      -Real string
    
            有效.pfx证书文件的路径
    
      -Verify string
    
            验证一个文件的代码签名证书
    
      -debug
    
            打印调试信息

## 工具使用

如需对一个文件进行签名，我们需要使用“Domain”命令选项来生成一个伪造的代码签名证书：

![](https://image.3001.net/images/20210329/1616996644_60616924b177394127f6c.png!small)

如需使用一个有效的代码签名证书来对一个文件进行签名，可以使用“Real”和“Password”命令选项来实现。

使用“verify”命令验证一个已签名的文件：

![](https://image.3001.net/images/20210329/1616996666_6061693a699c1634bce55.png!small)

签名验证结果如下图所示：

![](https://image.3001.net/images/20210329/1616996688_606169504b4587a92862b.png!small)

## 项目地址

Limelighter：https://github.com/Tylous/Limelighter

