回想起比赛的那次，三阶段的时候没有告诉ip地址，用nmap全网扫描，慢的一批。大佬佬说用masscan，速度真的快！（但是我折腾了很久，一直搞不出来，这不，今天搞出来了，发这里保存备用，希望大佬勿喷）

## 0x01.环境

（我用的centos7.1,8.几的实验了不太行，总是说什么加载不出来）

![1625918414_60e98bceb056ce09061dd.png!small](https://image.3001.net/images/20210710/1625918414_60e98bceb056ce09061dd.png!small)

## 0x02.安装一些依赖

yum install git gcc make libpcap-devel
clang![1625918601_60e98c893a55775ff2422.png!small](https://image.3001.net/images/20210710/1625918601_60e98c893a55775ff2422.png!small)

碰到输入y就完事

![1625918635_60e98cab00dc3d2dd62e8.png!small](https://image.3001.net/images/20210710/1625918635_60e98cab00dc3d2dd62e8.png!small)

## 0x03.

然后用xftp将github上的masscan包上传上去

![1625918753_60e98d21b5d1c7dd8b3a5.png!small](https://image.3001.net/images/20210710/1625918753_60e98d21b5d1c7dd8b3a5.png!small)

## 0x04.编译

![1625918873_60e98d99de4566b3e4c69.png!small](https://image.3001.net/images/20210710/1625918873_60e98d99de4566b3e4c69.png!small)

![1625918908_60e98dbcb2f6fdee37b9b.png!small](https://image.3001.net/images/20210710/1625918908_60e98dbcb2f6fdee37b9b.png!small)

## 0x05.添加环境变量

在/etc/profile文件末尾添加如下两行环境变量：

![1625919611_60e9907b17a305815da13.png!small](https://image.3001.net/images/20210710/1625919611_60e9907b17a305815da13.png!small)

PATH=/tools/masscan/bin:$PATH

export PATH

![1625919189_60e98ed5007428c9c5f47.png!small](https://image.3001.net/images/20210710/1625919189_60e98ed5007428c9c5f47.png!small)

保存文件后退出，执行命令 source /etc/profile 使修改的环境变量生效

![1625919206_60e98ee6648ea00816c95.png!small](https://image.3001.net/images/20210710/1625919206_60e98ee6648ea00816c95.png!small)

0x06.检验效果

![1625919239_60e98f07f2b34bf509fe2.png!small](https://image.3001.net/images/20210710/1625919239_60e98f07f2b34bf509fe2.png!small)

![1625919266_60e98f2260f7108590eec.png!small](https://image.3001.net/images/20210710/1625919266_60e98f2260f7108590eec.png!small)

总结：学习这东西真的需要锲而不舍；有些问题稍微放一下，下次来解决，可能有更高效的方法。

