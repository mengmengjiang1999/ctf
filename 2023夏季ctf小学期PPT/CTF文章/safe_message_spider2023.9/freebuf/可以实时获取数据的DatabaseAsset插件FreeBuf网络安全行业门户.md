![](https://image.3001.net/images/20201126/1606362117_5fbf24053a9e7cfc18f48.jpg!small)

**前言：**
Goby之前开放的插件入口点较少，大家只能在扫描前、扫描后执行事件，无法参与扫描过程中来。为实现更多场景的应用及提高扫描效率（如：后台爆破子域名等），Goby开放了一些新的API：事件通知机制、自定义页面等，并开发了一个统计数据库信息的插件——Database
Asset，作为案例。该插件可以统计扫描任务中获取到的数据并进行筛选，筛选出用户需要显示的数据库信息。

## 0x001 插件效果

安装完成插件后，Goby左侧导航栏会出现我们的插件入口，开始扫描后，插件会统计扫描到的数据库信息，插件默认统计mysql，redis，MongoDB，Elasticsearch这四个数据库。扫描过程中会将统计的数据库数量展现在左侧导航栏插件入口标记处。

> 插件开发文档 <https://gobies.org/docs.html>

![](https://image.3001.net/images/20201126/1606362394_5fbf251a4f982619a6f07.gif!small)

## 0x002 插件开发

###  **2.1 确定功能的入口点及用到的API**

 **入口点** ：左侧导航 **自定义页面并可以后台运行的API** ：showPage(url,true)

    
    
    function activate(content) {
        goby.registerCommand('left-nav',function(){
             //因为支持相对路径,所以传入相对路径,第二个参数为后台运行
            goby.showPage('./assets/index.html',true); 
        })
    }
    exports.activate = activate;

需要实时获取扫描过程中的数据以及扫描状态改变时执行一些自定义事件：bindEvent;

扫描到符合条件的数据是需要通知用户：changeBadge;

点击查看信息页面跳转：showPage(url,false);

###  **2.2 开发流程**

 **2.2.1 package.json中设置入口点以及initEvents**

    
    
    "views": {
          "leftNav": [
            {
              "command":"left-nav",
              "title": "Database",
              "icon": "src/assets/img/logo.png"
            }
          ]
        }
    
    
    "initEvents": ["left-nav"]

> 注：新版本支持String 与 Array，如果要执行多个命令，只需将命令依次放到数组里，Goby会在安装插件成功后，主动执行指定命令:
    
    
    "initEvents": ["event1", "event2"]

 **2.2.2 html页面初始化**

首先声明我们需要统计的数据库信息、消息通知的内容、整合后的数据对象、任务id：

    
    
    let app = ["mysql" ,"redis", "MongoDB", "Elasticsearch"];  
    //消息通知
      let num = 0;
      //保存数据
      let data = {};
      //任务Id
      let taskId;

 **2.2.3 绑定事件通知及设置Badge**

实时获取数据，对扫描数据进行处理。因为太多，这里只展示对onApp数据的处理，数据的详细信息在官网中有说明。

    
    
    goby.bindEvent('onApp',function(content){
        init();
        let ip = content.hostinfo.match(ipreg)[0];
        let port = content.hostinfo.split(':').pop();
        initIp(ip);
        initPort(ip,port,content);
        if(app.map((v,k)=>v.toLowerCase()).includes(content.product.toLowerCase())){
          num++;
          goby.changeBadge('leftNav','left-nav',num);
          let tbody = $(`#${taskId}`)[0];
          if(!tbody){
            let ttbody = $(`<tbody id="${taskId}" class="${taskId}">
                <tr class="task">
                  <td colspan="3">任务 : ${taskId}</td>  
                </tr>
              </tbody>`);
            $('table').append(ttbody);
          }
          if($('.noData').css('display')!='none'){
            $('.noData').hide();
          }
          if($('table').css('display')=='none'){
            $('table').css('display','table')
          }
          let tr = $(`<tr class="info">
              <td>${content.product}</td>
              <td>${ip}</td>
              <td>${port}</td>
            </tr>`);
          $(tr).prop('ip',ip);
          $(tr).prop('port',port);
          $(tr).prop('taskId',taskId);
          $(`#${taskId}`).append(tr);
        }
      })

点击跳转页面，使用委托事件绑定点击事件，调用showPage API打开一个临时页面，并将要展示的数据传过去。

    
    
    $("table").delegate('.info','click',function(){
       let info = data[$(this).prop('taskId')][$(this).prop('ip')][$(this).prop('port')];
    //因为整合数据后偶尔会没有ip与port,所以在手动设置一遍
        info.ip = [$(this).prop('ip')];
    info.port = [$(this).prop('port')];
        goby.showPage(`./detail.html?info=${encodeURI(JSON.stringify(info))}`)
     })

 **2.2.4 数据展示**

详情页面中就是将传送数据的展示：

![](https://image.3001.net/images/20201126/1606362960_5fbf275037ee06e3d34bf.gif!small)

## 0x003 小结

这个插件没有使用第三方UI框架，写的样式很简单，这次在showPage页面中内置了goby对象，不需要在通过parent.goby来访问API，可直接使用，除此之外内置了一些css简单样式，不需要自己写的多复杂，只是简单的展示数据库信息。

Goby的showPage页面的还内置的一些css颜色变量（主题颜色变量），我们在开发的时候可以使用这些变量来设置颜色，这样我们的页面还会随着Goby主题的切换而变化：

![](https://image.3001.net/images/20201126/1606363003_5fbf277b95b46bb91353b.png!small)

 **如何下载Database Asset插件？**

Database
Asset目前只支持到超级内测版，后面很快支持到内测版、开发版与大家见面，届时，后台路径爆破、IP地理位置识别、操作系统识别等需求都可以通过此方式实现。

> 如何开启一个自定义页面
>
> <https://www.bilibili.com/video/BV1Ha411w7RF/>
>
> 绑定事件通知
>
> <https://www.bilibili.com/video/BV1Py4y1q7LD/>
>
> 设置Badge
>
> <https://www.bilibili.com/video/BV1Ur4y1F7Bp/>
>
> 默认浏览器打开给定的URL
>
> <https://www.bilibili.com/video/BV11z4y1k7zP/>

Goby内测版：微信公众号GobySec  
Goby正式版：[https://gobies.org﻿](https://gobies.org)

