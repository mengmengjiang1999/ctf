***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![jhk-1532485926451.jpeg](https://image.3001.net/images/20180725/15325007614739.jpeg!small)

##  ** **一、前言****

**修饰器(modifier)可以改变函数的行为，例如作为前置的检测条件。同时修饰器具有可继承属性，可以由派生合约中的定义覆盖。本次BUGX.IO区块链安全课堂给大家进行修饰器的相关漏洞分析。**

##  **二、什么是修饰器**  

修饰器具有可继承属性，可以由派生合约中的定义覆盖，如下示例代码，由于 onlyOwner 的修饰，给 foo 函数加了一个前置条件，即只有 owner
才能成功调用此函数，否则就会报错回滚。其中 `_;` 表示函数中的其余代码。

    
    
    pragma solidity ^0.4.24;
    contract Foo {
      address public owner;
      constructor() public {
          owner = msg.sender;
      }
      modifier onlyOwner() {
          require(msg.sender == owner);
          _;
      }
      function foo() onlyOwner public view returns(bool){
          return true;
      }
    }  
    

并且，修饰器也能带入参数，如：  

    
    
    modifier assertValueIsOne(uint value) {
      assert(value == 1);
      _; // original function goes at this point
    }
    function doSomething(uint value) assertValueIsOne(value) {
      // do Something
    }  
    

##  **三、常见修饰器**

常见的库合约包括管理者权限控制合约、暂停功能合约、黑名单管理合约、日志记录等等，而常见的修饰器有
onlyOwner、isOwner、whenNotPaused、whenPaused、manager、execute、onlyContractCreator
等等。

常见权限控制的修饰器写法有：

    
    
    modifier onlyOwner(){
        if(msg.sender != owner){ throw;}
        _;
    }
    modifier  onlyOwner{
          if(msg.sender != owner){
              revert();
          }else{
              _;
          }
      }
    modifier onlyOwner() {
      if(msg.sender != owner) revert();
      _;
    }
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }
    modifier onlyOwner {
      assert(msg.sender == owner);
      _;
    }
    
    
    
      
    

日志记录：  

    
    
    event StartEvent();
    event FinishEvent();
    modifier logEvents {
      StartEvent();
      _;
      FinishEvent();
    }
    function toggle () logEvents {
    }
    
      
    

## **四、常见修饰器漏洞类型**  

 **1、Modifier Wrong Check 修饰器检测逻辑错误**

修饰器中的判断错误，导致修饰器无法起到开发者预期的控制作用。

如 I_See_Voice_Token (ISVT) 合约 ：

<https://etherscan.io//address/0xa6b0412276b2484cfb370890b9d07e0c8f1f7684#code>

    
    
    modifier  onlyOwner() {
        require(msg.sender != owner);
        _;
    }  
    

正确的写法应该是 `==` ,结果错写成了 `!=`，从面造成了权限控制失效。

 **2、Modifier Invalid Check 修饰器检测无效漏洞**

缺少使用 if、 if throw、if revert()、require、assert 作为条件判断，使得判断无效，导致修饰器的权限控制功能失效。

如 BancorKiller 合约 ：

<https://etherscan.io//address/0x32a8c2da487ff26ef5778fd44dc8eaa73d7bb437#code>

    
    
    modifier onlyAdmin() {
        msg.sender == admin;
        _;
    }  
    

使用以下代码进行测试，可以发现，任何人都可以调用 foo_flaw 函数，正确写法的 foo_right 函数则只有管理员才可以调用。

    
    
    pragma solidity ^0.4.24; 
    contract foo {
      address public admin;
      constructor() public {
          admin = msg.sender;
      }
      modifier onlyAdmin_flaw() {
          msg.sender == admin;
          _;
      }
      function foo_flaw() onlyAdmin_flaw public view returns(bool){
          return true;
      }
     
      modifier onlyAdmin_right() {
          require(msg.sender == admin);
          _;
      }
      function foo_right() onlyAdmin_right public view returns(bool){
          return true;
      }
    }
    
    
    
      
    

**3、更复杂的情况带参修饰器漏洞**  

由于修饰器能够带参执行，这种类型的漏洞就只能按照实际情况进行分析。

##  **五、修复方案**  

严格验证修饰器的判断条件，合约发布做好前充分的功能测试。

##  **六、参考资料**

<https://solidity.readthedocs.io/en/latest/contracts.html?highlight=modifier#function-modifiers>

## **七、公司介绍**  

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。  

 ***本文作者：BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**

