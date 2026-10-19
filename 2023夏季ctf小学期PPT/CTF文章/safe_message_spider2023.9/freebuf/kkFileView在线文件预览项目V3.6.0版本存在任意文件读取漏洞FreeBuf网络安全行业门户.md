这段时间因为主导开发单位里的网络安全运营管理平台，用脑比较多，头发又掉了不少，在项目中使用到了kkFileView来实现在线文件预览的功能，一个偶然的操作，发现这个kkFileView的部署文件里是存在一个demo页面的，能够将文件上传到服务器上，同时支持文件预览功能，职业习惯原因隐约觉得这里有可能存在安全漏洞。

由于项目开发工作繁忙，也没有专门花时间去挖这个漏洞，直到4月15日国家安全日当天在参加中国电子技术标准研究院组织的关键信息基础设施保护贯标活动，在访问某个公共服务平台的时候发现也是用了kkFileView作为在线文件预览的工具，这才决定挖一挖这个kkFileView的漏洞。

##  **1、访问预览的demo页面，找一找有用的信息**

![图片](https://image.3001.net/images/20220429/1651209641_626b75a9718a81ebbcd17.png!small)

可以发现某公共服务平台使用的是v3.6.0版本的kkFileView，在开源代码仓库里找V3.6.0的源代码,看到对urlPath参数没有进行过滤，意味着可以通过构造各种协议的地址作为参数传递给服务端。

    
    
    /**
         * 根据url获取文件内容
         * 当pdfjs读取存在跨域问题的文件时将通过此接口读取
         *
         * @param urlPath  url
         * @param response response
         */
        @RequestMapping(value = "/getCorsFile", method = RequestMethod.GET)
        public void getCorsFile(String urlPath, HttpServletResponse response) {
            logger.info("下载跨域pdf文件url：{}", urlPath);
            try {
                URL url = WebUtils.normalizedURL(urlPath);
                byte[] bytes = NetUtil.downloadBytes(url.toString());
                IOUtils.write(bytes, response.getOutputStream());
            } catch (IOException | GalimatiasParseException e) {
                logger.error("下载跨域pdf文件异常，url：{}", urlPath, e);
            }
        }

比如预览百度的首页效果如下：

![图片](https://image.3001.net/images/20220429/1651209652_626b75b49d0b01652d604.png!small)

##  **2、漏** **洞验证**  
  

同样将协议换成file://,就可以读取到服务器上的任意文件：

![图片](https://image.3001.net/images/20220429/1651209664_626b75c069d8b823939b0.png!small)

上述漏洞信息提交到了国家信息安全漏洞共享平台，目前漏洞已经处置完毕，漏洞危害级别为中。

![图片](https://image.3001.net/images/20220429/1651209674_626b75ca69f051729a5a1.png!small)

CNVD-ID| CNVD-2022-29894  
---|---  
公开日期| 2032-04-15  
危害级别| 中  
  
##  **3、延伸**

虽然上面报送的是任意文件读取漏洞，实际上通过这个漏洞还可以实施针对于该服务器所在内网网端的主机的攻击，能够完成SSRF攻击，对内网的主机也构成严重威胁。

这个漏洞并不限于V3.6.0版本。

另外目前kkFileView也被使用的很广泛，利用这个漏洞可以批量的挖洞。

在开头提及到的网络安全运营管理平台开发中已经对这个漏洞进行了修复。

 **参考链接：**

> https://mp.weixin.qq.com/s/DbShQLWLgG0dv-vb2YepSw

