# CS上线Linux--坑太多了

> 传统的Cs只能上线windows，而有时为了方便想将Linux主机上线到Cs，这个时候就需要使用CrossC2插件。

## 1.1 前期准备

    
    
    #下载指定版本
    https://github.com/gloxec/CrossC2/releases/tag/v2.2.4
    

我这里在Windows上展示，所以下的Windows

![image-20220527162027710](https://image.3001.net/images/20220528/1653708713_629197a9114035c109189.png!small)

然后下载cna

 **下载地址：** https://github.com/gloxec/CrossC2/tree/v2.2.4/src

我将其解压到了CS的目录下，并将cna放到了CrossC2文件夹中

![image-20220527162226940](https://image.3001.net/images/20220528/1653708713_629197a9523e42bb38f17.png!small)

编辑cna文件，$CC2_PATH为CrossC2绝对路径，$CC2_BIN根据系统选择

![image-20220527162434224](https://image.3001.net/images/20220528/1653708713_629197a980ce93431e0c0.png!small)

从服务端CS拷贝`.cobaltstrike.beacon_keys`文件到CrossC2文件夹内

![image-20220527163122232](https://image.3001.net/images/20220528/1653708713_629197a9c631376d73def.png!small)

## ​1.2 安装

打开`脚本管理器`加载cna文件

![image-20220527164426062](https://image.3001.net/images/20220528/1653708714_629197aa1c7091a46ca5b.png!small)

## 1.3 反弹shell

这里坑就来了，首先要知道CrossC2需要依赖https监听端口，我这里新建了一个beacon

![image-20220527164607573](https://image.3001.net/images/20220528/1653708714_629197aa67dd72f777664.png!small)

然后点击创建一个CrossC2监听器

![image-20220527164642941](https://image.3001.net/images/20220528/1653708714_629197aaab5441ff319af.png!small)

这里按照如下选择即可，点击生成即可

![image-20220527181037778](https://image.3001.net/images/20220528/1653708714_629197aae7f108d9bae05.png!small)

在监听器选项卡即可看到新生成的CrossC2监听器，点击生成后正常会生成t_cc2.out，就算不生成也无妨，因为生成的不好用，我们不用它。

![image-20220527205120397](https://image.3001.net/images/20220528/1653708715_629197ab3ec0bf480acf5.png!small)

这时候我们转到CrossC2目录，然后打开个cmd，用`genCrossC2.Win.exe`生成文件

    
    
    genCrossC2.Win.exe IP地址 端口 keys文件路径 null Linux x64 文件名
    

端口要注意

![image-20220527211843930](https://image.3001.net/images/20220528/1653708715_629197ab94abe311070f3.png!small)

然后会在CrossC2文件目录生成，将其传到Linux给权限，并运行，CS上线

![image-20220527205044295](https://image.3001.net/images/20220528/1653708716_629197ac5c36282b0d65b.png!small)

