# 前言

前段时间的比赛将该cms作为了题目考察，这个cms的洞也被大佬们吃的差不多了，自己也就借此机会来浅浅测试下这个cms残余漏洞，并记录下这一整个流程，谨以此记给小白师傅们分享下思路，有错误的地方还望大佬们请以指正。

# 安装

参考官方文档，给出了很详细的安装说明，如安装遇到问题，可到官方论坛寻找解决方法，常见安装失败问题都有。

<https://gitee.com/iteachyou/dreamer_cms#https://gitee.com/link?target=https%3A%2F%2Fwww.iteachyou.cc%2Farticle%2F55ec2939c29147eca5bebabf19621655>

![image-20230506234239542](https://image.3001.net/images/20230508/1683531243_6458a5eb091c7ecf6ae85.png!small)

该cms项目是基于springboot框架开发的，安装的时候需要的环境为 springboot+redis+mysql+ IDEA

配置文件主要是这两个application-prd.yml和application-dev.yml，需要配置好mysql数据库连接、redis连接以及网页静态资源路径，其余的安装上面的一步步安装即可。

![image-20230506235812299](https://image.3001.net/images/20230508/1683531244_6458a5ec7db5bed7ea346.png!small)

安装成功后访问登陆页面

![image-20230507105459127](https://image.3001.net/images/20230508/1683531245_6458a5edbcafc68adc741.png!small)

管理员账号密码已经给了，直接登录。

![image-20230507001517779](https://image.3001.net/images/20230508/1683531247_6458a5ef5695313989f61.png!small)

# 漏洞测试

## 风格管理模板存在任意编辑文件实现命令执行

经测试，发现后台风格管理模板上传主题压缩包时可以进行污染压缩包theme.json文件，达到目录穿越到服务器敏感目录，从而在模板管理在解析时没有进行检测可以任意编辑系统敏感文件导致GetShell，控制服务器权限。

漏洞产生的主要文件：主题上传Controller文件：`src/main/java/cc/iteachyou/cms/controller/admin/ThemesController.java`，
找到`add`方法。

![img](https://image.3001.net/images/20230508/1683531249_6458a5f10384b8b540202.jpg!small)

首先是判断文件是否存在以及JSON解析是否正确；判断Key是否都存在；判断对应值是否为空；创建theme对象；判断设置路径是否已"default"开头。最后校验主题包各种配置是否正确。确认的话就成功上传。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

但是没有对themePath路径问题进行检测，便可构造目录穿越，这也是该漏洞造成的关键原因。

最后是判断上传的压缩包里的各类信息无误后进入处理保存文件逻辑的save方法。

![image-20230507003001316](https://image.3001.net/images/20230508/1683531250_6458a5f234f24b7df7c85.png!small)

在上传的主题包里的\dreamer\dreamer-cms\templates\default_v3\theme.json文件，将目录穿越的构造替换主题包路径，更改之后theme.json文件内容如下：

    
    
    {  
    "themeName":"新版主题",  
    "themeImage":"http://localhost:8888/resource/img/dreamercms-logo.png",  
    "themeAuthor":"",  
    "themePath":"../../../../../../../../../../../../../../"//此路径要和模板文件夹的名称一致  
    }

虽然有检测，但是在之前themeDir已经被污染了，所以相当于检测相当于没有。接着检查是否有权限，startwith方法也没有问题。

![img](https://image.3001.net/images/20230508/1683531251_6458a5f3c1170751af2fd.jpg!small)``

最后就是保存文件。到此时后台模板已被刚刚传入的构造污染，可以进行利用，效果如下：

将修改后的主题包上传

![image-20230507114351235](https://image.3001.net/images/20230508/1683531252_6458a5f4ec14232de0069.png!small)

风格页面会多出一个新的主题

![image-20230507114501540](https://image.3001.net/images/20230508/1683531254_6458a5f6646263ade8e54.png!small)

点击启用。然后查看模板管理页面，发现目录穿越成功，成功进入服务器的根目录，这时就相当于在自己服务器上编辑修改文件。

![image-20230507130444874](https://image.3001.net/images/20230508/1683531256_6458a5f8209fcd4483683.png!small)

测试文件为/home/www 目录下的1.txt文件，原本是空文件。

![image-20230507142840402](https://image.3001.net/images/20230508/1683531257_6458a5f96b19091153e98.png!small)

在页面修改该文件，添加内容

![image-20230507143018335](https://image.3001.net/images/20230508/1683531258_6458a5fa62e3a573e75fc.png!small)

然后保存，再到服务器里查看，成功将内容加入。

![image-20230507143235384](https://image.3001.net/images/20230508/1683531259_6458a5fb850999c6684b2.png!small)

如果修改authorized_key文件便可进行免密登录，利用压缩校验不正确从而上传任意危险文件，例如一句话木马等来获取系统权限；还可以获取系统passwd文件获取敏感信息，也可以写计划任务进行命令执行。

该漏洞分析到此为止，接着是附件管理模板可以进行任意文件下载、删除。

#

## 附件管理模板可以进行任意文件下载、删除。

漏洞产生主要文件：

src/main/java/cc/iteachyou/cms/controller/admin/AttachmentController.java添加附件功能的代码如下：

![img](https://image.3001.net/images/20230508/1683531260_6458a5fcb89db7e939e11.jpg!small)

首先肯定是先添加附件，这里没有对attachment参数进行过滤。导致保存附件的时候目录穿越的构造就被保留了下来，对其进行解析后就可以将服务器的指定文件随意下载、删除，从而对服务器构成威胁。

下载、删除功能的代码都在同一个文件，都是通过刚刚的attachment参数，然后使用attachment.getFilepath()获取服务器文件路径，对其进行解析。

先看下载功能的代码：

![img](https://image.3001.net/images/20230508/1683531262_6458a5fe1360528cd5edc.jpg!small)

这里也没有对 filePath变量进行过滤，所以总的来说就是添加附件和下载附件的两处代码，都没有对相应的变量进行检测过滤，从而导致漏洞产生。

删除功能的代码：

![img](https://image.3001.net/images/20230508/1683531263_6458a5ff14a0ba1022bc3.jpg!small)

删除的话就没什么好说的，和上面一样的原理，试想下，如果可以任意删除服务器的配置文件，那不就相当于服务器要崩的节奏。

漏洞演示如下：

还是利用刚刚/home/www目录下的1.txt文件

![image-20230507155131691](https://image.3001.net/images/20230508/1683531264_6458a60038388af7e993d.png!small)

在添加附件模块先随便上传一个本地文件（这里随便上传了一个theme.txt文件）

![image-20230507145916803](https://image.3001.net/images/20230508/1683531265_6458a6018706800c9e85a.png!small)

burpsuite抓包如下

![image-20230507145925542](https://image.3001.net/images/20230508/1683531266_6458a6028af5189e94b0a.png!small)

需要改的就是这个filepath参数对应的文件路径，将其修改为

    
    
    ../../../../../../../../../../../../../home/www/1.txt

然后放包。

![image-20230507150052833](https://image.3001.net/images/20230508/1683531267_6458a603ce5c68a6dd37d.png!small)

刷新页面，观察到多了一个theme.txt文件，下载下来并打开内容如下：

![img](https://image.3001.net/images/20230508/1683531269_6458a605161084888127f.jpg!small)

![image-20230507155205283](https://image.3001.net/images/20230508/1683531270_6458a6063a39180de7393.png!small)

服务器里的/home/www/1.txt里的内容193840sswwloP 已成功写入本地theme.txt文件，任意下载文件成功。

删除效果，点击右边的删除。

![image-20230507155303188](https://image.3001.net/images/20230508/1683531271_6458a607946c1e8d3eec1.png!small)

发现该1.txt文件被删除了，任意删除文件成功。

## 模板管理存在任意文件包含

产生漏洞的主要文件：src/main/java/cc/iteachyou/cms/taglib/tags/IncludeTag.java

![img](https://image.3001.net/images/20230508/1683531272_6458a608de21b8ec74591.jpg!small)

If语句只是简单判断值是否为空，但是没有检测过滤字符，导致可以传入目录穿越的构造`../../../../../../../../../../../../../home/www/1.txt`进行文件包含，读取里面内容。接着在模板管理找到
**index_about.html**

将`../../../../../../../../../../../../../home/www/1.txt`写入div标签并保存，如下图

![img](https://image.3001.net/images/20230508/1683531274_6458a60a4a9a659771f36.jpg!small)

接着访问主页里的关于我们：

![img](https://image.3001.net/images/20230508/1683531275_6458a60b6eae409166d1e.jpg!small)

可以看到，成功进行了文件包含，如将构造`/home/www/1.txt`换成`/etc/passwd`这类敏感文件，则被攻击者获取到关键信息，这里也测试下：修改构造

![img](https://image.3001.net/images/20230508/1683531276_6458a60c8eb35e801a0e0.jpg!small)

页面如期输出/etc/passwd文件里的信息。

![img](https://image.3001.net/images/20230508/1683531277_6458a60dc83ccf7153eda.jpg!small)

# 总结

本文测试是在该cms旧版本上进行的，新版本对已有问题已进行了修复，这次对该java实现的cms漏洞挖掘收获满满，对cms安装、部署以及代码审计中要注意的点得到了良好的锻炼。

###  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

