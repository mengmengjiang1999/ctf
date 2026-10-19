jq动画

[ 每天进步一点点5454](https://www.jianshu.com/u/897bc9137aee)关注赞赏支持

# jq动画

jq函数

    
    
    当DOM加载完成后，执行其中的函数。
    
    jQuery 代码:
    $(function(){
      // 文档就绪
    });
    $(document).ready(){}
    

长度\动画\显示\隐藏\上拉\下拉

    
    
    $("#show").click(function () {
          var n = $("div").queue("fx");
          $("span").text("Queue length is: " + n.length);
    });
    function runIt() {
          $("div").show("slow");
          $("div").animate({left:'+=200'},2000);
          $("div").slideToggle(1000);
          $("div").slideToggle("fast");
          $("div").animate({left:'-=200'},1500);
          $("div").hide("slow");
          $("div").show(1200);
          $("div").slideUp("normal", runIt);
    }
    runIt();    
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [2019-11-26 流式编程：让页面飞起来](https://www.jianshu.com/p/28b0978db2d1)

前端开发一直有它自己的特殊性。要做开发不仅仅要学 HTML，还要学 CSS、JS 等，甚至还有 Node.js 这...

[半眼鱼](https://www.jianshu.com/u/8c590065e5b9)阅读 394评论 0赞 1

  * [2019-11-26开题答辩](https://www.jianshu.com/p/3bb73f9b84db)

研究应用场景： 可以先检测GPS设备失效； 判断无人机即将飞入禁飞区； 无人机在失去GPS信息的时候，会按照之前的...

[keaiduoduo](https://www.jianshu.com/u/e302a5fabe93)阅读 623评论 0赞 1

  * [2019-11-26](https://www.jianshu.com/p/a7e98e4b3263)

##css3动画 过渡：transition 2D转换transform 3D转换transform 动画：ani...

[猴子不是妖精](https://www.jianshu.com/u/89489c31d58d)阅读 128评论 0赞 0

  * [2019-11-26](https://www.jianshu.com/p/9900affdbfef)

1、新增数据 基本语法：insert into 表名 [(字段列表)] 2、主键冲突（Duplicate key）...

[7k7k扛把子](https://www.jianshu.com/u/5d8a5d2e7a5e)阅读 100评论 0赞 0

  * [2019-11-26](https://www.jianshu.com/p/4e955eba6367)

NCTF中密码学的学习 keyboard 几个wp中用到的函数 .split(' ')split(分隔符，分割几次...

[掩掩](https://www.jianshu.com/u/5ee80ac05230)阅读 394评论 0赞 0

 