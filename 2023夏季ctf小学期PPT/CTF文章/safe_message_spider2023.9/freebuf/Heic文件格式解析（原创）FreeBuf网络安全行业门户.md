**heic是一种图像格式，自iOS 11开始，苹果将heic设置为图片存储的默认格式。这种图片无法在windows
系统中直接打开。<http://nokiatech.github.io/heif/> 网站提供了详细的该格式文件的读写方法，及如何将该种文件转化为“jpg”
类型图像文件。通过二进制查看，该文件结构是一种长度桢数据结构，为四字节长度+四字节类型+数据的格式。  
**

 **选取网上一张示例图片(<https://raw.githubusercontent.com/nokiatech/heif/gh-pages/content/images/cheers_1440x960.heic>)，按照该方法提取一级结构如下：**

总长度（0x） a1cb

偏移位置（0x）** 4字节长度（0x）** 类型

a1cb

0000 **001c **ftyp

001c **0200 **meta

021c **942d **mdat

9649 **0b72 **mdat

a1bb **0010 **mdat

![无标题.png](https://image.3001.net/images/20180311/15207682829798.png!small)  

（上图是部分二进制图片格式）

 **对类型为“meta” 的段再进行类似的结构提取方式为长度+类型+数据，如果长度为0直接跳过 ：结果如下：**

偏移位置（0x）** 4字节长度（0x）** 类型

0024 **0000 **

0028 **0021 **hdlr

0049 **000e **pitm

0057 **0034 **iloc

008b **004e **iinf

00d9 **001a **iref

00f3 **0129 **iprp

 **在说明文档中有格式解析，和每个参数的实际意义：**

_<http://standards.iso.org/ittf/PubliclyAvailableStandards/c066067_ISO_IEC_23008-12_2017.zip>_
。 **我们的示例简单列举如下：**

**hdlr:** 00 00 00 00

 **pitc:** 00 00 00 00

 **pitm:** item_ID= 4e 22

 **iloc:** item_count=2

item_ID=4e 22,extent_count=1,extent_offset=0x224,extent_length=0x9425

item_ID=4e 23,extent_count=1,extent_offset=0x9651,extent_length=0xb6a

 **iinf:** entry_count=2

 **infe:** item_ID= 4e 22 item_type=hvc1

infe: item_ID=4e 23 item_type=hvc1

 **iref:**

referenceType=thmb,from_item_ID=4e 22,ref_count=1,to_item_ID=1;

 **iprp:**

 **下面图片是文档中对格式的说明，和我们实际的图片略有差异：**

![无标题.png](https://image.3001.net/images/20180311/15207692907290.png!small)

