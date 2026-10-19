# 如何利⽤Quake挖掘某授权⼚商边缘站点漏洞

阅读量 **230798**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-02 15:00:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0146fe1d9251bbf8bc.jpg)

## 0x00 360Quake牛刀小试

在对某厂商进行授权安全测试时，苦于寻找资产，于是决定利用网络空间测绘系统来看看有没有奇效。  
刚好近期看到360发布了Quake空间测绘系统（quake.360.cn），试用了下感觉还不错。  
于是想通过Quake中的title语法来简单的搜索边缘资产。

![](https://imgkr2.cn-bj.ufileos.com/9b835ade-700c-4b92-898a-eadfc946723e.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=o1KjbB7fHB3xBxzva643llkr64A%253D&Expires=1606876296)

搜到疑似该厂商的一个边缘站点。根据经验，像这种界面的系统一般多多少少都有漏洞。

![](https://imgkr2.cn-bj.ufileos.com/65a0ff4d-3209-4d9d-916e-91d195818929.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=dsRZ%252FiBnH3E%252Fldl6l1LefjJ%252Bq6E%253D&Expires=1606876094)

因为站点只有一个后台界面，所以我们的漏洞利用点一般先是寻找爆破弱口令账户，或者是找到一处全局越权。最好是弱口令账户。经过一些列的账户爆破处理，并没有一个有效用户可利用。于是乎只能寄托于能不能搞到这套系统的相似源码或者框架。

这时候，我注意到之前quake搜索出来的结果。在360quake当中，对存在ico的站点会在搜索栏下告知站点ico的md5值。根据favicon的图标，我猜测这不是一套原生框架。

![](https://imgkr2.cn-bj.ufileos.com/45899428-8000-4a6c-92a4-82222f9ad3d2.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=nuBbb2drw44K%252BBQL2XEzVCo%252F7%252Bc%253D&Expires=1606876567)

删除对应的title关键词，可以根据favicon来搜索使用同套相似框架的站点。

当然假如quake没有给出这个站点的icon值，你也可以根据 `curl
http://xxxx.com/favicon.ico|md5sum`的方式，得到站点ico的md5，然后利用quake语法，`favicon:"{MD5}"`搜索。

运气较好，在quake的第一页就发现了和厂商使用同样cms，并且明示用了什么框架的站点：jeecg-boot。

![](https://imgkr2.cn-bj.ufileos.com/15290e8b-81f2-4fa9-b057-096be98079ad.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=NQlllaKRtHD9lurd6ZFx1dLXD9U%253D&Expires=1606877018)

## 0x01 如何利用360quake搜索相似站点，并获得源码

这里一般我们搜索相似源码的站点有以下几种方式：

  * 1、`根据favicon搜索`
  * 2、`根据首页页面里的一些特征，利用body:"{特征}"来搜索`
  * 3、`根据response里的header头特征来搜索，一般是在cookie里有设置特定的cookie。比如shiro的rememberMe=xxx，或者apache的ofbiz。`
  * 4、`根据cert里Issuer、Subject特征搜索，一些单位、甚至部门信息会包含在ssl证书内容之中。`

搜索到相似站点后，有几种方式搞到源码：

  * 1、`对相似站点进行入侵，getshell后获得源码（动静较大）`
  * 2、`对相似站点批量扫备份文件`
  * 3、`得知cms的名称去凌风云网盘搜索该cms源码是否有人分享`
  * 4、`闲鱼搜有没有对应源码有人在买卖`
  * 5、`去github，gitee搜有没有相似的源码，是否是根据别人的源码二次开发的成品`

## 0x02 步入正题，如何搞定这个cms。

这里我们搜索到jeecg-boot是github上开源的成熟项目，项目成熟，不代表没有漏洞。成熟项目有成熟项目的好，就是有人会去发现漏洞，然后告知到github的issue上，你只要祈祷你遇到的站点不是最新版本就行。项目不成熟，只能你自己审计代码，好处就是用的人少，相对有漏洞的概率就大。

根据 <https://github.com/zhangdaiscott/jeecg-boot> 项⽬可知，该项⽬是由java基于
springboot开发的。所以我第⼀时间阅读了这个项⽬的README。

![](https://imgkr2.cn-bj.ufileos.com/2962fdb6-1c5d-499a-977f-d3235e9f4856.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=w%252FIs84AZaknjpL%252FObXYAQmdTTec%253D&Expires=1606877690)

舒服，有fastjson和shiro，还有我熟悉的springboot的。

首先，登录抓个包。

![](https://imgkr2.cn-bj.ufileos.com/4ff8138b-1de0-437b-8bfb-26b76bf05225.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=r5xgFg8ErpeIN3e4jq%252BdABi4e5w%253D&Expires=1606877853)

符合站点描述缩写的，确实是可能使用了fastjson，整个response和request里的url都有springboot的气息。

因为知道有shiro，但是shiro版本⼤于是1.4.0。所以有那个paddingoracle的漏洞，也有⼏个  
shiro配合springboot的url绕过漏洞。整理下⼏个漏洞的利⽤条件。

paddingoracle的漏洞利⽤条件：

  * 1、需要登录后的rememberMe的值，也就是说需要账号密码。

shiro的url验证绕过：

  * 1、不需要利⽤条件，但是前提是作者那样⼦配置认证⽅式，其次就是  
你有对应的后台漏洞的url。

第⼀个paddingoracle暂时利⽤不了，只能从第⼆个shiro绕过找办法。

因为是1.4.0所以那个  
反序列化还是存在的。因为只是key随机化了⽽已，查看项⽬，并没有设置固定的key，所以  
⽤⼯具没跑出来key。  
于是乎，根据前面提到的，我们在issue上找到⼀个最近的sql注⼊漏洞。 `https://github.com/  
zhangdaiscott/jeecg-boot/issues/1887`

![](https://imgkr2.cn-bj.ufileos.com/64ea6ae1-4645-4577-b941-ed142a7c8003.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=zpCq3iW04Uz15wUPlWd3FplDCbs%253D&Expires=1606878119)

先看看这个url在未登陆下是啥情况。

![](https://imgkr2.cn-bj.ufileos.com/df45d552-d137-4a38-b8c4-c57961eda1f5.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=fh%252F%252FLRyl4aoK%252F1GZRyYZQl3%252FMAA%253D&Expires=1606878160)

提示重新失效。然后根据shiro的最近⼏个未授权漏洞进⾏fuzz。当发现下图情况时候，返回码不  
⼀样了。说明已经绕过了shiro认证。

![](https://imgkr2.cn-bj.ufileos.com/79fd8392-1f30-426d-95ef-843c9bf15110.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=uto797sTQfzlNfmBdLExwPAVfKE%253D&Expires=1606878187)

根据issues⾥的图⽚请求，进⾏填写剩余的get参数。成功获取到数据。

![](https://imgkr2.cn-bj.ufileos.com/b35c2a21-4f96-40aa-b08a-07a01d926b42.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=N%252FzLVOgDDY1XsSoDT%252FsFZO2xeeI%253D&Expires=1606878233)

注⼊点在code=处。mysql数据库。

![](https://imgkr2.cn-bj.ufileos.com/9c11b290-be60-4fab-9848-1371c0e0c9ea.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=xP1U%252BeZ2WHTAItzk7IG3zF1QLLM%253D&Expires=1606878253)

注入点很明显，直接可以用sqlmap。 —is-dba

![](https://imgkr2.cn-bj.ufileos.com/e7c4fa0d-2a2e-4603-b384-cb30e34e4960.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=rA9RkW2%252BJCu0gfvybx6mRbKNLBM%253D&Expires=1606878282)

然后下载源代码，看看有没有upload的漏洞。找到⼀处新版被注释掉的上传代码（大概率可能有洞才被在新版注释掉）。

    
    
    //    @PostMapping(value = "/upload2")
    //    public Result<?> upload2(HttpServletRequest request, HttpServletResponse response) {
    //        Result<?> result = new Result<>();
    //        try {
    //            String ctxPath = uploadpath;
    //            String fileName = null;
    //            String bizPath = "files";
    //            String tempBizPath = request.getParameter("biz");
    //            if(oConvertUtils.isNotEmpty(tempBizPath)){
    //                bizPath = tempBizPath;
    //            }
    //            String nowday = new SimpleDateFormat("yyyyMMdd").format(new Date());
    //            File file = new File(ctxPath + File.separator + bizPath + File.separator + nowday);
    //            if (!file.exists()) {
    //                file.mkdirs();// 创建文件根目录
    //            }
    //            MultipartHttpServletRequest multipartRequest = (MultipartHttpServletRequest) request;
    //            MultipartFile mf = multipartRequest.getFile("file");// 获取上传文件对象
    //            String orgName = mf.getOriginalFilename();// 获取文件名
    //            fileName = orgName.substring(0, orgName.lastIndexOf(".")) + "_" + System.currentTimeMillis() + orgName.substring(orgName.indexOf("."));
    //            String savePath = file.getPath() + File.separator + fileName;
    //            File savefile = new File(savePath);
    //            FileCopyUtils.copy(mf.getBytes(), savefile);
    //            String dbpath = bizPath + File.separator + nowday + File.separator + fileName;
    //            if (dbpath.contains("\\")) {
    //                dbpath = dbpath.replace("\\", "/");
    //            }
    //            result.setMessage(dbpath);
    //            result.setSuccess(true);
    //        } catch (IOException e) {
    //            result.setSuccess(false);
    //            result.setMessage(e.getMessage());
    //            log.error(e.getMessage(), e);
    //        }
    //        return result;
    //    }
    

构造请求包：

![](https://imgkr2.cn-bj.ufileos.com/172de189-6da9-4141-af68-74d71f725a3a.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=Np0C9zoAFHGWwQbP5FVUkHUnXX0%253D&Expires=1606878323)

根据代码，看下上传到哪⾥去了。

![](https://imgkr2.cn-bj.ufileos.com/5b905889-cbd7-4e46-a0d2-e1be4ad97121.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=ItzfzmXyoWQ%252BJSRRFzOckg746bs%253D&Expires=1606878343)

${jeecg.path.upload}

![](https://imgkr2.cn-bj.ufileos.com/409b8e85-2211-4e5a-b20e-93d6a4d7e8c8.png?UCloudPublicKey=TOKEN_8d8b72be-579a-4e83-bfd0-5f6ce1546f13&Signature=huuETKf3Bv1PMjZdXcXCfTga7Ow%253D&Expires=1606878363)

可惜，这个站点的biz不可控，文件只能上传到和webapp同⽬录下的upload⽬录，那在web的URL下是访问不到我们的上传文件。如果是上传到webapp下⾯，那就可以访问到。

## 0x03 后续渗透思路

  * 1、利用注入点，新增or修改后台某个账户为弱口令。
  * 2、利用弱口令账户登入系统，获取到rememberMe的正确值，使用shiro的paddingoracle的JRMP的gadget进行攻击。
  * 3、看了下项目，作者提供了便捷的docker方案。So后续渗透getshell后有大概率是在docker里。

## 0x04 总结

  * 1、在日益艰难的web项目渗透下，利用现有的资产搜索引擎可以更好的帮我们掌握目标站点的情报。
  * 2、现在的入侵都不是一步水到渠成，往往需要迂回而上，越了解目标的环境，越有机会拿下目标站点。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ph4nt0mer** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224420](/post/id/224420)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Quake](/tag/Quake)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0194446028f682cffe.jpg) ph4nt0mer

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

