GDidees CMS是法国一款开源的网站管理工具，可用于创建站点、照片或视频库。GDidees CMS
3.9.1及以下版本存在任意文件上传漏洞，允许未经授权的攻击者上传精心构造的文件并执行任意代码。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 未知  
  
## Part2 漏洞描述

‍漏洞名称|

GDidees CMS任意文件上传漏洞  
  
---|---  
CVE编号| CVE-2023-27178  
漏洞类型|  任意文件上传  
漏洞等级| 高危(9.8)  
公开状态| 公开  
漏洞描述|

GDidees CMS 3.9.1及更低版本存在任意文件上传漏洞，允许未经授权的攻击者上传精心构造的文件并执行任意代码。  
  
时间线|

2023-4-10 NVD发布  
  
影响产品|

GDidees CMS 3.9.1及以下版本  
  
## Part3 漏洞复现  

###  **1\. 复现环境**

系统版本：Kali 2023.1

软件版本：GDidees CMS 3.9.1

 **2\. 复现步骤**

创建文件格式为phar的一句话木马文件

![图片](https://image.3001.net/images/20230518/1684395226_6465d4dac4f03b5ce801f.jpg!small)

访问Roxy Fileman插件页面

![图片](https://image.3001.net/images/20230518/1684395235_6465d4e38fd4b08ab50c4.jpg!small)

上传cmd.phar文件

![图片](https://image.3001.net/images/20230518/1684395245_6465d4edc252dabcd50a5.jpg!small)

携带参数cmd=echo ‘csx lab’;访问cmd.phar页面，可以看到php代码成功执行。

![图片](https://image.3001.net/images/20230518/1684395256_6465d4f8e51fb06ec8dbf.jpg!small)

## Part4 漏洞分析

### Roxy Fileman插件的index页面没有身份验证功能，因此允许用户直接访问该页面。

![图片](https://image.3001.net/images/20230518/1684395277_6465d50d155ec7721301b.jpg!small)

查看Roxy Fileman的conf.json文件，可以发现FORBIDDEN_UPLOADS字段未限制phar格式。

![图片](https://image.3001.net/images/20230518/1684395285_6465d515ceb1cd1ccef86.jpg!small)

查看apache2的配置文件，可以发现默认情况下扩展名为php、phar和phtml的文件都被当作php文件解析。因此在当前环境下，上传的phar文件将作为php文件进行解析，从而执行任意代码。

![图片](https://image.3001.net/images/20230518/1684395297_6465d521329cf578812b8.jpg!small)

## Part5 修复建议

修改conf.json文件中的FORBIDDEN_UPLOADS字段，禁止上传phar格式的文件。

