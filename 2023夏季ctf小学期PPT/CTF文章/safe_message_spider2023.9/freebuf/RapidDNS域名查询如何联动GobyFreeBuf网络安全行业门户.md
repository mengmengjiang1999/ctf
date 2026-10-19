![](https://image.3001.net/images/20201109/1604910007_5fa8fbb729163bcc6db0d.jpg!small)

RapidDNS.io
是一个秒级在线子域名和同IP域名的查询工具。目前拥有25亿条DNS记录，支持A、AAAA、CNAME、MX4种DNS记录类型。由于Goby程序对子域名收集方面不是很完善，这里特编写此插件作为其拓展。可以方便快速获取域名和ip地址信息进行侦察，提升探测效率。

## 0x001 插件使用

输入要查询的根域名，点击搜索按钮，稍等片刻即可查看所有查询结果。可以根据情况选择导入域名，IP或者两者都导入。

    
    
    注：由于有些域名数量较多，等待时间也可能会久一些，请耐心等待。如果长时间没有结果，可以关闭查询gobies.org这类数量少的域名确认是否可以正常使用。

![](https://image.3001.net/images/20201109/1604910103_5fa8fc174ae01773ffcb3.png!small)

## 0x002 插件开发

插件开发很简单，只需要获取网页查询结果表格显示即可。可以借鉴已有样式，比如FOFA插件。

1\. 首先，直接拷贝FOFA插件并重命名为RapidDNS。  
2\. 更改`package.json`文件中属性信息。修改`README.md`和`CHANGELOG.md`  
3\. 更改相关文件名为和内容为rapiddns，即替换fofa即可。  
4\. 修改`src/extension.js`文件中指向的文件为`rapiddns.html`。  
5\. 修改请求的url，替换为
`https://rapiddns.io/subdomain/${content}?full=1`。根据返回的内容，提取查询结果的表格内容。这里可以使用正则`<thead>(.+?)<\/tbody>`提取，使用多行和全局模式即可。对提取到的内容直接append到插件窗口中。这里要修改下页面中id为`ip-table`文的表格，要删除掉多余内容，只保留`<table lay-filter="demo" id="ip-table" class="layui-table"></table>`就可以。  
6\. 删除掉export按钮，增加3个按钮，分别为export ip, export subdomain, export all。并修改对应的id。  
7\. 因为页面中使用了Jquery库，直接通过遍历表格的方法就可以将内容导出目标。`$("#ip-table
tr").each`，循环遍历，并根据其DNS类型是否导入ip或者子域名。获取表格列值的代码是`currentRow.find("td:eq(2)").text()`。  
具体可以看如下示例代码，其他同理：

    
    
    $(".export-ip").on("click", function() {
    
            let ips = [];
            $("#ip-table tr").each(function(){
              var currentRow=$(this);
              var type =currentRow.find("td:eq(2)").text();
              if(type=="A"){
                var ip=currentRow.find("td:eq(1)").text();
                if(ip !=""){
                  ips.push(ip);
                }
              }
            })
    
            goby.addScanIps(ips, 1);
            goby.showSuccessMessage("Export completed!");
            goby.closeIframeDia();
        })

  
8\. 清理无用的文件和加载的代码，完成开发。

## 0x003 小结

由于Goby暂时不支持IPv6扫描，不会导入IPv6地址。后续Goby支持IPv6扫描后再添加IPv6地址（RapidDNS网站本身支持IPv6）。开发过程中发现问题：1.
无法识别Readme文档中的项目符号。2. 扫描框高度只能显示两个目标太少。3. 窗口不能拖动也挺难受的。不过这些问题都不大。

在不了解太多信息以及缺乏相关基础知识的情况下，通过已有的插件，可以快速的实现插件编写，达到自己的需求和目的。通过拓展，也可以提升在渗透过程中的效率。

Happy Hacking！！！

如果表哥/表姐也想把自己上交给Goby社区，戳这里领取一份插件任务？

    
    
    https://github.com/gobysec/GobyExtension/projects

