作者：LoRexxar'@知道创宇404区块链安全研究团队  
时间：2018年8月10日  
英文版：<https://paper.seebug.org/670/>

### 一、 简介

在知道创宇404区块链安全研究团队整理输出的《知道创宇以太坊合约审计CheckList》中，把“未触发Transfer事件问题”、“未触发Approval事件问题”、“假充值漏洞”、“构造函数书写错误”等问题统一归类为“以太坊智能合约规范问题”。

“昊天塔(HaoTian)”是知道创宇404区块链安全研究团队独立开发的用于监控、扫描、分析、审计区块链智能合约安全自动化平台。我们利用该平台针对上述提到的《知道创宇以太坊合约审计CheckList》中“以太坊智能合约规范”类问题在全网公开的智能合约代码做了扫描分析。详见下文：

### 二、漏洞详情

ERC20是一种代币标准，用于以太坊区块链上的智能合约。ERC20定义了一种以太坊必须执行的通用规则，如果在以太坊发行的代币符合ERC20的标准，那么交易所就可以进行集成，在它们的交易所实现代币的买卖和交易。

ERC20中规定了transfer函数必须触发Transfer事件，transfer函数必须返回bool值，在进行余额判断时，应抛出错误而不是简单的返回错误，approve函数必须触发Approval事件。

#### 1、未触发Transfer事件

    
    
    function transfer(address _to, uint256 _value) public returns (bool success) {
            require(balanceOf[msg.sender] >= _value);           
            require(balanceOf[_to] + _value >= balanceOf[_to]); 
            balanceOf[msg.sender] -= _value;                            
            balanceOf[_to] += _value;                           
            return true;
        }

上述代码在发生交易时未触发Transfer事件，在发生交易时，未产生event事件，不符合ERC20标准，不便于开发人员对合约交易情况进行监控。

#### 2、未触发Approval事件

    
    
        function approve(address _spender, uint256 _value) public
            returns (bool success) {
            allowance[msg.sender][_spender] = _value;
            return true;
        }

上述代码在发生交易时未触发Approval事件，在发生交易时，未产生event事件，不符合ERC20标准，不便于开发人员对合约情况进行监控。

#### 3、假充值漏洞

    
    
        function transfer(address _to, uint256 _amount) returns (bool success) {
            initialize(msg.sender);
    
            if (balances[msg.sender] >= _amount
                && _amount > 0) {
                initialize(_to);
                if (balances[_to] + _amount > balances[_to]) {
    
                    balances[msg.sender] -= _amount;
                    balances[_to] += _amount;
    
                    Transfer(msg.sender, _to, _amount);
    
                    return true;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        }

上述代码在判断余额时使用了if语句，ERC20标准规定，当余额不足时，合约应抛出错误使交易回滚，而不是简单的返回false。

这种情况下，会导致即使没有真正发生交易，但交易仍然成功，这种情况会影响交易平台的判断结果，可能导致假充值。

2018年7月9日，慢雾安全团队发布了关于假充值的漏洞预警。

2018年7月9日，知道创宇404区块链安全研究团队跟进应急该漏洞，并对此漏洞发出了漏洞预警。

#### 4、构造函数书写错误漏洞

Solidity0.4.22版本以前，编译器要求，构造函数名称应该和合约名称保持一致，如果构造函数名字和合约名字大小写不一致，该函数仍然会被当成普通函数，可以被任意用户调用。

Solidity0.4.22中引入了关于构造函数constructor使用不当的问题，constructor在使用中错误的加上了function定义，从而导致constructor可以被任意用户调用，会导致可能的更严重的危害，如Owner权限被盗。

##### 构造函数大小写错误漏洞

    
    
    contract own(){
        function Own() {
            owner = msg.sender;
        }
    }

上述代码错误的将构造函数名大写，导致构造函数名和合约名不一致。这种情况下，该函数被设置为一个普通的public函数，任意用户都可以通过调用该函数来修改自己为合约owner。进一步导致其他严重的后果。

2018年6月22日，MorphToken合约代币宣布更新新的智能合约，其中修复了关于大小写错误导致的构造函数问题。

2018年6月22日，知道创宇404区块链安全研究团队跟进应急，并输出了《以太坊智能合约构造函数编码错误导致非法合约所有权转移报告》。

##### 构造函数编码错误漏洞

    
    
        function constructor() public {
            owner = msg.sender;
        }

上述代码错误的使用function来作为constructor函数装饰词，这种情况下，该函数被设置为一个普通的public函数，任意用户都可以通过调用该函数来修改自己为合约owner。进一步导致其他严重的后果。

2018年7月14日，链安科技在公众号公布了关于constructor函数书写错误的问题详情。

2018年7月15日，知道创宇404区块链安全研究团队跟进应急，并输出了《以太坊智能合约构造函数书写错误导致非法合约所有权转移报告》

### 三、漏洞影响范围

使用Haotian平台智能合约审计功能可以准确扫描到该类型问题。

![](https://images.seebug.org/content/images/2018/08/0f362a35-6a90-4676-80b8-3a5ccfe06ae3.png-w331s)

基于Haotian平台智能合约审计功能规则，我们对全网的公开的共39548 个合约代码进行了扫描，其中共14978个合约涉及到这类问题。

#### 1、 未触发Transfer事件

截止2018年8月10日为止，我们发现了4604个存在未遵循ERC20标准未触发Transfer事件的合约代码，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/eb7cc870-39c6-4dd2-b812-65a247586b5e.png-w331s)

#### 2、 未触发Approval事件

截止2018年8月10日为止，我们发现了5231个存在未遵循ERC20标准未出发Approval事件的合约代码，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/bdcbc41c-38bf-48dd-96ef-2ca446583116.png-w331s)

#### 3、假充值漏洞

2018年7月9日，知道创宇404区块链安全研究团队在跟进应急假充值漏洞时，曾对全网公开合约代码进行过一次扫描，当时发现约3141余个存在假充值问题的合约代码，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/be0be822-ea17-44eb-93de-b636496926e2.png-w331s)

截止2018年8月10日为止，我们发现了5027个存在假充值问题的合约代码，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/5105a238-f377-4af4-8839-17642a770ba7.png-w331s)

#### 4、构造函数书写问题

##### 构造函数大小写错误漏洞

2018年6月22日，知道创宇404区块链安全研究团队在跟进应急假充值漏洞时，全网中存在该问题的合约约为16个。

截止2018年8月10日为止，我们发现了90个存构造函数大小写错误漏洞的合约代码，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/b1369bdc-51d1-4592-9c7d-735c791c4473.png-w331s)

##### 构造函数编码问题

截止2018年8月10日为止，我们发现了24个存在构造函数书写问题的合约代码，比2018年7月14日对该漏洞应急时只多了一个合约，其中交易量最高的10个合约情况如下：

![](https://images.seebug.org/content/images/2018/08/6890c76c-22bf-4de2-b45a-64b42a39cb8f.png-w331s)

### 四、修复方式

#### 1）transfer函数中应触发Tranfser事件

    
    
      function transfer(address _to, uint256 _value) public returns (bool) {
        require(_value <= balances[msg.sender]);
        require(_to != address(0));
    
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
      }

#### 2）approve函数中应触发Approval事件

    
    
      function approve(address _spender, uint256 _value) public returns (bool) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
      }

#### 3）transfer余额验证时应使用require抛出错误

    
    
      function transfer(address _to, uint256 _value) public returns (bool) {
        require(_value <= balances[msg.sender]);
        require(_to != address(0));
    
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
      }

#### 4）0.4.22版本之前，构造函数应和合约名称一致

    
    
    contract ownable {
        function ownable() public {
        owner = msg.sender;
      }

#### 5）0.4.22版本之后，构造函数不应用function修饰

    
    
    constructor() public {
            owner = msg.sender;
        }

### 五、一些思考

上面这些问题算是我在回顾历史漏洞中经常发现的一类问题，都属于开发人员没有遵守ERC20标准而导致的，虽然这些问题往往不会直接导致合约漏洞的产生，但却因为这些没有遵守标准的问题，在后期对于合约代币的维护时，会出现很多问题。

如果没有在transfer和approve时触发相应的事件，开发人员就需要更复杂的方式监控合约的交易情况，一旦发生大规模盗币时间，甚至没有足够的日志提供回滚。

如果转账时没有抛出错误，就有可能导致假充值漏洞，如果平台方在检查交易结果时是通过交易状态来判断的，就会导致平台利益被损害。

如果开发人员在构造函数时，没有注意不同版本的编译器标准，就可能导致合约所有权被轻易盗取，导致进一步更严重的盗币等问题。

我们在对全网公开的合约代码进行扫描和监控时容易发现，有很大一批开发人员并没有注意到这些问题，甚至构造函数书写错误这种低级错误，在漏洞预警之后仍然在发生，考虑到大部分合约代码没有公开，可能还有很多开发者在不遵守标准的情况下进行开发，还有很多潜在的问题需要去考虑。

这里我们建议所有的开发者重新审视自己的合约代码，检查是否遵守了ERC20合约标准，避免不必要的麻烦以及安全问题。

* * *

**智能合约审计服务**

针对目前主流的以太坊应用，知道创宇提供专业权威的智能合约审计服务，规避因合约安全问题导致的财产损失，为各类以太坊应用安全保驾护航。

知道创宇404智能合约安全审计团队： <https://www.scanv.com/lca/index.html>  
联系电话：(086) 136 8133 5016(沈经理，工作日:10:00-18:00)

欢迎扫码咨询：
![](https://images.seebug.org/content/images/2018/08/3adb8e66-32a1-441c-9c6b-4c34e28551a8.png-w331s)

**区块链行业安全解决方案**

黑客通过DDoS攻击、CC攻击、系统漏洞、代码漏洞、业务流程漏洞、API-Key漏洞等进行攻击和入侵，给区块链项目的管理运营团队及用户造成巨大的经济损失。知道创宇十余年安全经验，凭借多重防护+云端大数据技术，为区块链应用提供专属安全解决方案。

欢迎扫码咨询：
![](https://images.seebug.org/content/images/2018/08/bbd55d7f-3bdd-410b-b269-50d0fa82b3ed.png-w331s)

  

### 六、REF

[1] ERC标准  
<https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md>

[2] Morpheus官方公告  
<https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91

b80dbc7655>

[3] 构造函数书写问题漏洞详情  
<https://mp.weixin.qq.com/s/xPwhanev-cjHhc104Wmpug>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/663/>

