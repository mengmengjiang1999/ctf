> 摘要：对于WEB漏洞的越权漏洞检测，除了人工检测方法外，还有没有更好的办法。

# 0x00 前言

说起WEB安全大家能想到什么？SQL注入、XSS、越权、文件上传、CSRF等等漏洞？还是WVS、APPscan、openVAS等这些扫描器呢？

如果你想到的是扫描器，那么，世面上这些扫描器都有哪些优缺点呢？比如它们是否能扫描越权漏洞呢？扫描时是否会对系统产生影响等等问题呢？如果它们都不能检测越权漏洞，同时也不能像人工检测那样避免对目标系统产生影响，那么有没有一种可以趋于人工与扫描器之间的方法，即能像扫描器那样快速，又能像人工那样检测越权等业务漏洞的产品呢？如果您还没听说过类似的产品，那么今天我就来分享一款自主开发的WEB安全扫描平台——safeScan。

# 0x01 产品简介

safeScan是一套基于python开发的web应用系统，它可以完成半人工的WEB安全扫描，其核心功能是通过开启http代理方式获取人工操作网站的请求数据，然后将所有请求数据与横向或纵向越权账号的数据进行对比，从而发现越权漏洞。

基于以上核心功能，该扫描平台还提供了多种扫描形式，如单接口越权扫描、自定义代理数据收集扫描、平台集成代理扫描、SQL注入、XSS等的单接口、多接口扫描。同时还支持扫描结果汇总展示等。效果展示图如下：

![1603443278_5f929a4eafc708b72cadc.png!small](https://image.3001.net/images/20201023/1603443278_5f929a4eafc708b72cadc.png!small)

图：首页

![1603443289_5f929a595c9a696e513eb.png!small](https://image.3001.net/images/20201023/1603443289_5f929a595c9a696e513eb.png!small)

图：批量扫描

# 0x02 环境准备

我们将通过一系列文章分享该扫描平台从环境准备到安装使用，今天我们就讲讲环境准备，Safecan运行所需环境如下：

windows7-10/linux

python==3.8

pip==20.0.0

django==2.2 web框架

celery==5.0.1 异步/消息处理

redis==3.3.2 内存数据库

requests==2.21.0 页面请求模块

PyMySQL==0.10.0 mysql连接器

pyecharts==1.8.1 图表可视化

ueditor==1.4 富文本编辑器

mitmproxy==5.1.1 中间人代理工具

mysql==5.7.28 数据库

注意：由于该系统是之前开发好的，文章是后续写的，所以环境准备中罗列的东西可能不全，如发现需要增加或修改的地方会在后续文章中说明。

# 0x03 安装过程问题处理

 **django与mysqldb版本兼容性问题**

  * 如果没有安装pymysql，而是通过mysqlclient运行，那么会报类似如下错误：core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
  * Django连接MySQL时默认使用MySQLdb驱动，但MySQLdb不支持Python3，因此这里需要将MySQL驱动设置为pymysql。
  * 安装完之后，需要在工程文件同名目录下的py中添加以下代码即可（import pymysql；pymysql.install_as_MySQLdb()）
  * 同时需要注释掉site-packages/django/db/backends/mysql/base.py文件中的35/36行。  
if version < (1, 3, 3):  
raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have
%s" % Database.__version__)

  * 还需要修改site-packages/django/db/backends/mysql/base.py文件中的46行，将query = query.decode(errors='replace')修改为query = query.encode(errors='replace')，否则会报如下错误：AttributeError: ‘str’ object has no attribute ‘decode’
  * 修改完以上内容后，django连接mysql就没有问题了。

 **django高版本导致'staticfiles'错误问题**

  * 由于该是两年前开发的，当时使用的是2版本，而现在使用pip默认安装的都是高版本，所以会报如下错误： **TemplateSyntaxError at /en/admin/login/ 'staticfiles' is not a registered tag library. Must be one of:**
  * 解决方法就是降低django版到2以下
  * 其它安装基本没有什么问题，安装完之后就可以准备后续的开发、部署、运行。

# 0x04 下集预告

环境安装其实也没有什么可讲的，但是安装又是一个因不同人不同电脑会产生问题最多的地方，所以今天我们的内容就先分享到这里，后续有问题的同学可以在后台留言，我们将一一整理，然后回复大家。文章会同步发布在freebuf和公众号平台，同名：andiSEC

下集主要讲解safeScan运行环境中的所有模块之间的互通与联调，以及部分代码讲解。

