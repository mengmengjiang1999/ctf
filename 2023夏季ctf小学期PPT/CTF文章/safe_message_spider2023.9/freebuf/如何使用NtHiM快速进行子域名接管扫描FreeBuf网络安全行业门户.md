![](https://image.3001.net/images/20210411/1618121315_607292631da5192ba631d.png!small)

## 关于NtHiM

NtHiM是一款快速的子域名接管扫描与检测工具，在它的帮助下，广大研究人员可以轻松实现子域名接管漏洞的检测与扫描任务。

## NtHiM安装

### 方法一：使用预编译代码

为了方便广大用户的安装和使用，我们在本项目GitHub的【https://github.com/TheBinitGhimire/NtHiM/releases】页面提供了针对不同操作系统平台的预编译代码，大家可以选择适用于各子系统的版本下载，解压文件之后就可以直接使用NtHiM了。

### 方法二：使用Crates.io

NtHiM还可以通过https://crates.io/crates/NtHiM获取。因此，如果你已经在你的系统上安装好了Rust环境的话，你就可以直接使用下列命令来安装NtHiM了：

    
    
    cargo install NtHiM

### 方法三：手动构建

当然了，你还可以选择手动构建NtHiM，不过你还需要先安装好Cargo。如果你已经安装好了Cargo，你可以直接按照下列方法进行项目手动构建：

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/TheBinitGhimire/NtHiM

在命令行窗口中切换到项目根目录：

    
    
    cd NtHiM

然后，使用下列命令进行代码构建：

    
    
    cargo build

接下来，切换到新创建的target目录中，然后打开其中的debug目录：

    
    
    cd target/debug

此时，你将会看到NtHiM.exe（针对Windows系统）或NtHiM源码（针对Linux系统）了。

如需了解NtHiM的整个安装过程，大家可以点击观看安装指导视频，指导视频中会演示以上三种工具安装的操作步骤。

 **视频地址：** https://youtu.be/CUTbqFhRjwY

## 工具使用

 ** **参数****

|

 ** **描述****

|

 ** **演示样例****  
  
---|---|---  
  
-h

|

显示工具帮助信息

|

NtHiM -h  
  
-t

|

扫描一个目标

|

NtHiM -t https://example.example.com  
  
-f

|

扫描文件列表中的多个目标

|

NtHiM -f hostnames.txt  
  
-c

|

设置并发线程数量

|

NtHiM -c 100 -f hostnames.txt  
  
-V

|

显示工具版本信息

|

NtHiM -V  
  
## 工具使用

### 使用样例1：扫描单个目标

    
    
    NtHiM -t https://example.example.com

### 使用样例2：扫描多个目标

    
    
    NtHiM -f hostnames.txt

## 工具使用演示

![](https://image.3001.net/images/20210411/1618121399_607292b712e0110a05038.gif!small)

## 工具运行

 **扫描单个目标：**

![](https://image.3001.net/images/20210411/1618121383_607292a79bb97315598e5.png!small)

 **使用并发线程扫描多个目标：**

![](https://image.3001.net/images/20210411/1618121389_607292ad09171eca59103.png!small)

## 项目地址

NtHiM：https://github.com/TheBinitGhimire/NtHiM

## 参考资料

https://github.com/TheBinitGhimire/NtHiM/releases

https://crates.io/crates/NtHiM

https://youtu.be/CUTbqFhRjwY

https://github.com/EdOverflow/can-i-take-over-xyz

https://github.com/TheBinitGhimire/NtHiM/issues?q=is%3Aissue+label%3AFAQ

