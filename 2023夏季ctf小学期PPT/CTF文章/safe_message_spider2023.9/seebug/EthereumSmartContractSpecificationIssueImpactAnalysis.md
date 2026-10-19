Author：Knownsec 404 Blockchain Security Research Team  
Chinese version：<https://paper.seebug.org/663/>

#### 1\. Brief Introduction

The "Unemitted Transfer Event Issue", "Unemitted Approval Event Issue", "Fake
Recharge" Vulnerability and "Writing Error of Constructed Function" are
uniformly classified as "Ethereum smart contract specification problem" in
"Knownsec Ethereum Contract Audit Checklist" which sorted out by the Knownsec
404 Blockchain Security Research Team.

"HaoTian" is an automation platform for monitoring, scanning, analysis and
auditing blockchain smart contract. It is independently developed by the
Knownsec 404 Blockchain Security Research Team. We use this platform to scan
and analyze the smart contract code publicly posted across the web for the
above-mentioned "Ethereum Smart Contract Specification".

#### 2\. Vulnerability Details

ERC20 is a standard of the token for the smart contract on the Ethereum
blockchain. ERC20 defines a general rule that must be enforced by Ethereum.
Exchanges can be integrated to implement token trading if the token issued at
Ethereum reaches the ERC20 standard.

ERC20 stipulates that the transfer function must trigger a transfer event and
return a Boolean value. It should also throw an error instead of returning the
error simply when making a balance judgment. And the approve function must
trigger an approve event.

##### 1) Unemitted Transfer Event

    
    
    function transfer(address _to, uint256 _value) public returns (bool success) {
            require(balanceOf[msg.sender] >= _value);          
            require(balanceOf[_to] + _value >= balanceOf[_to]);
            balanceOf[msg.sender] -= _value;                            
            balanceOf[_to] += _value;                          
            return true;
        }

The above code did not trigger the Transfer event when the transaction
occurred. Failure to comply with the ERC20 standard makes it difficult for
developers to monitor contract transactions.

##### 2) Untriggered Approval Event

    
    
    function approve(address _spender, uint256 _value) public
            returns (bool success) {
            allowance[msg.sender][_spender] = _value;
            return true;
        }

The above code did not trigger the Approve event when the transaction
occurred. Failure to comply with the ERC20 standard makes it difficult for
developers to monitor contract transactions.

##### 3) Fake Recharge Vulnerability

    
    
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

The above code uses the if statement to judge the balance. ERC20 stipulates
the contract should throw an error to roll back the transaction, rather than
returning the error simply when the balance is insufficient.

In this case, the transaction will still succeed even if there is no real
transaction, which may affect the judgment of the trading platform and lead to
false recharge.

On July 9, 2018, SlowMist Security Team issued a warning on the vulnerability
of fake recharge.

On July 9, 2018, the Knownsec 404 Blockchain Security Research Team followed
with the vulnerability and issued a vulnerability warning for the
vulnerability. If the case of the constructor name doesn't match the contract,
this function will still be treated as a normal function and can be called by
any user.

##### 4) Writing Error of Constructed Function

The compiler required that the constructor name should be consistent with the
contract name before the Solidity version 0.4.22 released.

Improper use of constructors is introduced in Solidity 0.4.22. The constructor
adds a function definition incorrectly, which causes the constructor can be
called by any user and lead to more serious harm, such as the Owner's
permission being stolen.

  * Case Error

    
    
    contract own(){
        function Own() {
            owner = msg.sender;
        }
    }

Capitalized constructor name incorrectly causes the constructor name doesn't
match the contract name. In this case, the function is set as a normal public
function. Anyone can modify themselves to the owner of the contract by this
function. That's will lead to other serious results.

On June 22, 2018, the MorphToken contract token announced the update of an
smart new contract, which fixed the constructor problem on case errors.

On June 22, 2018, the Knownsec 404 Blockchain Security Research Team followed
with the emergency and released the "Ethereum smart contract constructor
coding error leading to an illegal contract ownership transfer report."

  * Coding Error

    
    
    function constructor() public {
            owner = msg.sender;
        }

Using function as a decorate word for constructor function is incorrectly in
the above code. In this case, the function is set as a normal public function.
Anyone can modify themselves to the owner of the contract by this function.
That's will lead to other serious consequences.

On July 14, 2018, Link Safe Technology released details in their Official
Account about the constructor function's writing errors.

On July 15, 2018, the Knownsec 404 Blockchain Security Research Team followed
with the emergency and released the "Ethereum smart contract constructor
writing error leading to an illegal contract ownership transfer report."

#### 3\. The Scope within Vulnerability Impact

The smart contract audit function of the Haotian platform can scan for this
type of the problem accurately.

![](https://images.seebug.org/content/images/2018/08/0f362a35-6a90-4676-80b8-3a5ccfe06ae3.png-w331s)

We scanned a total of 39,548 contract codes for the entire network based on
the Haotian platform's smart contract auditing rules. It included a total of
14,978 contracts involving such issues.

##### 1) Unemitted Transfer Event

As of August 10, 2018, we found 4604 contract codes that didn't reach the
standard of ERC20 and didn't trigger the Transfer event. 10 contracts with the
highest transaction volume are as follows:

![](https://images.seebug.org/content/images/2018/08/eb7cc870-39c6-4dd2-b812-65a247586b5e.png-w331s)

##### 2) Unemitted Approval Event

As of August 10, 2018, we found 4604 contract codes that didn't reach the
standard of ERC20 and didn't trigger the Approval event. 10 contracts with the
highest transaction volume are as follows:

![](https://images.seebug.org/content/images/2018/08/bdcbc41c-38bf-48dd-96ef-2ca446583116.png-w331s)

##### 3) Fake Recharge Vulnerability

On July 9, 2018, we scanned contract codes for the entire network when the
Knownsec 404 Blockchain Security Research Team followed and responded urgently
with the Fake Recharge Vulnerability. At that time, over 3141 contract codes
with fake recharge issue we were found. The 10 of them with the highest
transaction volume are as follows:

![](https://images.seebug.org/content/images/2018/08/be0be822-ea17-44eb-93de-b636496926e2.png-w331s)

As of August 10, 2018, over 5027 contract codes with fake recharge issue we
were found. The 10 of them with the highest transaction volume are as follows:

![](https://images.seebug.org/content/images/2018/08/5105a238-f377-4af4-8839-17642a770ba7.png-w331s)

##### 4) Writing Error of Constructed Function

  * Case Error

On June 22, 2018, the Knownsec 404 Blockchain Security Research Team followed
and responded urgently with the Fake Recharge Vulnerability, there are about
16 contracts with this problem in the whole network.

As of August 10, 2018, 90 contract codes with case error on the constructor we
were found. The 10 of them with the highest transaction volume are as follows:

![](https://images.seebug.org/content/images/2018/08/b1369bdc-51d1-4592-9c7d-735c791c4473.png-w331s)

  * Coding Error

As of August 10, 2018, 24 contract codes with writing error on the constructor
we found, only one more contract than the emergency response to this
vulnerability on July 14, 2018. 10 contracts with the highest transaction
volume are as follows:

![](https://images.seebug.org/content/images/2018/08/6890c76c-22bf-4de2-b45a-64b42a39cb8f.png-w331s)

#### 4\. Repair

##### 1) Transfer function trigger Transfer event

    
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_value <= balances[msg.sender]);
        require(_to != address(0));
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
      }

##### 2) Approve function trigger Approve event

    
    
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
      }

##### 3) Transfer balance verification should use require to throw an error

    
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_value <= balances[msg.sender]);
        require(_to != address(0));
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
      }

##### 4) The constructor should be consistent with the contract name before
the 0.4.22 version

    
    
    contract ownable {
        function ownable() public {
        owner = msg.sender;
      }

##### 5) The constructor should not be decorated with function after the
0.4.22 version.

    
    
    constructor() public {
            owner = msg.sender;
        }

#### 5\. Reflection

These questions are a type of problem that I often find in reviewing
historical vulnerabilities. They are caused by developers not complying with
the ERC20 standard. Because of these out-standard problems, many problems in
the maintenance of contract tokens will appear later. Although these will not
cause the emergence of contract vulnerabilities directly.

If not trigger the corresponding events on the transfer and approve function,
developers need more complicated ways to monitor contract transaction. There
are not even enough logs to provide a rollback once a large-scale stolen time
occurs.

The error that is not thrown at the time of transfer brings the fake recharge
vulnerability to occur. The platform benefits will be compromised if it's
judged by the transaction status when checks the transaction result.

If the developer does not pay attention to different versions of the compiler
standard when constructing the function, it may cause contract ownership can
be stolen easily, and further bring more serious problems such as the steal of
currency.

It's easy to find that there is a large number of developers have not noticed
these problems. When we scan and monitor the open contract code of the whole
network even low-level errors such as constructor writing errors are still
happening after the vulnerability warning. Considering that most of the
private contract code, there may still many developers develop without
complying on standards and there are many potential issues to consider.

In order to avoid unnecessary hassles and security issues, we recommend that
all developers review their contract code and check they comply with the REC20
contract standard whether or not.

#### 6\. Reference

[1] ERC standard  
<https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md>  
[2] Morpheus official announcement  
<https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91
b80dbc7655>[/https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91](mailto:/https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91)  
[3] Constructor writing problem vulnerability details  
<https://mp.weixin.qq.com/s/xPwhanev-cjHhc104Wmpug>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/670/>

