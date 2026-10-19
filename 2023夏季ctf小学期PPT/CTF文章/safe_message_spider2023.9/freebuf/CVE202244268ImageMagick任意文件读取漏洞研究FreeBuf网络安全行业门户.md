ImageMagick 是一个免费的开源跨平台软件套件，用于显示、创建、转换、修改和编辑光栅图像。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
## Part2 漏洞描述

‍漏洞名称|

ImageMagick任意文件读取漏洞  
  
---|---  
CVE编号| CVE-2022-44268  
漏洞类型| 任意文件读取  
漏洞等级| 6.5 中危 (Medium）  
公开状态| 公开  
漏洞描述|

在 ImageMagick 上的 7.1.0-51 之前的版本中，存在一个信息泄露漏洞，该漏洞可用于在修改 PNG 文件时读取任意文件。  
  
时间线|

2023.01.20 提交

2023.02.06 公开披露  
  
影响产品|

ImageMagick v7.1.0-51  
  
 **分析环境：** Kalix64ImageMagick：7.1.0-49-PHP

## Part3 漏洞复现

搭建好 ImageMagick环境，运行服务在8080端口，然后浏览器访问。

![图片](https://image.3001.net/images/20230518/1684394126_6465d08e81c9553ce97af.jpg!small)

生成验证文件 python ***.py generate -o exp.png -r /etc/passwd

这里表示，漏洞利用，读取/etc/passwd 的文件内容上传验证图片

![图片](https://image.3001.net/images/20230518/1684394144_6465d0a0de3dcd5fa3d87.jpg!small)

保存Your image下面的图片。使用脚本解析生成的图片。得到/etc/passwd文件内容

![图片](https://image.3001.net/images/20230518/1684394154_6465d0aa35536519b9595.jpg!small)

复现成功！

## Part4 漏洞分析

  * 上传图像以触发图像魔术命令，例如“转换”

  * ReadOnePNGImage （coders/png.c：2164）：

![图片](https://image.3001.net/images/20230518/1684394178_6465d0c2bcd985344782f.jpg!small)

\- 读取 tEXt 块：

![图片](https://image.3001.net/images/20230518/1684394189_6465d0cdab3b5bfbf8967.jpg!small)

  * SetImageProfile （MagickCore/property.c：4360）

![图片](https://image.3001.net/images/20230518/1684394200_6465d0d84065f10e66fea.jpg!small)

  * 检查关键字是否等于“配置文件”：

![图片](https://image.3001.net/images/20230518/1684394215_6465d0e74966bd48385fe.jpg!small)

  * 将文本字符串复制为第 4720 行中的文件名，并将内容保存在第4722 行：

![图片](https://image.3001.net/images/20230518/1684394301_6465d13d1e96749329052.jpg!small)

  * FileToStringInfo 将内容存储到string_info->datum， （MagickCore/string.c：1005）：

![图片](https://image.3001.net/images/20230518/1684394311_6465d147b286dc4c51d94.jpg!small)

  * 如果提供了有效（且可访问）的文件名，则内容将返回到调用方函数 （FileToStringInfo），而 StringInfo 对象将返回到 SetImageProperty 函数，从而将 blob 保存到生成的新图像中，这要归功于函数 SetImageProfile：

![图片](https://image.3001.net/images/20230518/1684394320_6465d150a87725416db6f.jpg!small)

攻击者可以使用嵌入任意网站文件内容的下载此新图像。

## Part5 修复建议

1\. 检测上传文件内容；

2\. 修复ImageMagick组件到v7.1.51以上版本。

