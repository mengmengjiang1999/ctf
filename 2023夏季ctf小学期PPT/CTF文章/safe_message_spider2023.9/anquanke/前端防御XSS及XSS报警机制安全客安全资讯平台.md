# 前端防御XSS及XSS报警机制

阅读量 **132537**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-08-05 11:34:30

 **x**

##### 译文声明

本文是翻译文章，文章来源：Black-Hole

译文仅供参考，具体内容表达以及含义原文为准。

**author:Black-Hole**

前言:

我不否认前端在处理XSS的时候没有后端那样方便快捷,但是很多人都在说过滤XSS的事就交给后端来做吧。前端做没什么用。我个人是非常反感这句话的。虽然说前端防御XSS比较麻烦,但是,不是一定不行。他只是写的代码比后端多了而已。而且前端防御XSS比后端防御XSS功能多,虽说后端也可以完成这些功能,但是代码量会比前端代码多很多很多。其实说了那么多,交给nginx||apache||nodeJs||Python会更好处理。但是我不会C,也就没办法写nginx模块了。而且也不在本文章的范围内,等我什么时候学会C再说把。有人会问为什么不直接防御,而是不防御报警呢。很简单,因为防御的话,攻击者会定位到那一段的JavaScript代码,从而下次攻击的时候绕过代码。如果不防御而报警的话,攻击者会降低警觉,不会在看JavaScript代码(至少我是这样)。回到正题,下面说的代码,是基于thinkphp框架和bootstrap3.3.5框架。如果你的网站没有使用thinkphp3.2.3框架的话,可以参照我的思路重新写一个。这里我强调一下“前端防御XSS是建立在后端忘记做过滤,没有做过滤,疏忽做过滤的基础上的。

**  
**

**0x01:后端数据反馈过滤**

现在大部分的网站都是在后端过滤一下后,就交给数据库,然后前端输出,整个流程只有后端做了防护,一般这个防护被绕过或者某个参数的防护没有做,那么网站就会被沦陷了(请别以为XSS只能获取cookie,熟练的程度取决于你的思想和编程)

现在我们来假设一下网站的一个URL参数没有做好过滤,直接导入数据库了,然后在前端反馈结果。代码如下:

把用户输入的内容导入到数据库里defenderXssTest_GetData.php:

    
    
    <?php
      if(empty($_GET['xss'])){         //判断当前URL是否存在XSS参数
        exit();
      }
      $xssString= $_GET['xss'];
      /*数据库基础配置*/
      $mysql_name='localhost';
      $mysql_username='root';
      $mysql_password='123456';
      $mysql_database='xsstest';
      $conn= mysql_connect($mysql_name,$mysql_username,$mysql_password);
      mysql_query("setnames 'utf8'");
      mysql_select_db($mysql_database);
      $sql= "insert into XSSTest (xss) values ('$xssString')";
      mysql_query($sql);
      mysql_close();

返回数据库中最后一条数据内容(即最新的内容)defenderXssTest_QueryData.php:

    
    
    <?php
    /*数据库基础配置*/
      $mysql_name='localhost';
      $mysql_username='root';
      $mysql_password='123456';
      $mysql_database='xsstest';
      $conn= mysql_connect($mysql_name,$mysql_username,$mysql_password);
      mysql_query("setnames 'utf8'");
      mysql_select_db($mysql_database);
      $sql="select * from XSSTest where id = (select max(id) fromXSSTest)";        //返回数据库中最后一条数据
      $xssText= mysql_query($sql);
      while($row= mysql_fetch_array($xssText)){ //显示从数据库中返回的数据
        echo$row['xss'];
      }
      mysql_close();

  

前端输入及反馈defenderXssTest.html:

    
    
    <!DOCTYPEhtml>
    <html>
    <head>
      <metacharset="utf-8">
      <title>前端防御XSS#Demo1</title>
    </head>
    <body>
      <inputtype="text" name="xss">
      <inputtype="submit" value="提交"id="xssGet">
    </body>
    <!--测试请记得更换jQuery路径--!>
    <scripttype="text/javascript"src="/Public/js/library/jquery.js"></script>
    <script>
      $("#xssGet").click(function(){
        $.ajax({
          url:'/defenderXssTest_GetData.php',
          type:'get',
          dataType:'text',
          data:"xss="+$('input:first').val(),
          cache:false,
          async:false,
        })
        .done(function(){
          $.ajax({
            url:'/defenderXssTest_QueryData.php',
            type:'post',
            dataType:'text',
            cache:false,
            async:false,
          })
          .done(function(data){
            $("body").append(data);
          })
        })
      });
    </script>
    </html>

一共三个文件,因为测试用,我就没把数据库基础配置分离出来放在其他文件里了。

现在我们在浏览器里打开defenderXssTest.html文件:

输入“<script>(1)</script>”后,点击“提交”。会发现弹窗了:

现在我们再看下数据库:

已经导入到数据库里了。

OK,以上就是最普通的储蓄型XSS案例。为什么会出现这个问题呢,是因为PHP没有做好过滤。同时前端也没有做好过滤,这里会有人说前端做没用的,攻击者可以使用burp抓到此数据包,然后改包就可以绕过了。对,确实是这样。但是大伙从一开始就已经被误导了。想知道哪里被误导么,往下看。

这里我画个前端、Nginx、后端都做了过滤的图:

思维导图URL:[https://www.processon.com/view/link/56c486cde4b0e2317a8b6681](https://www.processon.com/view/link/56c486cde4b0e2317a8b6681)

这里我们可以看到防火墙的第一道门是前端过滤XSS机制。也是目前被大家所熟知的过滤结构。而本章要说的是:为什么不把前端过滤copy或者move到后端过滤机制下呢?

这里是新型的过滤机制的图:

思维导图URL:[https://www.processon.com/view/link/56c4882ce4b0e5041c35ab53](https://www.processon.com/view/link/56c4882ce4b0e5041c35ab53)

这里我们在后端过滤机制的后面加上了前端过滤。为什么要这样做呢?

大家都知道前端过滤XSS是可以被抓包软件给修改的,所以是可以绕过,没有什么用。而Nginx过滤我相信大家都知道,很少有人愿意采用它,因为如果是做安全文章一类的话,是会被Nginx给抛弃当前的数据包的,也就是你发布的文章不会被存到数据库里,而且Nginx防御XSS模块并没有前端、后端那样简单方便,需要配置的东西很多。也导致了很多管理员不在Nginx安全上下功夫,即使管理员配置了Nginx过滤XSS模块,也可以绕过。

利用Nginx的一处逻辑缺陷(详情请移步到:[http://www.freebuf.com/articles/web/61268.html](http://www.freebuf.com/articles/web/61268.html)
文章里的0x03小节:利用Nginx&Apache环境bug来实现攻击),至于后端过滤机制肯定会有不严谨的时候,不然也而不会导致那么多XSS漏洞了。所以当攻击者输入的XSS字符串绕过了前端、Nginx、后端的话,那么就会直接导入到数据库中。那么这个时候后端传来的数据就不可信了。而如果我们在前端显示后端传来的数据时加了过滤会怎么样呢,答案是verygood。当然了,这里有个前提,是前端显示后端传来数据的时候使用的是AJAX方法,而不是类似ThinkPHP这样在模板里调用。确切的说:此方法只针对于API接口

现在我们来做一个测试,之前的代码就是使用了AJAX方法,而

defenderXssTest_GetData.php和defenderXssTest_QueryData.php就类似于后端的API接口。我们现在在原有的基础上添加一些代码:

下面是前端过滤XSS的代码,取自于百度FEX前端团队的Ueditor在线编辑器:

    
    
    functionxssCheck(str,reg){
      returnstr ? str.replace(reg ||/[&<">'](?:(amp|lt|quot|gt|#39|nbsp|#d+);)?/g,function (a, b) {
        if(b){
          returna;
        }else{
          return{
            '<':'&lt;',
            '&':'&amp;',
            '"':'&quot;',
            '>':'&gt;',
            "'":''',
          }[a]
        }
      }): '';
    }

然后我们在原有代码的基础上添加xssCheck()函数就行了。如下:

    
    
    <!DOCTYPEhtml>
    <html>
    <head>
      <metacharset="utf-8">
      <title>前端防御XSS#Demo1</title>
    </head>
    <body>
      <inputtype="text" name="xss">
      <inputtype="submit" value="提交"id="xssGet">
    </body>
    <scripttype="text/javascript"src="/Public/js/library/jquery.js"></script>
    <script>
      $("#xssGet").click(function(){
      $.ajax({
        url:'/defenderXssTest_GetData.php',
        type:'get',
        dataType:'text',
        data:"xss="+$('input:first').val(),
        cache:false,
        async:false,
      })
      .done(function(){
        $.ajax({
          url:'/d  efenderXssTest_QueryData.php',
            type:'post',
            dataType:'text',
            cache:false,
            async:false,
          })
          .done(function(data){
            $("body").append(xssCheck(data));
          })
        })
      });
      functionxssCheck(str,reg){
        returnstr ? str.replace(reg ||/[&<">'](?:(amp|lt|quot|gt|#39|nbsp|#d+);)?/g,function (a, b) {
          if(b){
            returna;
          }else{
            return{
              '<':'&lt;',
              '&':'&amp;',
              '"':'&quot;',
              '>':'&gt;',
              "'":''',
            }[a]
          }
        }): '';
      }
    </script>
    </html>

现在我们来输入XSS字符串看看:

变成了这个样子。我们再去数据库里看下:

的确是完整的XSS字符串,但是前端过滤了,导致此XSS没有用武之地。

所以前端开发人员只需要在网站的base.js代码里把过滤XSS的函数写进去,再把每一个ajax传过来的数据加上函数就可以了。

**  
**

**0x02:前端报警机制**

这里的报警机制不能说特别的完整,是可以绕过的。那这个报警机制到底有何用处呢?就是在攻击者测试的时候发现及报警。

我们都知道测试XSS的时候和装逼的时候,攻击者会输入()函数,而之前的过滤方式,都是使用正则匹配,从而导致正则过长,匹配不易,运行过慢等问题。而现在我们完全可以重写函数来让攻击者在测试的时候,使用的是我们已经重写后的函数,这样做的好处是:当当前的参数不存在XSS的时候,这些函数是不会被触发的。而当当前参数存在XSS的时候,攻击者会依次输入:woaini->查看是否在源码里输出->woaini<>->查看<>有没有被过滤->输入<script>alret(1)</script>或者<imgsrc="test"
onerror="(1)"/>->使用了我们重写的函数->触发报警机制。这样说可能有些人看不懂,下面是我画的图:

思维导图:[https://www.processon.com/view/link/56c55805e4b0e5041c39261f](https://www.processon.com/view/link/56c55805e4b0e5041c39261f)

让我们来看下具体的代码吧:

    
    
    varbackAlert = ;     //把赋值给backAlert,当后面重写时,避免照成死循环,照成溢出错误。
    window.= function(str){       //重写函数
      backAlert(str);
      console.log("已触发报警,将数据发送到后台");
    }

再把console.log换成ajax把数据发送给后台应用。后台接受的时候记得做过滤。前端代码记得加密,防止攻击者看出意图从而导致绕过,不触发报警。因为可能有些公司、个人网站已经有了自己的攻击报警系统、智能日志检索系统,我也就不再写了。把ajax发送的数据过滤后存到数据库里,再显示就行了。可以根据自己现有的框架进行开发,思路上面已经了,不难理解,代码也不难写。如果你不会或者说是不想写,可以等到我下一篇的文章。到时候里面会有全部的源代码。

  

**0x3:前端报警机制之前端要做的事**

其实标题应该改成“XSS报警机制”的,因为在这一章里使用了大量的后端代码。但是第一章的标题都出来了,也没法改了。

前端要做的事情在第一章的时候就已经说了,代码如下:

现在我们就是针对第38行进行修改,改成我们后台接受的APIURL。就像这样:

对,就这一行。没有其他代码。在实际的线上环境中,也只需要上面5行。可以直接copy到您的线上环境中,记得把倒数第二行的url改成自己的地址就行了。难道就那么简单?不,后面还会一点前端代码

  

**0x04:前端报警机制之数据库要做的事**

一共两个表。fecm_user和fecm_bugdata。

fecm_user的字段信息如下:

name为管理员账户名

md5name为3次name值的md5

password为3次密码的md5

email为管理员邮箱

create_date为管理员创建时间

为了安全起见(其实就是懒)没有写添加管理员的,自行在数据库里添加

fecm_bugdata的字段信息如下:

url为漏洞的url地址

category为漏洞类型

cookies为攻击者的cookies

ua为攻击者的User-Agent

hxff_ip为攻击者的HTTP_X_FORWARDED_FOR

hci_ip为攻击者的HTTP_CLIENT_IP

ra_ip为攻击者的REMOTE_ADDR

time为攻击者攻击的时间

fixes为漏洞是否修复(0为未修复,1为已修复)

  

**0x05:前端报警机制之后端要做的事**

因为后端代码太多,所以我就说一些核心的后端处理代码。

在0x01节里,有个核心的代码是newImage().src =
'[http://fecm.cn/Api/addVul/](http://fecm.cn/Api/addVul/)';

接下来我们来说说这个Api的处理方式(ThinkPHP代码)

    
    
    publicfunction addVul(){
      if(I('get.category','','int')== ""){
        $this->ajaxReturn(array(
          "typeMsg"=> "error",
          "msgText"=> "漏洞类型错误",
        ));
      }
      switch(I('get.category','','int')) {
        case'1':
          $vul['category']= "触发alret函数";
        break;
        case'2':
          $vul['category']= "发现不在白名单里的第三方JavaScript资源";
        break;
        default:
          $this->ajaxReturn(array(
            "typeMsg"=> "error",
            "msgText"=> "漏洞类型错误",
          ));
          break;
      }
      if($_SERVER['HTTP_X_FORWARDED_FOR']=== null){
        $vul['hxff_ip']= "攻击者没有通过代理服务器访问";
      }else{
        $vul['hxff_ip']= I('server.HTTP_X_FORWARDED_FOR');       //获取攻击者的HTTP_X_FORWARDED_FOR
      }
      if($_SERVER['HTTP_CLIENT_IP']=== null){
        $vul['hci_ip']= "攻击者数据包头部没有HTTP_CLIENT_IP";
      }else{
        $vul['hci_ip']= I('server.HTTP_CLIENT_IP');//获取攻击者的HTTP_CLIENT_IP
      }
      $vul['ra_ip']= I('server.REMOTE_ADDR');   //获取攻击者的REMOTE_ADDR
      $vulcookie = I('cookie.');       //获取攻击者的cookies
      for($i= 0;$i<count($vulcookie);$i++){
        $vul['cookies'].=array_keys($vulcookie)[$i].'='.$vulcookie[array_keys($vulcookie)[$i]].';'; //拼接成方便查看的cookies格式
      }
      $vul['url'] = I('server.HTTP_REFERER');   //获取攻击者攻击成功的url
      $vul['ua'] = I('server.HTTP_USER_AGENT'); //获取攻击者的User-Agent
      $vul['time'] = date("Y-m-d");    //获取攻击者攻击的时间
      $vul['fixes']= 0;       //默认为漏洞未修复
      $bugData= M('bugdata'); //连接fecm_bugdata数据库
      $bugData->data($vul)->add();     //添加到数据库中
    }

因为这里是接受攻击信息,不能有管理员验证。

后台有一个数据库可视化的表格,这里我使用的Chart.js,下面是后端代码：

    
    
    publicfunction index(){
      $reportForm= M('bugdata');       //连接fecm_bugdata数据库
      $dateTimeLabels= [];
      $dateTimeTotal= [];
      for($i= 0;$i < 7;$i++){ //获取近7天的数据
        $time= date("Y-m-d",strtotime(-$i." day"));
        array_unshift($dateTimeLabels,$time);
        $data['time']= array('like','%'.$time.'%');
        array_unshift($dateTimeTotal,$reportForm->where($data)->count());
      }
      $reportForm= json_encode(["Labels" => $dateTimeLabels,"Total"=> $dateTimeTotal]);    //转化成json格式
      $this->assign('reportForm',$reportForm)->assign('total',total());   //交给前端模块
      $this->display();       //前端页面生成
    }

前端代码:

    
    
    varlineChartData = {
      labels:eval({$reportForm})['Labels'],
      datasets: [{
        fillColor: "rgba(151,187,205,0.5)",
        strokeColor: "rgba(151,187,205,1)",
        pointColor: "rgba(151,187,205,1)",
        pointStrokeColor: "#fff",
        data: eval({$reportForm})['Total']
      }]
    }
    varmyLine = newChart(document.getElementById("Statistics").getContext("2d")).Line(lineChartData);

实际的效果图:

**0x06:让我们实际测试一下**

代码就用0x01节的代码。我们输入<script>(1)</script>。看一下:

我们再去平台看一下:

成功显示了。

  

**0x07:检测第三方js资源是否为xss脚本**

这一节需要用到之前长短短分享的代码:

    
    
    for(vari=0,tags=document.querySelectorAll('iframe[src],frame[src],script[src],link[rel=stylesheet],object[data],embed[src]'),tag;tag=tags[i];i++){
      var a = document.createElement('a');
      a.href= tag.src||tag.href||tag.data;
      if(a.hostname!=location.hostname){
        console.warn(location.hostname+'发现第三方资源['+tag.localName+']:'+a.href);
      }
    }

但是他这里只是在console里显示,没有进一步的操作,而且他这里同时检测了iframe、frame、script、link、object、embed标签,对我们来说只需要script标签就行了,于是我重写了这段代码,首先我们需要一个白名单列表,用于放置网站允许第三方加载的url地址:

    
    
    varscriptList = [
      location.hostname,
    ]

这里只是默认的只允许当前域名加载,打击爱可以根据自己的需要添加。

然后就是获取当前网页的所有script标签:

    
    
    varwebScript = document.querySelectorAll('script[src]');

在把当前的地址赋值varwebHost
=location.hostname;至于为什么不放在for循环里,因为根据js优化规则,for循环里避免多次一样的赋值。

接下来就是for循环里的代码了:

    
    
    for(vari = 0;i < webScript.length;i++){
      var a = document.createElement('a');      //建立一个新的a标签,方便取值
      a.href= webScript[i].src;        //把script里的src赋值给a标签里的href属性
        if(a.hostname!= webHost){      //对比,是否为第三方资源
        for(varj = 0;j < scriptList.length;j++){
          if(a.hostname!= scriptList[i]){       //判断当前的第三方资源是否在白名单里
            newImage().src = 'http://fecm.cn/Api/addVul/category/2';      //发送给FECM
          }
        }
      }
    }

这里我做了一个测试,加载[hi.baidu.com](http://hi.baidu.com)的资源:

刷新后,打开FECM平台,看一下:

  

**0x08:结语**

之前EtherDream已经说了前端防火墙了,只是他做的是防御,而我是不防御(也可以防御)直接报警。然后人工修复代码。因为虽然你防御住了,但是后端漏洞还在那,而触发报警机制后就可以进行人工修复。不是说EtherDream写的不好,反之非常好,在他的基础上也可以修改成前端报警机制,不过我还是喜欢让攻击者高兴几十分钟后,就懵逼的样子。在EtherDream的代码中有一个很棒的代码片段,他使用了内联事件监听了onclick等on事件,可以近一步的监听到黑客的操作。因为版权问题,我不方便把代码贴到本文中,毕竟是别人的思想结晶。想了解的话可以去查看:

[http://fex.baidu.com/blog/2014/06/xss-frontend-firewall-1/](http://fex.baidu.com/blog/2014/06/xss-frontend-firewall-1/)
本来打算采用ED的on事件拦截代码的,但是发现on事件在程序里也会大量使用,索性就没有添加。使用时记得在ApplicationHomeConfconfig.php改下配置(我已经全部加了注释,即使不会thinkphp的也可以搭建)个人代码写的没有多好,思路可能也比较烂。如果您有什么意见欢迎提出来,我会进一步修改的。

下载地址:[https://github.com/BlackHole1/Fecm](https://github.com/BlackHole1/Fecm)

**Author:Black-Hole**

**Blog:bugs.cc**

**github:**[
**https://github.com/BlackHole1/**](https://github.com/BlackHole1/)

**Twitter:**[
**https://twitter.com/Free_BlackHole**](https://twitter.com/Free_BlackHole)

[**Email:158blackhole@gmail.com**](mailto:Email%3A158blackhole@gmail.com)

本文翻译自Black-Hole [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **_Black_Hole_** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84339](/post/id/84339)

安全客 - 有思想的安全新媒体

本文转载自: [Black-Hole]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t017ac7ce07b1fb544e.jpg)
_Black_Hole_

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

