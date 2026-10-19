**作者：深信服千里目实验室**  
**原文链接：<https://mp.weixin.qq.com/s/9IWS0VX90CUJzhh8i0myAw>**

## 一、组件介绍

### 1.1 基本信息

ThinkCMF是一款基于PHP+MYSQL开发的中文内容管理框架。ThinkCMF提出灵活的应用机制，框架自身提供基础的管理功能，而开发者可以根据自身的需求以应用的形式进行扩展。每个应用都能独立的完成自己的任务，也可通过系统调用其他应用进行协同工作。在这种运行机制下，该系统的用户无需关心开发SNS应用是如何工作的，但他们之间又可通过系统本身进行协调，大大的降低了开发成本和沟通成本。

普通的CMS（内容管理系统）一般不能完成所有的需求，而因为CMS在ThinkCMF内部只是一个应用的形式存在，所以使用ThinkCMF可以用CMS来管理内容，用电影网站系统来管理视频，用电商系统来管理电商网站。这些程序不会影响，也可以模块化的增加或减少应用。

ThinkCMF自身层次非常清晰，逻辑也相当的严谨，特别是系统自带的protal应用非常适合PHP初学者使用。采用了国内优秀的开源php框架ThinkPHP使得ThinkCMF具备了优秀的性能以及良好的安全性。

### 1.2 版本介绍

ThinkCMF基于ThinkPHP框架进行了二次开发，经过逐年演化，逐渐成为了一款功能齐全的内容管理框架。ThinkCMF发展至今已有近8年历史，其核心开发系列共有以下三个，即ThinkCMF
V1.x系列，ThinkCMFX 2.x系列，ThinkPHP 5.x系列。ThinkCMF同时与ThinkPHP的版本有以下对应关系：ThinkCMF
V1.x系列版本基于ThinkPHP 3.1.3版本进行开发的、ThinkCMFX 2.x系列版本是基于ThinkPHP
3.2.3而进行开发、ThinkCMF 5.x系列版本是基于ThinkPHP 5版本开发的。其中ThinkCMF 1.x、ThinkCMFX
2.x官方已经停止了维护，ThinkCMF 5.x属于现阶段核心版本。而ThinkCMFX
2.x系列基于其优良的性能，也在过去积累了很多的历史客户，使得ThinkCMF 5与ThinkCMFX 2在市场上并驾齐驱。版本细分如下图所示：

![version_info.PNG](https://images.seebug.org/content/images/2020/12/03/1606977134000-1xtkdr.png-w331s)

### 1.3 使用量及使用分布

根据全网数据统计，使用ThinkCMF的网站多达2万余个，其中大部分集中在国内，占使用量的75%以上。其中，浙江、北京、山东、广东四省市使用量最高，由此可见，ThinkCMF在国内被广泛应用。通过网络空间搜索引擎的数据统计和柱状图表，如下图所示。

![tongji.PNG](https://images.seebug.org/content/images/2020/12/03/1606977135000-2aqpvd.png-w331s)

## 二、高危漏洞介绍

通过对ThinkCMF漏洞的收集和整理，过滤出其中的高危漏洞，可以得出如下列表。

漏洞名称 | 漏洞ID | 影响版本 | 漏洞披露日期  
---|---|---|---  
ThinkCMF X2.2.3 任意文件删除漏洞 | CVE-2018-16141 | ThinkCMFX <=2.2.3 | 2018  
ThinkCMF X2.2.3 SQL注入漏洞 | CVE-2018-19894 | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3 SQL注入漏洞 | CVE-2018-19895 | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3 SQL注入漏洞 | CVE-2018-19896 | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3 SQL注入漏洞 | CVE-2018-19897 | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3 SQL注入漏洞 | CVE-2018-19898 | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3 前台文件上传漏洞 |  | ThinkCMFX <=2.2.3 | 2018  
ThinkCMF X2.x缓存Getshell（display函数） |  | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3代码注入漏洞（fetch函数） |  | ThinkCMFX <= 2.2.3 | 2018  
ThinkCMF X2.2.3代码注入漏洞（plugin类） |  | ThinkCMFX <= 2.2.3 | 2019  
ThinkCMF 后台任意代码执行漏洞1 | CVE-2019-6713 | ThinkCMF <= 5.0.190111 | 2019  
ThinkCMF 后台任意代码执行漏洞2 | CVE-2019-7580 | ThinkCMF <= 5.0.190111 | 2019  
  
从中可以看出，ThinkCMF近年出现的高风险漏洞主要分布在ThinkCMF
X2.x系列中，且其中主要集中在SQL注入漏洞，看过笔者上一篇ThinkPHP分析文章的读者都知道，ThinkPHP
3.x系列存在大量SQL注入风险函数，不出意外，这些风险函数最终都在二次开发的基础上被使用，造成了SQL注入漏洞。幸好，在ThinkCMF开发的的过程中，开发人员做过一些SQL注入的风险控制，这就使得这些SQL注入漏洞被利用的难度会大大增加，提高了框架被攻陷的门槛。

ThinkCMF
X2.x系列除了以上的SQL注入的风险之外，另外最大的风险存在于ThinkCMF框架中Controller中的两个模板操作函数，fetch()以及display()函数，这两个函数在处理模板文件的过程中，存在漏洞，会导致任意代码注入，最终造成任意代码执行，且不需要任何权限，所以该漏洞的风险很高。

我们再看ThinkCMF 5系列，这个系列的安全性基于ThinkPHP
5的安全性提高也随之大大提高，近两年比较出名的就是CVE-2019-6713、CVE-2019-7580两个后台任意代码执行漏洞，这两个漏洞源于在后台处理router的时候，没有经过严格验证，导致攻击者可以通过单引号逃逸，将恶意代码注入到ThinkCMF数据库中，最终代码会产生在router.php文件中。

## 三、漏洞利用链

基于ThinkCMF高危漏洞，我们可以得出几种可以利用的ThinkCMF框架漏洞利用链。

#### 3.1 ThinkCMFX 2.x GetShell

![ThinkCMFX_2_chain.png](https://images.seebug.org/content/images/2020/12/03/1606977136000-3dzjhf.png-w331s)

**ThinkCMF 2.x - GetShell**

  * ThinkCMF 低版本可以使用以上代码注入漏洞，获取服务器权限。

#### 3.2 ThinkCMF 5.x GetShell

![ThinkCMF_5_chain.png](https://images.seebug.org/content/images/2020/12/03/1606977138000-4ftzdl.png-w331s)

**ThinkCMF 5.x - GetShell**

  * 首先明确ThinkCMF框架系列版本。
  * 首先需要获取到ThinkCMF的后台登录账号密码，执行ThinkCMF后台代码执行漏洞，即可getshell。

## 四、高可利用漏洞分析

从高危漏洞列表中，针对ThinkCMF高可利用漏洞进行深入分析。

### 4.1 ThinkCMF 2.x 代码注入漏洞（fetch函数）

#### 4.1.1 漏洞简介

漏洞名称：ThinkCMF 2.x 代码注入漏洞（fetch函数）  
漏洞编号：无  
漏洞类型：代码注入  
CVSS评分：无  
漏洞危害等级：高危

#### 4.1.2 漏洞概述

ThinkCMF是一款基于ThinkPHP+MySQL开发的中文内容管理框架。攻击者可利用此漏洞构造恶意的url，向服务器写入任意内容的文件，从而实现远程代码执行。该漏洞只适用windows系统。

#### 4.1.3 漏洞影响

1.6.0 <= ThinkCMFX <= 2.3.0

#### 4.1.4 漏洞修复

1.将 HomebaseController.class.php和AdminbaseController.class.php 类中 display 和
fetch 函数的修饰符改为 protected

2.目前厂商已不维护2.x版本，请受影响的用户使用升级到ThinkCMF 5系列或者采用以上临时解决方案

#### 4.1.5 漏洞分析

分析该漏洞，我们要详细跟踪一下content参数值的流向，我们从程序入口开始往后跟踪：

Step1：首先通过ThinkPHP.php入口文件进入到Think.class.php文件中的`start()`函数；

####
![411.png](https://images.seebug.org/content/images/2020/12/03/1606977139000-5dyrqv.png-w331s)

在start()函数中，进入到App.class.php文件中的主函数`run()`;

![412.png](https://images.seebug.org/content/images/2020/12/03/1606977140000-6mmtld.png-w331s)

进入到文件中的exec()函数，exec函数的作用就是解析请求的路由，这一块的处理模式即为ThinkPHP的处理模式；

![413.png](https://images.seebug.org/content/images/2020/12/03/1606977141000-7cmtvn.png-w331s)

![414.png](https://images.seebug.org/content/images/2020/12/03/1606977144000-8hetzs.png-w331s)

通过路由解析，解析出了请求的module、action，分别为:`view`的`fetch`。然后通过invokeAction()函数中的反射，定位到具体类以及具体的操作函数。以下即为第一阶段的路由解析阶段的调用链。

![415.png](https://images.seebug.org/content/images/2020/12/03/1606977148000-9fsilo.png-w331s)

Step2：在定位了操作函数之后，首先定位到了HomebaseController.php文件中的fetch()函数；

![416.png](https://images.seebug.org/content/images/2020/12/03/1606977150000-10cyitd.png-w331s)

然后通过`return parent::fetch`返回到其父类的Controller.php文件中的fetch()函数；

![417.png](https://images.seebug.org/content/images/2020/12/03/1606977151000-11paqtu.png-w331s)

根据之前的路由解析，我们知道即将调用View然后即进入到View.class.php文件中的fetch()函数，进行模板处理。

![418.png](https://images.seebug.org/content/images/2020/12/03/1606977152000-12ahmyq.png-w331s)

我们可以看到该函数中，再起始有一个`ob_start();`，然后对content进行处理后，通过`$content =
ob_get_clean();`将content清空，所以我们在清空之后下断点，然后我们即进入到view_parase模块，通过跟踪，我们解析出了模块对应的是ParseTemplateBehavior.php文件；

![419.png](https://images.seebug.org/content/images/2020/12/03/1606977154000-13esxcu.png-w331s)

进入到`ParseTemplateBehavior::run()`主函数中，我们将面临着两个分支，我们分别在两个分支打上断点，来验证此处程序的走向。我们发现content的值是第一次发送的话，将会走else分支，如果不是第一次发送，将会走第一个分支，从判断条件也可得知，如果缓存中存在content的缓存，即走if分支，否则就走else分支。

![](https://images.seebug.org/content/images/2020/12/03/1606977155000-4110.png-w331s)

我们利用第一次发送的poc，进入到else分支中的fetch函数，我们发现进入到Template.class.php文件中的fetch函数，

![](https://images.seebug.org/content/images/2020/12/03/1606977155000-4111.png-w331s)

我们可以看到fetch函数中调用了`loadTemplate()`函数，进入到该函数中，我们可以看到content最终被赋值到了
`$tmplContent`参数中；

![](https://images.seebug.org/content/images/2020/12/111b603e-2c10-4728-91b3-f7c2f20da14e.png-w331s)

然后`$tmplContent
(content)`经过编译后通过`Storage::put`函数保存，最终将文件生成到data/runtime/Cache/Portal文件夹中。最后，最后在Template.class.php文件中调用了`Storage::load`加载cache文件，最终导致代码执行。

![](https://images.seebug.org/content/images/2020/12/f93bcca1-e313-48d5-9c17-45d383ee42e9.png-w331s)

### 4.2 ThinkCMF 2.2.x 前台任意文件上传漏洞

#### 4.2.1 漏洞简介

漏洞名称：ThinkCMF 2.2.x 前台任意文件上传漏洞  
漏洞编号：无  
漏洞类型：文件上传  
CVSS评分：无  
漏洞危害等级：高危

#### 4.2.2 漏洞概述

ThinkCMF是一套基于ThinkPHP的CMS（内容管理系统）。在 **ThinkCMFX 2.2.3**
最终版及以前版本中，存在一处任意文件上传漏洞（需要普通用户权限，默认可注册）。远程攻击者可利用该漏洞上传任意可执行文件。

#### 4.2.3 漏洞影响

1.6.0 <= ThinkCMFX <= 2.2.3

#### 4.2.4 漏洞修复

目前厂商已不维护2.x版本，请受影响的用户使用升级到ThinkCMF 5系列。

#### 4.2.5 漏洞分析

在/application/Asset/Controller/UeditorController.class.php中，存在一个上传接口，但是在上传前存在一个权限验证，即登录后才可上传，前台会员与后台管理员权限均可。

![](https://images.seebug.org/content/images/2020/12/a0b2e357-c4ca-453a-ab3a-fd95d53c2ed3.png-w331s)
然后进入到upload方法中，该方法支持上传多种类型文件，我们可以选择uploadfile接口继续跟踪，该接口调用了_ueditor_uplaod()函数；

![](https://images.seebug.org/content/images/2020/12/aaefe29f-d075-473b-800c-d02da95b9c25.png-w331s)

进入到_ueditor_upload()函数中，我们发现这里是通过`$allowed_exts=explode(',',
$upload_setting[$filetype]);`来进行后缀白名单设置的，明显可以看出程序想用白名单数组，但是使用了 **
filetype]**获得的是一个数组，包含upload_max_filesize和extensions两个key，而explode的作用为把第二个参数通过字符串分割成数组，导致出错，最终返回了一个Null；

故此处少了 **[‘extensions’]** ，正确写法应该是 ** upload_setting);**，此处最终会导致
**$allowed_exts** 的值为Null，导致白名单失效。

![](https://images.seebug.org/content/images/2020/12/fb1ec198-8306-4bd4-9392-52ad7147c95e.png-w331s)

然后就将调用Upload.php文件中的upload()函数，进行文件上传操作

![](https://images.seebug.org/content/images/2020/12/ad3cc7d1-f52d-4785-8a4d-6a58dc579950.png-w331s)

进入到upload()函数中，要进入一个check();

![](https://images.seebug.org/content/images/2020/12/804c692f-0068-4357-bbe4-57a90088cebc.png-w331s)

check()中将进行后缀检查checkExt()；

![](https://images.seebug.org/content/images/2020/12/bc12e8cb-8695-4996-a22b-470829c82e38.png-w331s)

在checkExt方法中, 从刚才的分析可以知道$this->config[‘exts’]为null, empty(null)为true,
所以直接返回true了,不会再判断后缀了。

![](https://images.seebug.org/content/images/2020/12/b928486a-d5e5-4753-bfe6-991c248be061.png-w331s)

在check之后, 通过getSaveName生成最终保存的文件名;

![](https://images.seebug.org/content/images/2020/12/4e910dcf-3625-416a-85d2-2dd24d838a56.png-w331s)

所以在$rule为$config中的savename属性值 array(‘uniqid’,’’)，文件的后缀来自, `$ext =
empty($this->config['saveExt']) ? $file['ext'] : $this->saveExt;`
在默认的上传配置信息中’saveExt’ => ‘’,saveExt为空, 所以这里不会强制修改文件的后缀而是直接使用的上传文件名的后缀。

![](https://images.seebug.org/content/images/2020/12/db21af98-f487-4c8e-b0ba-49b3c745a02e.png-w331s)

生成好文件名之后, 就直接通过save方法进行上传了。save方法中已经没有了任何后缀校验, 所以直接实现了任意文件上传。

![](https://images.seebug.org/content/images/2020/12/2951b1a0-0aca-427d-aed5-2c5d26173566.png-w331s)

最终通过json数据将文件上传的内容返回。

![](https://images.seebug.org/content/images/2020/12/e0afd4f8-5568-48d7-b402-3b299ce9880c.png-w331s)

### 4.3 ThinkCMF 2.x 代码注入漏洞（display函数）

#### 4.3.1 漏洞简介

漏洞名称：ThinkCMFX 代码注入漏洞(通过缓存GetShell)  
漏洞编号：无  
漏洞类型：代码注入  
CVSS评分：无  
漏洞危害等级：高危

#### 4.3.2 漏洞概述

ThinkCMF是一套基于ThinkPHP的CMS（内容管理系统）。由于ThinkCMF 2.x使用了ThinkPHP
3.x作为开发框架，默认情况下启用了报错日志并且开启了模板缓存，导致可以使用加载一个不存在的模板来将生成一句话的PHP代码写入data/runtime/Logs/Portal目录下的日志文件中，再次包含该日志文件即可在网站根目录下生成任意PHP文件。

#### 4.3.3 漏洞影响

1.6.0 <= ThinkCMFX <= 2.2.3

#### 4.3.4 漏洞修复

1.将 HomebaseController.class.php和AdminbaseController.class.php 类中 display 和
fetch 函数的修饰符改为 protected

2.目前厂商已不维护2.x版本，请受影响的用户使用升级到ThinkCMF 5系列或者采用以上临时解决方案

#### 4.3.5 漏洞分析

我们从程序入口开始往后跟踪：

Step1：首先通过ThinkPHP.php入口文件进入到Think.class.php文件中的`start()`函数；

![](https://images.seebug.org/content/images/2020/12/9b17e98c-2080-483b-b857-dc1aa09e5ff0.png-w331s)

在start()函数中，进入到App.class.php文件中的主函数`run()`;

![](https://images.seebug.org/content/images/2020/12/1c518557-23db-4955-bdc9-c6353053467f.png-w331s)

进入到文件中的exec()函数，exec函数的作用就是解析请求的路由，这一块的处理模式即为ThinkPHP的处理模式；

![](https://images.seebug.org/content/images/2020/12/fa30b372-6397-4a8a-97f1-fcc2b41abab8.png-w331s)

![](https://images.seebug.org/content/images/2020/12/ddf81edb-78bb-40ff-bd83-35d8e1df6059.png-w331s)

通过路由解析，解析出了请求的module、action，分别为:`HomebaseController`的display()。然后通过invokeAction()函数中的反射，定位到具体类以及具体的操作函数。以下即为第一阶段的路由解析阶段的调用链。

![](https://images.seebug.org/content/images/2020/12/59c7c909-da7a-4205-8b36-92056789498a.png-w331s)

Step2：在定位了操作函数之后，首先定位到了HomebaseController.php文件中的display()函数；然后入到模板解析parseTemplate()函数；

![](https://images.seebug.org/content/images/2020/12/5733c540-0ee9-41db-8cc1-d3f86ac47ae9.png-w331s)

在解析过程中，分别解析出了路径path，module，以及模板文件名，$template.html；然后进行文件检验环节；

![](https://images.seebug.org/content/images/2020/12/2ee70879-3609-484c-ae45-c87428490402.png-w331s)

通过if(!file_exists_case(file);验证文件是否存在，若文件不存在，则系统异常报错，进入到E()中，抛出异常。

![](https://images.seebug.org/content/images/2020/12/9709cfd9-8ba8-4365-9729-b047140b79c7.png-w331s)

![](https://images.seebug.org/content/images/2020/12/a6074f77-8edb-4112-b342-a540d0362aff.png-w331s)

![](https://images.seebug.org/content/images/2020/12/62d04ed7-562f-482f-880a-99da7e4cf890.png-w331s)

![](https://images.seebug.org/content/images/2020/12/6180e781-cc2a-43e3-aefd-d5bccc7a3c15.png-w331s)

Step3：在将代码注入到log文件中，然后再通过view.class.php在通过display()函数中的fetch()函数解析日志文件，最后执行日志文件中的恶意代码。

![](https://images.seebug.org/content/images/2020/12/e92d4fd3-e387-43f9-9905-94fbf61b5e6f.png-w331s)

![](https://images.seebug.org/content/images/2020/12/627077e1-ac2e-49b0-92e5-d280cf68ccb4.png-w331s)

### 4.4 ThinkCMF 5.x后台 远程代码执行漏洞

#### 4.4.1 漏洞简介

漏洞名称：ThinkCMF 5.x后台 远程代码执行漏洞  
漏洞编号：CVE-2019-6713  
漏洞类型：代码注入  
CVSS评分：【CVSS v2.0：7.5】【CVSS v3.0：9.8】  
漏洞危害等级：高危

#### 4.4.2 漏洞概述

ThinkCMF是一套基于ThinkPHP的CMS（内容管理系统）。ThinkCMF
5.0.190111版本中的app/admincontroller/RouteController.php文件存在一个代码注入。远程攻击者可利用该漏洞执行任意的PHP代码。

#### 4.4.3 漏洞影响

ThinkCMF < = 5.0.190111

#### 4.4.4 漏洞修复

目前厂商已发布升级补丁以修复漏洞，补丁获取链接：

<https://bst.cloudapps.cisco.com/bugsearch/bug/CSCvm13822>

#### 4.4.5 漏洞分析

0x0：首先我们可以控制数据库的写入:将payload插入数据库

0x1：间接的控制了$allRoutes变量

0x2：逃逸单引号，我们可以往data/conf/route.php中写入代码并再写入之后再次触发执行

首先我们在ThinkCMF（ThinkPHP）的路由解析入口打上断点，即在 `$data = self::exec($dispatch,
$config);`处，然后往下走，

![](https://images.seebug.org/content/images/2020/12/c0c90d6e-6d46-49c8-9c45-83a65a4be56e.png-w331s)

通过路由解析，解析出了请求的控制器、类、以及对应函数，分别为:`RouteController.php`的`addPost`函数。

![](https://images.seebug.org/content/images/2020/12/03/1606977157000-442.png-w331s)

在addpost()函数中，通过
`$routeModel->allowField(true)->save($data);`中的save函数存储路由到数据库中(`INSERT
INTO`cmf_route`(`full_url`,`url`,`status`) VALUES (‘portal/List/index’ ,
‘list/:id’ , ‘1’)`)。

![](https://images.seebug.org/content/images/2020/12/8e3dfb2f-1835-4617-bc3a-6646beeea7a1.png-w331s)

回到`RouteController.php::index()`函数中，该函数用于在请求/响应过程中遍历所有的存储路由。

![](https://images.seebug.org/content/images/2020/12/f5a4b344-2054-4fa8-be21-8c960d1080df.png-w331s)

在index()函数通过getRoutes()函数来进行的，进入到`$routeModel->getRoutes(true);`函数中，在该函数中，通过$allRoutes来存储从数据库中获取到的所有路由内容。

![](https://images.seebug.org/content/images/2020/12/1ce16d47-fec2-4be6-9bcf-11af007acb54.png-w331s)
最终在data/conf文件夹下生成`route.php`文件，可以看出是通过单引号逃逸在PHP文件中引入了在数据库中注入的恶意PHP代码。

![](https://images.seebug.org/content/images/2020/12/c194f21b-249f-4a04-a5da-998eabf80ff9.png-w331s)

![](https://images.seebug.org/content/images/2020/12/7e7b5883-f7ff-4bc5-996f-21060bbfb99c.png-w331s)

### 4.5 ThinkCMF 5.x后台 远程代码执行漏洞

#### 4.5.1 漏洞简介

漏洞名称：ThinkCMF 5.x后台 远程代码执行漏洞  
漏洞编号：CVE-2019-7580  
漏洞类型：代码注入  
CVSS评分：【CVSS v2.0：6.5】【CVSS v3.0：8.8】  
漏洞危害等级：高危

#### 4.5.2 漏洞概述

ThinkCMF是一套基于ThinkPHP的CMS（内容管理系统）。ThinkCMF
5.0.190111版本中存在安全漏洞。远程攻击者攻击者可通过向portal/admin_category/addpost.html页面发送'别名'参数利用该漏洞注入任意代码。

#### 4.5.3 漏洞影响

ThinkCMF < = 5.0.190111

#### 4.5.4 漏洞修复

目前厂商已发布升级补丁以修复漏洞，补丁获取链接：

<https://bst.cloudapps.cisco.com/bugsearch/bug/CSCvm13822>

#### 4.5.5 漏洞分析

0x0：首先我们可以控制数据库的写入:将payload插入数据库

0x1：间接的控制了$allRoutes变量

0x2：逃逸单引号，我们可以往data/conf/route.php中写入代码并再写入之后再次触发执行

首先我们在ThinkCMF（ThinkPHP）的路由解析入口打上断点，即在 `$data = self::exec($dispatch,
$config);`处，然后往下走，

![](https://images.seebug.org/content/images/2020/12/7ff017ae-1c4c-4885-a13a-ef00f25abf3d.png-w331s)

通过路由解析，解析出了请求的控制器、类、以及对应函数，分别为:`AdminCategoryController.php`的`addPost`函数。

![](https://images.seebug.org/content/images/2020/12/9faaa637-0d8f-4909-8df9-c6e01882cadd.png-w331s)
在`addPost`函数中通过`portalCategoryModel.php`中的`addCategory()`函数添加路由分类：

![](https://images.seebug.org/content/images/2020/12/88a19b72-030f-48c4-9f6a-4a899ff2337c.png-w331s)

继续跟进到`portalCategoryModel.php::addCategory()`函数中看出，通过`RouteModel.php::setRoute()`函数将`alias`的值进行存储。

![](https://images.seebug.org/content/images/2020/12/3f981df7-c3a0-4104-89c8-6294107c55bd.png-w331s)

在`RouteModel.php::setRoute()`函数中，首先确定该路由是否存在，若不存在，就直接将路由存储到数据库中。

![](https://images.seebug.org/content/images/2020/12/ff5c5d29-dd29-4f7f-b742-a185e81b2267.png-w331s)

数据库中已经保存了新增的url的内容，如下：

![](https://images.seebug.org/content/images/2020/12/ff1a0e08-2beb-4463-882c-44e820331a44.png-w331s)

回到`portalCategoryModel.php::addCategory()`函数中，在存储完新路由后，然后就进入到`$routeModel->getRoutes(true);`函数中，在改函数中，通过$allRoutes来存储所有的新增路由内容。

![](https://images.seebug.org/content/images/2020/12/a208a713-0d70-4752-a3f1-f55dfa447ea3.png-w331s)

最终在data/conf文件夹下生成`route.php`文件，该文件中包含了数据库中注入的恶意PHP代码。

![](https://images.seebug.org/content/images/2020/12/1f6bcbcd-1830-4102-b3cf-d346859d5a0c.png-w331s)

![](https://images.seebug.org/content/images/2020/12/7b0e7e66-1fcf-4b3b-b411-329a0f2eaf94.png-w331s)

### 4.6 ThinkCMF 2.x 代码注入漏洞(Api/Plugin)

#### 4.6.1 漏洞简介

漏洞名称：ThinkCMF 2.x 代码注入漏洞（Api/Plugin）  
漏洞编号：无  
漏洞类型：代码注入  
CVSS评分：无  
漏洞危害等级：高危

#### 4.6.2 漏洞概述

ThinkCMF是一套基于ThinkPHP的CMS（内容管理系统）。在 **ThinkCMFX 2.2.3**
最终版及以前版本中，存在一处模板注入漏洞。该漏洞源于程序未对模板文件名进行过滤，且接口权限控制不严。在模板名可控、文件内容可控的情况下，我们可以将
**webshell** 写入缓存文件，然后框架会去包含缓存文件，这样就成功执行了 **webshell** 。

#### 4.6.3 漏洞影响

1.6.0 <= ThinkCMFX <= 2.2.3

#### 4.6.4 漏洞修复

1.将 HomebaseController.class.php和AdminbaseController.class.php 类中 display 和
fetch 函数的修饰符改为 protected

2.目前厂商已不维护2.x版本，请受影响的用户使用升级到ThinkCMF 5系列或者采用以上临时解决方案

#### 4.6.5 漏洞分析

分析该漏洞，我们要详细跟踪一下content参数值的流向，我们从程序入口开始往后跟踪：

Step1：首先通过ThinkPHP.php入口文件进入到Think.class.php文件中的`start()`函数；

![](https://images.seebug.org/content/images/2020/12/6790589e-5a75-42c6-a619-cad50c6ba7c8.png-w331s)

在start()函数中，进入到App.class.php文件中的主函数`run()`;

![](https://images.seebug.org/content/images/2020/12/ff07bc7c-0c8d-48be-9fd9-ce8b486a2666.png-w331s)

进入到文件中的exec()函数，exec函数的作用就是解析请求的路由，这一块的处理模式即为ThinkPHP的处理模式；

![](https://images.seebug.org/content/images/2020/12/fe35d348-b522-4bbc-8773-97ef73b1910f.png-w331s)

![](https://images.seebug.org/content/images/2020/12/00b6a70b-7c40-439b-b6e9-b787a84ce9fa.png-w331s)

通过路由解析，解析出了请求的module、action，分别为:`view`的`fetch`。然后通过invokeAction()函数中的反射，定位到具体类以及具体的操作函数。以下即为第一阶段的路由解析阶段的调用链。

![](https://images.seebug.org/content/images/2020/12/89ea2e9b-97ef-4580-8256-7f979f3681a1.png-w331s)

Step2：在定位了操作函数之后，首先定位到了HomebaseController.php文件中的fetch()函数；

![](https://images.seebug.org/content/images/2020/12/5438a922-771b-43b2-9022-f04c32fc1c7d.png-w331s)

然后通过`return parent::fetch`返回到其父类的Controller.php文件中的fetch()函数；

![](https://images.seebug.org/content/images/2020/12/d96a9b2a-756e-4b09-aeb9-627d256ba8e2.png-w331s)

根据之前的路由解析，我们知道即将调用View然后即进入到View.class.php文件中的fetch()函数，进行模板处理。

![](https://images.seebug.org/content/images/2020/12/5481e236-8a93-462b-a6dd-3b8887149f5b.png-w331s)

我们可以看到该函数中，再起始有一个`ob_start();`，然后对content进行处理后，通过`$content =
ob_get_clean();`将content清空，所以我们在清空之后下断点，然后我们即进入到view_parase模块，通过跟踪，我们解析出了模块对应的是ParseTemplateBehavior.php文件；

![](https://images.seebug.org/content/images/2020/12/c08523a4-4fff-4763-a3f8-7ab17530086e.png-w331s)

进入到`ParseTemplateBehavior::run()`主函数中，我们将面临着两个分支，我们分别在两个分支打上断点，来验证此处程序的走向。我们发现content的值是第一次发送的话，将会走else分支，如果不是第一次发送，将会走第一个分支，从判断条件也可得知，如果缓存中存在content的缓存，即走if分支，否则就走else分支。

![](https://images.seebug.org/content/images/2020/12/f23df41d-f768-454a-bfff-832879a2bab6.png-w331s)

我们利用第一次发送的poc，进入到else分支中的fetch函数，我们发现进入到Template.class.php文件中的fetch函数，

![](https://images.seebug.org/content/images/2020/12/0ca4f716-d596-4e5e-a682-1523436255c3.png-w331s)

我们可以看到fetch函数中调用了`loadTemplate()`函数，进入到该函数中，我们可以看到content最终被赋值到了
`$tmplContent`参数中；

![](https://images.seebug.org/content/images/2020/12/51ebc712-cd37-460f-af70-9a734a0be35f.png-w331s)

然后`$tmplContent
(content)`经过编译后通过`Storage::put`函数保存，最终将文件生成到data/runtime/Cache/Portal文件夹中。最后，最后在Template.class.php文件中调用了`Storage::load`加载cache文件，最终导致代码执行。

![](https://images.seebug.org/content/images/2020/12/ed68f4cd-a9e6-4768-b324-2f37d5c7932d.png-w331s)

## 五、漏洞利用

最后，通过深信服千里目实验室 **漏洞利用工具Sniper** 进行最后的漏洞利用，具体操作如以下视频所示：

### 5.1 ThinkCMF 2.x 代码注入漏洞（fetch）

相关视频，请转到原文观看，链接：<https://mp.weixin.qq.com/s/9IWS0VX90CUJzhh8i0myAw>

### 5.2 ThinkCMF 2.x 代码注入漏洞（display）

相关视频，请转到原文观看，链接：<https://mp.weixin.qq.com/s/9IWS0VX90CUJzhh8i0myAw>

### 5.3 ThinkCMF 2.x 前台任意文件上传漏洞

相关视频，请转到原文观看，链接：<https://mp.weixin.qq.com/s/9IWS0VX90CUJzhh8i0myAw>

### 5.4 ThinkCMF 5.x 后台远程代码执行漏洞

相关视频，请转到原文观看，链接：<https://mp.weixin.qq.com/s/9IWS0VX90CUJzhh8i0myAw>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1419/>

