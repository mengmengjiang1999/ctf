## 前言

 **在CTF比赛中，往往会涉及到RSA解密类的题目，有了这个工具(基于python2.x)做起来就得心应手了。**

 **![页首配图](https://image.3001.net/images/20180928/15381188678677.png!small)**

## 0x1 安装

在下载前建议把ubuntu源设置为aliyun,速度谁用谁知道。

使用命令行：

    
    
    git clone <https://github.com/Ganapati/RsaCtfTool.git> 

或者去github下载zip包解压：

![把ubuntu源设置为aliyun](https://image.3001.net/images/20180926/1537929693_5baaf1dd0c140.png!small)

    
    
    cd RsaCtfTool  //进入这个目录

安装python第三方库

    
    
    pip install -r requirements.txt

其实是这4个(PyCrypto,GMPY2,SymPy,requests) python库，在安装GMPY2,SymPY的时候会报错，因为有些环境还要下载：

> mpfr,The MPFR library is a C library for multiple-precision floating-point
> computations with correct rounding.
    
    
    v=4.0.1
    wget http://www.mpfr.org/mpfr-current/mpfr-${v}.tar.bz2
    tar -jxvf mpfr-${v}.tar.bz2 && cd mpfr-${v}
    ./configure
    make && make check && make install

下载编译大概要10多分钟：

![下载编译](https://image.3001.net/images/20180926/1537928472_5baaed18e1fb3.png!small)到这里就是mpfr安装完成了。

接下来下载MPC：

    
    
    v=1.1.0
    wget ftp://ftp.gnu.org/gnu/mpc/mpc-${v}.tar.gz
    tar -zxvf mpc-${v}.tar.gz && cd mpc-${v}
    ./configure
    make && make check && make install

![MPC](https://image.3001.net/images/20180926/1537928808_5baaee68e1f9b.png!small)要注意的是一定要先安装好mpfr,才能安装MPC,不然会报这个错误：

> configure: error: libmpfr not found or uses a different ABI (including
> static vs shared)  
>

大概也是10分钟左右。

参考：<https://www.cnblogs.com/pcat/p/5746821.html>  

这时可以再次进入CtfRsaTool目录，再次运行`pip install -r requirements.txt`,就能成功安装python第三方依赖了。

![进入CtfRsaTool目录](https://image.3001.net/images/20180926/1537929318_5baaf0662e745.png!small)接下来就可以愉快的使用RsaCtfTool.py了。

## 0x2 使用

使用`python RsaCtfTool.py`去执行，如果./RsaCtfTool.py执行会报Crypto库不存在。

![使用python
RsaCtfTool.py去执行](https://image.3001.net/images/20180926/1537929967_5baaf2ef66879.png!small)用法一：已知公钥(自动求私钥)
--publickey，密文 ----uncipherfile。

这里有一道rsa的ctf题目:<https://pan.baidu.com/s/1-LenHQbB9MJ30HhrScYLcQ>

将文件解压复制到RsaCtfTool里：

    
    
    python RsaCtfTool.py --publickey 公钥文件 --uncipherfile 加密的文件

![将文件解压复制到RsaCtfTool里](https://image.3001.net/images/20180926/1537930441_5baaf4c9b359a.png!small)用法二：已知公钥求私钥。

    
    
    >RsaCtfTool.py --publickey 公钥文件 --private

![已知公钥求私钥](https://image.3001.net/images/20180926/1537930637_5baaf58d72e4f.png!small)用法三：密钥格式转换

把PEM格式的公钥转换为n，e

    
    
    >python RsaCtfTool.py --dumpkey --key 公钥文件

![umpkey --key
公钥文件](https://image.3001.net/images/20180926/1537930952_5baaf6c88b033.png!small)

把n,e转换为PEM格式

    
    
    python RsaCtfTool.py --createpub -n 782837482376192871287312987398172312837182 -e 65537

![捕获12.PNG](https://image.3001.net/images/20180926/1537931265_5baaf801b3f82.png!small)
项目地址参考:<https://github.com/Ganapati/RsaCtfTool>  

***本文作者：Cosmop01itaN，转载请注明来自FreeBuf.COM**

