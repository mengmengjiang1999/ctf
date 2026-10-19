**今天给大家介绍的是一款名叫Metaforge的OSINT元数据分析工具，在该工具的帮助下，研究人员可根据标签来过滤数据，并生成动态数据分析报告。**

![OSINT.png](https://image.3001.net/images/20190401/15540951823376.png!small)

## 什么是“元数据”？

简单来说，元数据就是一种跟数据有关的“信息“，这类信息来自于每一份特定文件中的标签数据，每一份文件中都包含了各种各样的数据标签都有各种不同的用途。需要注意的是，元数据的作用非常大，而且用处也非常多，尤其是那些跟信息安全有关的数据域，广大研究人员可以利用这些信息来进行渗透测试或信息收集，例如文件的创建者身份以及当初制作文件所使用的软件信息等等。

### Metaforge依赖组件

1、 必须使用类Unix操作系统（Arch、Debian和RHELLinux 发行版，以及macOS）；

2、 必须使用Python 3.5或更高版本；

3、 必须将所有需要分析的数据存放到/media目录下，请不要在该目录中存放其他文件夹；

### 支持的文件类型

    
    
    dll |docx | doc | exe | gif | html | jpeg| mkv | mp3 | mp4 | odp | ods | odt | pdf |png | pptx| ppt | svg | torrent |wav | xlsx | xls |zip |

## 工具安装

### 安装exiftool

Debian：

    
    
    apt install libimage-exiftool-perl

REHL：

    
    
    yum install perl-Image-ExifTool

Arch Linux：

    
    
    pacman -S perl-image-exiftool

macOS：

    
    
    brew install exiftool

安装依赖组件：

    
    
    pip3 install -r requirements.txt

## 运行Metaforge

1、 将所有需要分析的数据存放到/media目录下；

2、 运行metaforge.py：

    
    
    python3 metaforge.py

当Metaforge结束运行之后，检查User_Projects目录，找到你设置的项目文件，点击index.html文件后即可查看Metaforge为你生成的动态数据分析报告：

![2.png](https://image.3001.net/images/20190331/1554039195_5ca0c19b2301e.png!small)  

## 项目地址

Metaforge：【[GitHub传送门](https://github.com/chriswmorris/Metaforge)】

### 参考资源

1、 Exiftool:【[传送门](https://www.sno.phy.queensu.ca/~phil/exiftool/)】

2、 progress: 【[传送门](https://pypi.org/project/progress/)】

3、 dominate: 【[传送门](https://pypi.org/project/dominate/)】

4、 colorama: 【[传送门](https://pypi.org/project/colorama/)】

5、 pyexifinfo: 【[传送门](https://pypi.org/project/pyexifinfo/)】

***参考来源：[chriswmorris](https://github.com/chriswmorris/Metaforge)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

