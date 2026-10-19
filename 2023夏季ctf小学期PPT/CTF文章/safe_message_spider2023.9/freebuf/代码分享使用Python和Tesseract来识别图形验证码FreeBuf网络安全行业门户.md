***本文原创作者：ipenox，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

**各位在企业中做Web漏洞扫描或者渗透测试的朋友，可能会经常遇到需要对图形验证码进行程序识别的需求。很多时候验证码明明很简单（对于非互联网企业，或者企业内网中的应用来说特别如此），但因为没有趁手的识别库，也只能苦哈哈地进行人肉识别，或者无奈地放弃任务。在这里，我分享一下自己使用Python和开源的tesseract
OCR引擎做验证码识别的经验，并提供相关的源代码和示例供大家借鉴。**

## 一、关于图形验证码识别与tesseractOCR

尽管多数图型验证码只有区区几个数字或字母，但你可能听说了，在进行机器识别的过程中，你要收集样本，对图片去噪、二值化、提取字符、计算特征，甚至还要祭出神经网络去训练数据进行机器学习……还没开干，退堂鼓早打响三遍了。其实我根本不想去钻研那么多高深的理论，只想要寥寥数行Python代码就搞定它，然后把主要精力投入到更重要的渗透测试中去。在这种情况下，tesseract就能帮上大忙了。

Tesseract的OCR引擎最早是HP实验室开发的，曾经是
OCR业内最准确的三款识别引擎之一。2005年该引擎交给了Google，作为开源项目发布在Google
Project上了。Tesseract提供独立程序和API两种形式供用户使用。纯白色背景、字符规整无干扰像素的验证码图片可以直接调用tesseract程序来进行识别。如要更方便灵活地在自己的程序中进行识别，则可以使用tesseract的API。

## 二、Tesseract的编译和安装

Tesseract的项目主页（<https://github.com/tesseract-ocr/tesseract>）上wiki中有详细的编译安装步骤，大家可以参考，本文中我们将以3.05.01版本为基础。我的系统环境是RHEL
7.4，64位版本。首先用yum安装各种依赖的图形库，然后用源码安装Leptonica（官方主页<http://www.leptonica.com/download.html>，版本需要1.74以上），编译安装很简单，解压后，以默认参数依次执行configure,make,make
install命令即可。安装完之后需执行：

    
    
    exportPKG_CONFIG_PATH=/usr/local/lib/pkgconfig

不然在下一步tesseract的configure脚本会报找不到Leptonica。

将tesseract的源码解压后进入到源码主目录下依次执行：

    
    
    ./autogen.sh
    ./configure--with-extra-libraries=/usr/local/lib
    make
    make install

即可成功安装。

根据项目wiki，Data
Files节的指南下载相应的数据文件，因为我们只识别英文和数字验证码，所以下载3.04/3.05版本的英语文件eng.traineddata即可，下载后放到/usr/local/share/tessdata目录下。至此，tesseract就安装完毕了。

## 三、为Python封装tesseract API

tesseract提供的是C++
API（接口界面是TessBaseAPI类），最核心的函数就是TessBaseAPI::TesseractRect这个函数。为了能在Python中方便地使用，我将其封装为Python模块了，详细代码放在github上：<https://github.com/penoxcn/Decaptcha>。该模块名为decaptcha，源文件包括以下四个文件：

setup.py、decaptcha.i、decaptcha.h和depcaptcha.cpp。

将以上文件放在同一个临时目录下，然后执行以下命令进行编译和安装：

    
    
    python setup.py install

安装时需要调用swig命令，所以系统需要先安装swig。

如果tesseract不是安装在默认的路径下，请参照setup.py代码自行修改相关的头文件和库文件的路径即可。

安装完之后进入Python交互环境试着import一下看是否正常：

    
    
    from decaptcha import Decaptcha

如果报错找不到libtesseract，那可能是tesseract的库目录(/usr/local/lib)没有在Python的库搜索目录中。这时候可以将tesseract的库目录添加到系统的/etc/ld.so.conf文件中（加了之后需要执行ldconfig命令以生效）；或者每次import
decaptcha模块之前，都先执行以下Python代码：

    
    
    import sys
    sys.path.append("/usr/local/lib")

## 四、安装Python PIL库

PIL的全称是Python Imaging
Library，是一个强大而易用的图像库。在其主页（<http://pythonware.com/products/pil/>）下载最新版（截止目前是1.1.7）源代码进行安装。安装之前确保系统已安装了png/jpeg/tiff等图像库。解压缩之后，在主目录下执行python
setup.py install即可。

使用很简单，下面的代码片段从任意格式图片文件创建一个Image对象，进行格式转换，获得其大小和像素数组，只需几行代码：

    
    
    from PIL import Image
    img = Image.open('test.png') # Your image here!  
    img = img.convert("RGBA") 
    pixdata = img.load() 
    width,height = img.size
    print 'imgsize: %dx %d' % (width, height)
    print'pixel[2,4]:', pixdata[2, 4] #eg,(0xD3,0xD3,0xD3,0xFF)

##  **五、实战验证码识别**

至此，进行图形验证码识别的依赖环境都已准备好，我们可以开干了。

识别的流程简单来说如下：

> 1\. 用Image加载图像，转为RGBA格式，然后获取像素数据；
>
> 2\. 将RGBA格式的像素数据转换为0和1的字节串（其实就是二值化处理）；
>
> 3\. 调用decaptcha模块进行图像识别，获得验证码字符串

实际的代码也非常简单，请看我项目Decaptcha目录下的decaptcha_test.py文件，关键代码也就十几行。影响代码长短或复杂性的，就是二值化这一步了。其实很多图形验证码比较简单，细心分析一下，不难得出二值化的条件。下面以我工作中遇到过的一些验证码为例：

![验证码demo.png](https://image.3001.net/images/20180227/15197364027891.png!small)  

有5组，均来自于我公司的不同业务网站。识别代码请参看我项目目录下decaptcha_demo.py文件，所有的示例验证码放在images目录下。大家可以用图片编辑器打开相关的验证码文件观察和分析像素的规律。

第一组aa系列，字符颜色偏白，背景偏黑，所以可试着以像素RGB均值（或总和）大于某个数值为条件进行转换：r+g+b>=480则为1，否则为0。

第二组bb系列，字符有颜色，背景偏白色，转换条件考虑为RGB中是否有两个要素大于0xf0：int(r/240)+int(g/240)+int(b/240)
<=1则为1，否则为0。

第三组cc系列，字符和背景都是单色，但是有不固定位置的点干扰，干扰点颜色与字符颜色相同，但是都是离散的。这种情况下，像素是白色的就是背景0，否则再判断一下是否离散的点，可以简单地判断它右边和下边的点是否都是白色背景来判定。

第四组dd系列，字符颜色偏紫色，并且有背景干扰线。通过将一些样本图片的每个像素的RGB值打印出来，确赫然发现字符像素的G通道值都为0，其它情况要么是背景，要么是干扰线。

第五组ee系列是最复杂的，有干扰线，干扰点，字符也有变形，颜色也不固定。实际上它来源于一个叫做securimage的php库所产生，恐怕不能一两行代码就二值化了。但是仔细观察它的模式会发现，它的大背景、干扰线、干扰点、字符都是用同一种颜色产生。所以我们可以以统计数量的方式来找出哪些是背景颜色（出现次数最多的自然是背景颜色）。另外我们再统计每个字符的颜色与背景颜色的偏差(将rgb差值的平方加起来)，找出干扰线、字符与背景色的偏差值的阈值范围，再将其在二值化的时候进行应用，也可以成功地将其二值化。而字符变形的问题则不需要担心，交给tesseract就可以了。

在二值化的时候，我在屏幕上用# 符号打印出了二值化后的图像，大家可以看下效果：

    
    
    python decaptcha_demo.py aa aa1.gif

![识别aa1.png](https://image.3001.net/images/20180227/1519736461478.png!small)  

验证码实际是5648，识别为5649，错了一位。

下面来个正确识别的：

    
    
    python decaptcha_demo.py bb bb1.jpg

![识别bb1.png](https://image.3001.net/images/20180227/15197369327012.png!small)

第五组的识别情况：  

    
    
    python decaptcha_demo.py ee ee9.png > 1.txt

因图片有点长，超过了终端的列数，故输出到txt文件后再用notepad++打开的：

![识别ee9.png](https://image.3001.net/images/20180227/15197364863281.png!small)  

验证码实际是912065，识别为912085，错了一位。

再看看总体成绩如何：

> aa组10个验证码，整体正确识别的有5个。
>
> bb组10个验证码，整体正确识别的3个。
>
> cc组10个验证码，整体正确识别的9个。
>
> dd组10个验证码，整体正确识别的3个。
>
> ee组10个验证码，整体正确识别的4个。

aa组、cc组和ee组识别得还可以，没有识别出来的多数仅错了一个字符。而bb和dd组识别得较差，没有识别出来的可能都错了两三个字符。

这份成绩单，咋看之下，有些朋友可能觉得很不好看。但是，请不要太悲观，要想想投入产出比，大多数情况下，除了固定的模式化代码外，我们只需要编写寥寥几行二值化的代码就可以收获输出了啊，这意味着在测试时，程序自动化就可以搞了啊：不求百分之一百，只求十里有一发。即使只有30%的识别率，连续识别5个图片，获得其中一个准确识别的概率也达到了86%，无非多浪费一些Web请求而已。

因为Image库支持从内存中加载图片，所以与requests库的结合也是非常的方便，直接通过HTTP请求下载下来，将内容丢给Image就可以了：

    
    
    import requests，StringIO
    r =requests.get(imgurl)
    imgbuf = StringIO.StringIO(r.content)
    img =Image.open(imgbuf)

是不是很简单很愉快？

## 六、后记

通过以上的例子和代码，大家可以初探tesseract的能力。实际上tesseract支持学习，通过样本训练，可以大幅提高它的识别准确率，当然这个过程就有点复杂了，也不符合本文追求敏捷的宗旨。经过多年的技术对抗，传统的图片验证码已经显得过时了，但仍有很多企业网站在大量使用，希望本文能够给大家一些启发和帮助。

 ***本文原创作者：ipenox，本文属FreeBuf原创奖励计划，未经许可禁止转载**

