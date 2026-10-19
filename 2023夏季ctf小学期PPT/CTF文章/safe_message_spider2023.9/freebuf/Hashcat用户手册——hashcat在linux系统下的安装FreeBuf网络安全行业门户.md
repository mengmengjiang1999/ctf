前面我们已经说过hashcat在Window环境下的安装编译，今天我们就来聊一聊hashcat在Linux环境下的安装。总说安装确实有点无聊啊，但是大家忍耐一下把，安装好程序以后，大家就可以来聊一下hashcat中命令的使用方法。

## Ubantu下安装hashcat

这里我们安装hashcat-4.1.0.。hashcat4.0在源代码中整合GPU和CPU的版本。在安装时，hashcat会判断你的硬件，并安装相应的版本。

Hashcat4.0已经取消了gcc的限制，这就省略了很多事情。这样我们在安装hashcat时，只需要安装opencl库作为运行hashcat的支撑库。这样，就省却了很多配置环境的过程。

### 安装opencl

Opencl有很多版本,intel，nvida,AMD的opencl都可以用。打击可以跟据自己的硬件环境，使用相应的opencl SDK。

从官网下载opencl，我用的`opencl+runtime_16.1.2_x64_rh_6.4.0.37`，下载之后解压到一个你习惯使用的路径。在文件夹中找到`install_GUI.sh`。运行这个文件，会出现如下界面：

![1.png](https://image.3001.net/images/20180606/15282684688920.png!small)

然后按照图形界面中的提示内容，按步骤安装opencl就可以了。为了以防万一，我还下载了一个opencl_headers压缩包，这个压缩包中，有*.c文件。安装好opencl之后，hashcat的环境配置就搭好了。

### 安装hashcat

下载hashcat的源码,你可以到hashcat的网站下载源代码。或者直接把github中的hashcat源码复制到你的主机：

    
    
    git clone https://github.com/hashcat/hashcat.git
    

[](https://github.com/hashcat/hashcat.git)

下载hashcat之后，先看源码中的`README.md`,`BUILD.md`，`Makefile`三个文件。`BUILD`文件中是hashcat的安装命令，推荐大家作为参考。`Makefile`文件中是编译代码，包括引用的各各文件和数据库路径。

然后submodule更新

![2.png](https://image.3001.net/images/20180606/15282685248543.png!small)

Make：运行make命令后，会开始进行hashcat源码编译，并提供makefile文件中提供的相关功能。

![3.png](https://image.3001.net/images/20180606/15282685384217.png!small)

Make install：这条命令意味着开始安装hashcat。

安装完成后试运行–b命令,对hashcat进行测试。测试通过，意味着hashcat安装成功。

![4.png](https://image.3001.net/images/20180606/15282685493798.png!small)

如果大家安装3.0之后的hashcat的话，按照上面这些步骤进行操作，基本可以保证hashcat正常运行。如果大家对老版本的hashcat感情很深的话，可以看看下面的内容。

## 古早hashcat的环境配置

前面我们也说了，hashcat3.0之后的版本，不在区分基于CPU或GPU进行计算，都是整合了GPU和CPU的。但是我这里还有`hashcat2.0`和`oclhashcat2.01`。Hashcat2.0在无GPU的环境下进行计算，oclhashcat只能在有GPU的环境下运行下，利用GPU进行计算。现在我们分别来看一下，这两个版本的hashcat如何安装。

早期的hashcat限制条件比较多，需要在gcc4.9以上版本的支撑下运行。所以我们先要配置电脑的gcc，或者把自己的GCC编译器升级到4.9以上。gcc需要用到GMP，MPFR,MPC库，所以需要先主安装这些支撑软件。

### GMP安装

 **下载解压**

配置gcc环境，先要配置GMP，直接到官网下载干净又安全的版本就好了，我从官网上下载了gmp-6.1.2.tar.lz。

没有安装解压命令的，先安装解压命令：

![5.png](https://image.3001.net/images/20180606/15282686844130.png!small)

用lzip命令解压安装包，把gmp解压为一个.tar文件。然后用tar命令把压缩包解压到文件夹。

![6.png](https://image.3001.net/images/20180606/15282687322291.png!small)

 **安装**

    
    
    ./configure –prefix=/usr/local/gmp6.1.1（--prefix后的面的参数为可选，若不选，表示默认安装位置）
    

![7.png](https://image.3001.net/images/20180606/15282688436193.png!small)

![8.png](https://image.3001.net/images/20180606/15282688687019.png!small)

    
    
    make
    

![补.png](https://image.3001.net/images/20180606/15282690358488.png!small)

    
    
    make insatll
    

![9.png](https://image.3001.net/images/20180606/15282689407640.png!small)

Make和make install两个命令的作用，前面我们之前已经说过，这里就不再重复了。

在安装GMP的过程中，提示缺少m4，这个问题不是所有人都会出现的，没有提示这个问题的，可以不用管这一步。

![10.png](https://image.3001.net/images/20180606/15282691412803.png!small)

所以我又安装了m4，先下载解压，m4的安装命令跟GMP的安装命令相同。

![11.png](https://image.3001.net/images/20180606/15282691555465.png!small)

安装成功后记得用man命令测试一下。

### MPFR 安装

 **下载解压**

可以在<ftp://gcc.gnu.org/pub/gcc/infrastructure>下载对应的MPFR安装包

这里是一个后缀为.tar.b2z后缀名的压缩包，b2z的解压命令与前面不同

![12.png](https://image.3001.net/images/20180606/15282692819195.png!small)

 **安装**

安装方法和GMP库的安装命令是一样的，不在赘述。

    
    
    1 ./configure –prefix=/usr/local/mpfr-3.1.4
    2 make
    3 make install
    

### MPC安装

下载解压

在<ftp://gcc.gnu.org/pub/gcc/infrastructure>下载对应的MPC安装包，并解压。

安装

    
    
    1  ./configure –prefix=/usr/local/mpc-1.0.3
    2  make
    3  make install
    

### Gcc的安装

安装

下载解压安装太麻烦了，这次是直接从源里下载的gcc：

![13.png](https://image.3001.net/images/20180606/15282693061485.png!small)

安装gcc后可以通过如下命令，查看gcc的版本信息，输出如下：

![14.png](https://image.3001.net/images/20180606/15282693761658.png!small)

好了，以上就是低版本hashcat的全部配置过程了。

在ubantu下安装hashcat还挺简单的，按顺序操作，不太可能出现问题。如果大家想在服务器上安装hashcat的话，就会有点复杂。主要是配置起来要小心一点。

 **1**.下载并解压

可在<ftp://gcc.gnu.org/pub/gcc/infrastructure>下载对应的gcc安装包，并解压

 **2**.编译安装

要在root用户权限下安装gcc。

    
    
    1  ./configure --dis-checking --enable-languages=c,c++--disable-multilib -with-mpc=/usr/local
    2  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
    3  make     注:make运行的时间很长.
    4  make install
    

**3.** 修改环境变量

    
    
    vim /etc/profile
    
    在最后一行增加export PATH=$PATH:/usr/local/bin。
    保存退出。
    
    source/etc/profile
    

## 基于cuda的Hashcat安装

Hashcat的CUDA版本其实就是oclhashcat。这是专门用于GPU计算的版本。现在官网已经没有2.0左右的hashcat了。这里我利用很早之前预留的hashcat进行实验。

在此部分，我们的介绍分厂两部分：支撑软件的安装以及编译安装oclhashcat2.01

这里我们主要介绍cuda和nvidia的安装。注：本次安装基于服务器的

提示：如果希望通过系统命令来查看及其硬件信息的话，可以用如下命令，查看CPU信息,

![15.png](https://image.3001.net/images/20180606/15282709164552.png!small)

通过具体的参数可以获取相关信息，如下命令组合让可以获取物理CPU的个数以及CPU型号

![16.png](https://image.3001.net/images/20180606/15282709614934.png!small)

通过下面这条命令可以查看设备内存信息。

![17.png](https://image.3001.net/images/20180606/15282709843751.png!small)

### 支撑软件的安装

前面已经介绍了GMP库的安装，这里不再赘述，本节主要介绍Nvidia驱动和CUDA的安装。这是基于CUDA的hashcat需要的特有的支撑软件。

 **下载nvidia驱动**

到nvidia官网下载官方驱动，需要是的346.59或者以后的版本

chmod +x 文件名，就可以让文件成为可执行程序。

![20.png](https://image.3001.net/images/20180606/15282710686381.png!small)

 **修改系统配置(重点！！)**

1.关闭图形界面

将系统inittab文件中的init 5修改为init3。

2.卸载已安装的NV驱动

    
    
    dpkg-l|grep nvidia。
    

3.将开源驱动加入黑名单

这部分重要，我就是因为开始没有做这一步，导致后面的安装出现了各种问题，耽误了大量的时间。这可能是我将该驱动加入到黑名单后，所以上面没有卸载也没有问题。

4.安装nvidia驱动

执行./NVIDIA-Linux-x86_64-346.59.run即可，安装过程可根据提示，选择对应的选项即可。安装完成后，可以将（1）中描述的init：3修改回5，但我并没有修改，也可以。安装完成后后，执行nvidia-smi，可以看到如下的结果，即表示安装正确。（本系统中，我将其安装在/opt/hashcat-deps/ NVIDIA-Linux-x86_64-346.59中，为了后面cudaHashcat2.01安装的方便。大家当然不必如此，可以自行指定）

![不.jpg](https://image.3001.net/images/20180606/1528272371508.jpg!small)

### 安装CUDA

1.下载CUDA

Hashcat2.01需要7.5以上版本的CUDA，CUDA的下载安装方式和NVIDA驱动的下载安装相同。

2.执行CUDA的运行程序

按照图形界面的提示进行安装即可。

### 编译安装oclhashcat

1.下载及解压

前面已经说过很多次了，不再重复。大家能找到2.01版本可以试试，找不到就算了。

2.修改Makefile文件

前文已经描述了，src下的Makefile本系统中，因我只安装了Linux64下的nv版本，所以只修改了配置文件中的相关内容。进入oclHashcat2.01下的src目录，打开Makefile文件，修改对应的参数配置，如下所示（其它的部分可以不用管）：

> CUDA := /usr/local/cuda-8.0 /31行
>
> CUDALIBPATH32 := /usr/lib /32行
>
> CUDALIBPATH64 := /usr/lib64 /33行
>
> GDK :=/opt/hashcat-deps/NVIDIA-Linux-x86_64-346.59 /37行
>
> NV_BITNESS_ALL := 64 /109行
>
> binaries_all:linux64 /126行
>
> kernels_all:nv_all /128行
>
> release:binaries /130行
>
> linux:linux64 /132行
>
> linux64: cudaHashcat64.bin /159行

下图列出了其中部分修改的文档。

![21.jpg](https://image.3001.net/images/20180606/15282710872031.jpg!small)

3.编译安装

在oclhashcat目录下，执行make all，make linux，make nv-all。

执行这三个命令时，会产生大量报错，不用理会，这是其他版本缺少支撑库引起的。我们只用到NV-64这个版本，这些错误对我们不会产生影响。觉得报错碍眼的话，就到`src/Makefile`文件，把无关内容删除或注释掉，就不会出现大规模报错了。

4.收集可执行程序

将oclhashcat目录下生成的`hashcat64.bin`,`hashcat.hcstat`以及`kenerls`目录下的所有文件拷贝到一个文件夹内，同时确保应用程序的可执行权限，运行hashcat64.bin
–b就可以对hashcat进行benchmark测试了。

## 后记

以上就是这篇文章的全部内容，写的有点啰嗦，请大家见谅。下一篇文章，我计划好好说一说hashcat中各个参数的意义和使用方法。

 ***本文作者：EVA。本文属丁牛网安实验室原创出品，转载请注明来自FreeBuf.COM。**

