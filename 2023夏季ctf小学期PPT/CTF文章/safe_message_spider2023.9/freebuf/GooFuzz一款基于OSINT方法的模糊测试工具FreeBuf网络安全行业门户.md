## 关于GooFuzz

GooFuzz是一款基于OSINT方法的模糊测试工具，该工具基于Google
Dork实现其功能。本质上来说，GooFuzz是一个Bash脚本，该脚本使用了Google
Search技术来获取文件或目录中的敏感信息，而无需向目标Web服务器发送请求。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/m3n0sd0n4ld/GooFuzz.git

接下来，在命令行终端中切换到项目根目录下，然后给脚本提供可执行权限：

    
    
    $ cd GooFuzz
    
    $ chmod +x GooFuzz

下列命令即可查看该工具的帮助信息：

    
    
    $ ./GooFuzz -h

## 工具使用

 **工具菜单：**

**![](https://image.3001.net/images/20220705/1657033677_62c453cd9e2b7ab08d4cb.png!small)**

 **通过后缀枚举文件（逗号分隔）：**

**![](https://image.3001.net/images/20220705/1657033684_62c453d43b1b92e78fb34.png!small)**

 **通过后缀枚举txt文件中包含的文件：**

**![](https://image.3001.net/images/20220705/1657033692_62c453dc238361b2757a3.png!small)**

 **按扩展名（子域或域）枚举文件，并显示第一个Google搜索结果：**

**![](https://image.3001.net/images/20220705/1657033698_62c453e24cbee70eafdf4.png!small)**

 **通过字典枚举文件、目录甚至参数（建议只使用非常小的文件）：**

**![](https://image.3001.net/images/20220705/1657033705_62c453e9f3274e852087c.png!small)**

**![](https://image.3001.net/images/20220705/1657033713_62c453f1803120d4b1b48.png!small)**

 **通过指定路径、文字或文件名枚举目录和文件：**

![](https://image.3001.net/images/20220705/1657033721_62c453f932ab897d86104.png!small)

## 工具使用演示

### 在搜索中排除子域（用逗号或列表分隔）：演示一

在下面的例子中，我们从搜索中移除了“mars.nasa.gov”这个子域名：

![](https://image.3001.net/images/20220705/1657033740_62c4540c68e4ee18e019e.png!small)

### 在搜索中排除子域（用逗号或列表分隔）：演示二

在下面的例子中，我们使用了三个扩展名来搜索一个普通文件，并定位到了目标子域名：

![](https://image.3001.net/images/20220705/1657033747_62c4541383b48cb94b1e7.png!small)

我们创建了一个名为“exclusion_list.txt”的文件，并插入了三个需要引入的子域名，然后我们执行了相同的搜索操作：

![](https://image.3001.net/images/20220705/1657033769_62c454290b728a50e7f7a.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/m3n0sd0n4ld/GooFuzz/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **GooFuzz** ：【[ _GitHub传送门_](https://github.com/m3n0sd0n4ld/GooFuzz)】

