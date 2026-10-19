**作者：李安@星阑科技PotalLab  
原文链接：<https://mp.weixin.qq.com/s/bbfFFczkycYCpRK0b7HeHg>**

## **漏洞描述**

攻击者可以向batch-requests插件发送请求来绕过管理API的IP限制。Apache
APISIX的默认配置(带有默认的API密钥)容易受到远程代码执行的攻击。当管理密钥更改或管理API端口更改为与数据面板不同的端口时，影响较小。但是，绕过Apache
APISIX数据面板的IP限制仍然存在风险。在batch-requests插件中有一个检查，它用真实的远程IP覆盖客户端IP。但是由于代码中的一个bug，这个检查可以被绕过。

#### **batch-requests 插件介绍**

batch-requests 插件可以一次接受多个请求并以 http pipeline
（<https://en.wikipedia.org/wiki/HTTP_pipelining>） 的方式在网关发起多个 http
请求，合并结果后再返回客户端，这在客户端需要访问多个接口时可以显著地提升请求性能。

在漏洞版本中、默认是启用状态。

<https://apisix.apache.org/zh/docs/apisix/2.12/plugins/batch-requests/>

#### **复现思路：**

1、搭建漏洞环境。(注意需要修改:conf.yaml/allow_admin)

2、查看diff记录、进行简单调试，漏洞分析。

3、漏洞测试。

## **漏洞版本**

Apache APISIX 1.3 ~ 2.12.1 之间的所有版本（不包含 2.12.1 ）

Apache APISIX 2.10.0 ~ 2.10.4 LTS 之间的所有版本（不包含 2.10.4）

## **环境搭建**

搭建方式 | Docker 搭建 |  |  
---|---|---|---  
| 版本号 | 默认端口 | 默认admin_key/用户  
Apache APISIX | apisix:2.12.0-alpine | 9080 | edd1c9f034335f136f87ad84b625c8f1  
Apache APISIX Dashboard | apisix-dashboard:2.10.1-alpine | 9000 | admin/admin  
  
环境搭建可以使用下面这个Github地址：

Github 地址 <https://github.com/twseptian/cve-2022-24112/tree/main/apisix-docker>

cd CVE-2022-24112-main/apisix-docker/example/

vi apisix_conf/config.yaml

**将 allow_admin 修改为 127.0.0.0/24，此处修改的实际为nginx.conf。**

使用 docker-compose 创建docker容器。

docker-compose -p apisixCveTest up -d

在服务启动阶段、会读取config.yaml、生成nginx.conf 。

**1、会基于 Lua 模板 apisix/cli/ngx_tpl.lua 文件生成
nginx.conf。(APISIX架构介绍：<https://blog.csdn.net/alex_yangchuansheng/article/details/122053371>)**

**2、调用 ngx_http_access_module 模块。该模块限制客户端对某些地址的访问。(nginx
模块介绍：<http://nginx.org/en/docs/http/ngx_http_access_module.html#allow>)**

![](https://images.seebug.org/content/images/2022/10/495119fe-1a68-43ff-b7c3-19e237f19d76.jpeg-w331s)

进入到容器中查看，conf/nginx.conf。allow/deny 是设置允许与拒绝访问的地址。只允许127.0.0.1/24 访问
/apisix/admin 接口。

![](https://images.seebug.org/content/images/2022/10/686b3a65-bccb-4ee2-a853-bd1835a43ca3.jpeg-w331s)

Admin api 接口如下：

![](https://images.seebug.org/content/images/2022/10/287f95a9-66d8-4d1b-a346-1258a95a571b.png-w331s)

![](https://images.seebug.org/content/images/2022/10/4ae3b43f-152c-4953-87c3-7dffaff35f9b.jpeg-w331s)

#### **漏洞分析**

**diff ：**

1.<https://github.com/apache/apisix/pull/6254/commits/f5d44d1f58e0160132f009465e807f4093601a11>

2.<https://github.com/apache/apisix/pull/6251/commits/8f28aadc35362f417f89db505c18cd7f1d548c86>

3.<https://github.com/apache/apisix/pull/6204/commits/3d4b35b8e07f2c7cfcce7d7f56f24fad4e6e39de>

![](https://images.seebug.org/content/images/2022/10/98b430c4-41d0-43c3-b7a8-a4067ea02da5.jpeg-w331s)

查看diff记录后、修复方式是将real_ip_hdr 转化为小写。

1、查看插件batch-requests 代码，问题是出现在 set_common_header() 函数中

![](https://images.seebug.org/content/images/2022/10/12a68f65-821c-4f39-b235-4b6493ca8de6.jpeg-w331s)

函数参数为data是我们传入的请求体经过json.decode()后的数据、类型为"table"。

![](https://images.seebug.org/content/images/2022/10/e6f51eca-5b3c-420d-af27-1e0035416031.jpeg-w331s)

查看代码,real_ip_hdr 为调用 try_read_attr()函数获取到的返回值。通过遍历表结构、获取到 real_ip_header
的值然后再赋值给real_ip_hdr 。

select('#', ...) 获取输入参数的数量，

select(i, ...) 获取第 n 个参数，

![](https://images.seebug.org/content/images/2022/10/de37d3cf-5314-4a34-b606-42a8b1585a66.jpeg-w331s)

![](https://images.seebug.org/content/images/2022/10/04e5b3fe-f71e-4309-aa0c-f8ed42aaac83.jpeg-w331s)

注意：此时的real_ip_hdr 为 X-Real-IP 为大写。该值为在系统启动后、给定的默认值。

![](https://images.seebug.org/content/images/2022/10/940e0ab3-1827-480c-9f07-2682fb1a1333.jpeg-w331s)

2、通过遍历data.pipeline和data.headers 、将data.headers
出现的头信息赋值给data.pipline。发现data.headers中出现了x-real-ip:127.0.0.1 ，这是我们调用batch-requests插件传递的头信息，而此时系统默认的X-Real-IP为大写。

![](https://images.seebug.org/content/images/2022/10/6cf8b6c8-e2cc-471e-be56-fba34b4fc419.jpeg-w331s)

在请求头覆盖中、因为 real_ip_hdr 为 X-Real-IP ,
函数core.request.get_remote_clinte_ip()获取远程客户端ip、不能将 x-real-ip给覆盖。

![](https://images.seebug.org/content/images/2022/10/982bb5a1-815a-4e34-ad55-92b35bd909c2.jpeg-w331s)

查看此时的栈数据。在data.headers 中出现了 x-real-ip 与 X-Real-IP。

![](https://images.seebug.org/content/images/2022/10/b4875ce7-d1f2-44ea-bb5d-252c278f27f1.jpeg-w331s)

最后经由batch-requests 插件、使用PUT方法将请求发送到 /apisix/admin/xxxx 注册新的路由。通过filter_func
参数可写入一段lua代码、造成远程代码执行。

![](https://images.seebug.org/content/images/2022/10/ba3fecc9-0f1d-4cbb-977d-c0f46d529825.jpeg-w331s)

#### **漏洞测试**

![](https://images.seebug.org/content/images/2022/10/e370da98-b15c-45ad-87e6-40758cbd498c.jpeg-w331s)

#### **利用条件**

  * batch-requests插件默认开启状态。
  * 用户使用了 Apache APISIX 默认配置（启用 Admin API ，使用默认 Admin Key 且没有额外分配管理端口），攻击者可以通过 batch-requests 插件调用 Admin API 。

#### **攻击思路**

1、利用batch-requests 插件漏洞、绕过请求头检测；

2、通过伪造请求头、向Admin API 注册路由；

3、注册路由时、携带参数filter_func 传递 lua代码、造成远程代码执行漏洞。

## **修复意见**

1、更新至最新版本  
2、禁用batch-requests 插件

## **参考材料**

**APISIX官网：**<https://apisix.apache.org/docs/apisix/2.12/getting-started/>

**APISIX Github：**<https://github.com/apache/apisix>

**漏洞环境：**<https://github.com/twseptian/cve-2022-24112>

**APISIX架构分析：**<https://blog.csdn.net/alex_yangchuansheng/article/details/122053371>

**漏洞发现：**<https://www.youtube.com/watch?v=yrCXamnX9No>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1984/>

