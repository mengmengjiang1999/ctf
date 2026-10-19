Author：Knownsec 404 Blockchain Security Research Team  
Date：2018/8/20  
Chinese version：<https://paper.seebug.org/673/>

#### 0x00 Introduction

August 01, 2018, the Knownsec 404 Blockchain Security Research Team has
published a paper(Exhilarating Coin, Maverick Thief - Various Coin Stolen
Tricks of Ethereum JSON-RPC Interface) which has introduced "Smuggling
Vulnerability" and "ether and tokens stealing in 'Post-Smuggling Era'". It has
revealed three ways of stealing: Offline Attack, Replay Attack, Blast Attack.

We also found a supplementary to these attacks in further research: Scavenging
Attacks. The attackers resort to the miner or have the computing power to get
the right to package the transaction into the block. They construct a
transaction with a gasPrice of 0 on an attacked node in the "Smuggling
Vulnerability", waiting for the users to unlock the signature account
broadcast. The attackers also set a malicious node to receive the transaction
and pack the qualified transactions to implement 0 gas transfer. Through this
kind of attack, they can obtain all the ether which are not enough or barely
enough to pay the fee on the node. And to a certain extent, it can prevent the
race of other attackers. It’s a paragon like "gathering wool".

In addition, after gathering enough residues of ether, the attackers stared at
the tokens in the accounts which had been stolen. Until now, some tokens in
the stolen accounts are still being attacked by "Scavenging Attacks" for
gathering small amount tokens.

This article will start with a 0 gas transaction, simulate and recurrent the
actual process of stolen currency and analyze the key points of the success of
scavenging attack.

#### 0x01 Starting with a 0 gas Transaction

In the blockchain system, each transaction should come with a portion of gas
and the corresponding gasPrice as a fee. This fee will be rewarded to the
miners who completed the package when the transaction is packaged into the
block.

In the "Exhilarating Coin, Maverick Thief - Various Coin Stolen Tricks of
Ethereum JSON-RPC Interface" we have mentioned an attacker account that uses
the Ethereum JSON-RPC interface
0x957cD4Ff9b3894FC78b5134A8DC72b032fFbC464.(<https://etherscan.io/address/0x957cD4Ff9b3894FC78b5134A8DC72b032fFbC464>)
The attackers scan the open RPC port on the public network and construct a
high-fee transaction request. Once the user unlocks his account, the balance
is transferred to the attackers’ account or the contract account created by
the attackers.

When analyzing the transaction information of the account, we found a
transaction that wasn’t in common sense. We can start with it.

The transaction address:

0xb1050b324f02e9a0112e0ec052b57013c16156301fa7c894ebf2f80ac351ac22
(<https://https://etherscan.io/tx/0xb1050b324f02e9a0112e0ec052b57013c16156301fa7c894ebf2f80ac351ac22>)

    
    
    Function: transfer(address _to, uint256 _value)
    
    MethodID: 0xa9059cbb
    [0]:  000000000000000000000000957cd4ff9b3894fc78b5134a8dc72b032ffbc464
    [1]:  000000000000000000000000000000000000000000000000000000000abe7d00

Although the transaction from 0x00a329c0648769a73afac7f9381e08fb43dbea72
(<https://etherscan.io/address/0x00a329c0648769a73afac7f9381e08fb43dbea72>) to
[Minereum
Token](https://etherscan.io/address/0x1a95b271b0535d15fa49932daba31ba612b52946
"Minereum Token")(the attacker’s contract) has a few user balance, the
transaction uses all the balance of the account as the value of interacting
with the contract. It uses a normal amount of gas, but the gasPrice is set to
0.

As mentioned above, the attackers will use a higher fee to ensure the success
of their transaction. The miners will sort the gasPrices of each transaction
in the txpool of this node in reverse order, and preferentially package the
high gasPrice transaction into the subsequent blocks. There are countless
transactions happening all the time in this world. The lowest gasPrice for a
transaction was 3Gwei on the last 7 days. How did this 0 gas transaction
happen and how it was packaged into the block?

#### 0X02 Ideas Analysis

In the blockchain system, anyone can join the blockchain network and become
one of the nodes, participating in keeping accounts, mining and other
operations. The core of the credibility and decentralization of the blockchain
is the consensus mechanism.

##### Consensus Mechanism

> In Ethereum, the miner packs the hash value of the previous block, the
> transaction with a high cost in txpool, the timestamp, etc., and
> continuously calculates the nonce to mine. The miner who first obtains the
> qualified nonce value will have the right to book, gets the fee and mining
> reward. The miner will broadcast the obtained block and it will be verified
> by the other nodes. If there is no error, the new block is considered to be
> generated and the blockchain height is increased. This is the process of
> each node generates a new block to maintain consensus.

There are two issues need to be confirmed to complete 0 gasPrice transactions.

  * Whether the miner will accept the transaction and package it.
  * Whether the remaining nodes reach a consensus on the block containing this transaction when it is received.

Next, we will test the operations related to the 0 gasPrice transactions.
Finding out how 0 gas transactions are generated, how they accepted by txpool,
whether the block that was packaged with the 0 gas transaction could be
recognized, and answer to the above question was confirmed.

#### 0x03 0 gas Transaction Test

##### a.Single Node Test

First, let's confirm whether the transaction can enter the node's txpool and
enable a test chain. Its default RPC port is 8545 and uses a python web3
package to initiate a 0 gasPrice transfer.

    
    
    geth --networkid 233 --nodiscover --verbosity 6 --ipcdisable --datadir data0 --rpc --rpcaddr 0.0.0.0 console

The first node initiates the transfer script and unlocks the accounts before
transferring the account.

    
    
    from web3 import Web3, HTTPProvider
    web3 = Web3(HTTPProvider("http://localhost:8545/"))
    
    print(web3.eth.accounts)
    # Unlock your account before transferring money
    web3.eth.sendTransaction({
        "from":web3.eth.accounts[0],
        "to":web3.eth.accounts[1],
        "value": 10,
        "gas":21000,
        "gasPrice":0,
    })

Interaction result

    
    
    > txpool.content
    {
      pending: {},
      queued: {}
    }
    > eth.getBalance(eth.accounts[0])
    800000000
    > personal.unlockAccount(eth.accounts[0],'sissel')
    true
    > INFO [08-14|11:20:14.972] Submitted transaction                    fullhash=0x72e81751d2517807cabad24102d3cc2f0f4f2e8b92f1f106f1ee0bf6be734fe4 recipient=0x92636b228148e2824cB8d472Ef2F4e76f2F5059C
    > txpool.content
    {
      pending: {
        0x092fda221a114FA702e2f59C217C92cfEB63f5AC: {
          3: {
            blockHash: "0x0000000000000000000000000000000000000000000000000000000000000000",
            blockNumber: null,
            from: "0x092fda221a114fa702e2f59c217c92cfeb63f5ac",
            gas: "0x5208",
            gasPrice: "0x0",
            hash: "0x72e81751d2517807cabad24102d3cc2f0f4f2e8b92f1f106f1ee0bf6be734fe4",
            input: "0x",
            nonce: "0x3",
            r: "0x1eca20e3f371ed387b35ca7d3220789399a3f64c449a825e0fa7423b96ce235c",
            s: "0x35a58e5cb5027c7903c1f1cc061ae846fb5150186ebbabb2b0766e4cbfc4aee6",
            to: "0x92636b228148e2824cb8d472ef2f4e76f2f5059c",
            transactionIndex: "0x0",
            v: "0x42",
            value: "0xa"
          }
        }
      },
      queued: {}
    }
    > miner.start(1)
    INFO [08-14|11:20:35.715] Updated mining threads                   threads=1
    INFO [08-14|11:20:35.716] Transaction pool price threshold updated price=18000000000
    null
    INFO [08-14|11:20:35.717] Starting mining operation
    > INFO [08-14|11:20:35.719] Commit new mining work                   number=115 txs=1 uncles=0 elapsed=223µs
    > mINFO [08-14|11:20:36.883] Successfully sealed new block            number=115 hash=ce2f34…210039
    INFO [08-14|11:20:36.885] ? block reached canonical chain          number=110 hash=2b9417…850c25
    INFO [08-14|11:20:36.886] ? mined potential block                  number=115 hash=ce2f34…210039
    INFO [08-14|11:20:36.885] Commit new mining work                   number=116 txs=0 uncles=0 elapsed=202µs
    > miner.stop()
    true
    > eth.getBalance(eth.accounts[0])
    799999990

The 0 gas transaction initiated by the first node is successful, and the
transaction is successfully packaged into the block after mining.

##### b.Multi-node Consensus test

Now let's join another node.

    
    
    geth  --datadir "./" --networkid 233 --rpc  --rpcaddr "localhost" --port 30304 --rpcport "8546" --rpcapi "db,eth,net,web3" --verbosity 6 --nodiscover console
    > admin.nodeInfo
    > admin.addPeer()
    > admin.peers

The first node still uses the script to initiate a 0 gas transaction, and its
txpool was successfully appended. But the second node illegally rejected the
transaction because of gasPrice.

    
    
    TRACE[08-15|10:09:24.682] Discarding invalid transaction           hash=3902af…49da03 err="transaction underpriced"
    
    > txpool.content
     []

We found the parameters related to this in the configuration of the geth.

    
    
    --txpool.pricelimit value    Minimum gas price limit to enforce for acceptance into the pool (default: 1)

Change it to 0 when it starts, but the transaction still does not appear in
the txpool of the second node.

![](https://images.seebug.org/content/images/2018/08/c4a1920a-8ede-41fb-b098-791298c8eb2c.png-w331s)

We can know from the source code, this parameter is the lowest gasPrice of the
transaction to control the increasing txpool, but cannot be less than 1.

    
    
    if conf.PriceLimit < 1 {
        log.Warn("Sanitizing invalid txpool price limit", "provided", conf.PriceLimit, "updated", DefaultTxPoolConfig.PriceLimit)
        conf.PriceLimit = DefaultTxPoolConfig.PriceLimit
    }

The first node began mining. After the transaction was packaged into the
block, it was found that the second node recognized the block and reached a
consensus. Both of the nodes increased in height.

Conclusion:

  * Normally only the initiators' txpool can receive the 0 gas transaction. The remaining nodes cannot pass and synchronize the transaction. If necessary, the source code of geth must be modified and other operations.
  * Although the transaction cannot enter the txpool of other nodes, a consensus can be reached for the block containing this transaction.

We will conduct a brief source code analysis to support our conclusions.

#### 0x04 Source Code Analysis

(The following code analysis is based on the current latest submission at
<https://github.com/ethereum/go-ethereum> : commit
6d1e292eefa70b5cb76cd03ff61fc6c4550d7c36）

At present, the most popular node(Geth / Prity) program in Etherenum provides
RPC API for docking pools, wallets, and other third-party programs. First,
confirm the implementation of the code when the node is packing txs.

##### i.Trading Pool

Code path: ./go-ethereum/core/tx_pool.go

    
    
    // TxPool contains all currently known transactions. Transactions
    // enter the pool when they are received from the network or submitted
    // locally. They exit the pool when they are included in the blockchain.
    type TxPool struct {
        config       TxPoolConfig
        chainconfig  *params.ChainConfig
        chain        blockChain
        gasPrice     *big.Int             //Lowest GasPrice limit
        /*
            other parameters
        */
    }

It has found that there is a minimum requirement for gasPrice When generating
a txt instance. Specifically in this function will refuse to receive this
transaction.

    
    
    // validateTx checks whether a transaction is valid according to the consensus
    // rules and adheres to some heuristic limits of the local node (price and size).
    func (pool *TxPool) validateTx(tx *types.Transaction, local bool) error {
    
        // Verification of gasPrice
        if !local && pool.gasPrice.Cmp(tx.GasPrice()) > 0 {
            return ErrUnderpriced
        }
    
        /*
           ...
        */
    
        return nil
    }

##### ii.Removing Transactions Below the Threshold

Code path: ./go-ethereum/core/tx_list.go And it will delete the transaction
below the threshold in the processing txs, but the local transaction will not
be deleted.

    
    
    // Cap finds all the transactions below the given price threshold, drops them
    // from the priced list and returs them for further removal from the entire pool.
    func (l *txPricedList) Cap(threshold *big.Int, local *accountSet) types.Transactions {
        drop := make(types.Transactions, 0, 128) // Remote underpriced transactions to drop
        save := make(types.Transactions, 0, 64)  // Local underpriced transactions to keep
    
        for len(*l.items) > 0 {
            // Discard stale transactions if found during cleanup
            tx := heap.Pop(l.items).(*types.Transaction)
            if _, ok := (*l.all)[tx.Hash()]; !ok {
                // Update the states counter if one has been found deleted.
                l.stales--                continue
            }
            // Stop the discards if we've reached the threshold
            if tx.GasPrice().Cmp(threshold) >= 0 {
                // Exit if the price is above the threshold.
                save = append(save, tx)
                break
            }
            // Non stale transaction found, discard unless local
            if local.containsTx(tx) {  //The local transactions will not be deleted.
                save = append(save, tx)
            } else {
                drop = append(drop, tx)
            }
        }
        for _, tx := range save {
            heap.Push(l.items, tx)
        }
        return drop
    }

The above section is a node within the blockchain network and there are
partial filtering or rule restrictions when attempting to receive or join a
transaction with 0 gasPrice. But we can still legally add the 0 gasPrice
transactions to the block by modifying the source code, and perform the nonce
subsequent calculation. Next, we continue to analyze the source code to
investigate whether the block obtained by this method can be accepted by other
nodes and reach a consensus.

##### iii.Consensus checking

Code path: ./go-ethereum/consensus/consensus.go This is the consensus
algorithm engine interface provided in the geth.

    
    
    type Engine interface {
        // signature
        Author(header *types.Header) (common.Address, error)
    
        /*
           Verify the header, seal, processing difficulty and other functions
           ...
        */
    
        // Pre-processing block header information, modification difficulty, etc.
        Prepare(chain ChainReader, header *types.Header) error
    
        // Blocks rewards, etc. And something after mining out the block.
        Finalize(chain ChainReader, header *types.Header, state *state.StateDB, txs []*types.Transaction,
            uncles []*types.Header, receipts []*types.Receipt) (*types.Block, error)
    
        // Calculate nonce, exit if a higher chain is received.
        Seal(chain ChainReader, block *types.Block, stop <-chan struct{}) (*types.Block, error)
    
        // Calculate the difficulty value
        CalcDifficulty(chain ChainReader, time uint64, parent *types.Header) *big.Int
    
        // APIs returns the RPC APIs this consensus engine provides.
        APIs(chain ChainReader) []rpc.API
    
        // Close terminates any background threads maintained by the consensus engine.
        Close() error
    }

By looking at VerifySeal() we found that the following was verified:

  * Special treatments in different modes
  * Legality of difficulty
  * Legality of nonce values
  * Legality of gas values

It can be seen that other nodes check the signature, nonce and other content
for the consensus. The 0 gas transactions are not checked. In other words, the
0 gas transactions cannot motivate miners but still legal.

#### 0x05 Utilization Process

First, the attackers construct 0 gas and a normal transfer transaction with
the way that exploited by smuggling vulnerability. After users unlock the
account, broadcast the transactions. The specific process is as follows:

![](https://images.seebug.org/content/images/2018/08/68ce9e0f-16b7-4087-8ad4-eb46c845f47c.png-w331s)

#### 0x06 Summary

From a special transaction like h0 gasPrice we can draw the following
conclusions:

  * Normally, 0 gasPrice can be initiated by the node itself to join txpool.
  * Take geth as an example, modify the partial source code of geth to recompile and run, the node can accept special transactions issued by other nodes (target account initiated 0 gasPrice transactions). This is what the attackers need to do.
  * 0 GasPrice transactions can be packaged into blocks and meet consensus requirements.

By collecting such 0 gasPrice transactions and adding them to partial miners'
txpools, such transactions will also be packaged when the miner digs up a new
block. The attacker may cooperate with some miners or have a certain computing
power so that the miners no longer follow the principle of honest mining and
maintenance blockchain system.

#### 0x07 Utilization Value and Defense Plan

The emergence of 0 gas transactions brings significance to many low-yield
attacks.

##### Improving Profits

In this way, the attacker can transfer all the balances in the attacked
account in combination with other attack methods to maximize the revenue.

##### Wools Exhausted

According to the attack method in "Exhilarating Coin, Maverick Thief - Various
Coin Stolen Tricks of Ethereum JSON-RPC Interface", in the case of the less
account balance or insufficient to pay the transfer fee, the residues in the
account can be transferred to the wallet through the above-mentioned attack
scheme for "gathering wool". Because the gasPrice of this transaction is 0,
multiple transactions of this type can be packaged in one block at the same
time, such as multiple sets of transactions under this contract:
[0x1a95b271b0535d15fa49932daba31ba612b52946](https://etherscan.io/address/0x1a95b271b0535d15fa49932daba31ba612b52946
"0x1a95b271b0535d15fa49932daba31ba612b52946"). Several transactions in this
block: [4788940](https://etherscan.io/txs?block=4788940&p=6 "4788940")

![](https://images.seebug.org/content/images/2018/08/6c031cf1-6de0-4d02-bde7-0083e87e51c0.png-w331s)

##### Smuggling Tokens

The attacker found that some of the smart contract tokens still existed in
these accounts in the absence of ether currency in the stolen accounts.
Without Ethereum, you can't pay gas for transfer. And 0 gas transactions can
solve this problem perfectly. Until now, many attacked accounts without ether
currency are transferred tokens in this way.

##### Defense Plan

Because the 0 gasPrice transactions are only used to extend other attack
schemes, the defense should also be utilized on the previous json-rpc
interface.

  * For those nodes who have been attacked by the smuggling vulnerability, it is recommended to transfer the assets of the relevant account on the node to the new account and discard the accounts that may have been attacked.
  * We advise users not to use weak passwords as account passwords. If that has happened, you can crack the private key content according to the contents at the end of section 1.2, and then import the private key again via the geth account import command and set a strong password.
  * It is recommended that there is no private key file on the node if the node does not need to perform operations such as signature transfer. And if you need to transfer, be sure to use the personal_sendTransaction interface instead of the personal_unlockAccount interface.

#### 0x08 Impact Scale

We started with the 0 gasPrice transactions mentioned above. The survey found
that there are still many transactions traded through 0 gasPrice recently.
Most 0 gas transactions are from the mining pool:
[0xb75d1e62b10e4ba91315c4aa3facc536f8a922f5](https://etherscan.io/address/0xb75d1e62b10e4ba91315c4aa3facc536f8a922f5
"0xb75d1e62b10e4ba91315c4aa3facc536f8a922f5") and
[0x52e44f279f4203dcf680395379e5f9990a69f13c](https://etherscan.io/address/0x52e44f279f4203dcf680395379e5f9990a69f13c
"0x52e44f279f4203dcf680395379e5f9990a69f13c"), such as
[6161214](https://etherscan.io/block/6161214 "6161214"),
[6160889](https://etherscan.io/block/6160889 "6160889").

We noticed that only had a small number of early 0 gasPrice transactions
carrying little ether, which is in line with our expectations for the
characteristics of the gathering wool. According to statistics, there have
been 748 accounts since June 2017, and a total of 24.2eth was transferred by 0
gas.

And the replay attack mentioned was also found, resulting in account losses:
[0x682bd7426ab7c7b4b5beed331d5f82e1cf2cecc83c317ccee6b4c4f1ae34d909](https://etherscan.io/tx/0x682bd7426ab7c7b4b5beed331d5f82e1cf2cecc83c317ccee6b4c4f1ae34d909
"0x682bd7426ab7c7b4b5beed331d5f82e1cf2cecc83c317ccee6b4c4f1ae34d909")

![](https://images.seebug.org/content/images/2018/08/28ee7608-9d17-48c2-b00d-69de2566f4db.png-w331s)

Lost 0.05eth

![](https://images.seebug.org/content/images/2018/08/47edbc18-66f6-4e53-8024-c4fbd4e9a5f9.png-w331s)

Most of these 0 gasPrices are transfer requests for the
[TOKEN](https://etherscan.io/token/0x1a95b271b0535d15fa49932daba31ba612b52946
"TOKEN") issued by [the
contract](https://etherscan.io/address/0x1a95b271b0535d15fa49932daba31ba612b52946
"the contract"), transferring the tokens in the user's account to [the
contract owner's
account](https://etherscan.io/address/0xe386e3372e3d316ae063af50c38704ec6fba5149
"the contract owner's account"), for example:

![](https://images.seebug.org/content/images/2018/08/7a766314-2b8b-420e-a111-cb6c542df762.png-w331s)

Tx records for this account:

![](https://images.seebug.org/content/images/2018/08/59745b1c-27e8-4b18-92ee-1448ff080308.png-w331s)

The attackers have the computing power of multiple mining pools and transfer a
variety of tokens owned by many attacked accounts to the corresponding
accounts. Although the amount of a single transaction is small, there are more
accounts and contracts that can be used for such attacks and no fee is
required. Many a little make a mickle. The attackers are still carrying out
scavenging attacks on these tokens.

#### 0x09 Conclusion

The premise of the blockchain system based on decentralization to reach a
consensus on the transaction is that the vast majority of miners will maintain
the entire bitcoin system through honest mining. When the miners are no longer
honest, the credibility and decentralization of the blockchain will be greatly
reduced. When a hacker cooperates with a miner or has the computing power to
become a miner, it will provide more extended attack schemes based on existing
attack techniques. The emergence of the 0 gasPrice transactions violates the
original intention of the blockchain design, that is, the miners should pay
the fee as an incentive.

The popularity of blockchain technology and the virtual currency have given
the currency a huge economic value and everyone wants to get a little benefit
in the blockchain wave. Especially hackers. As a currency thief, they racked
their brains to attack blockchains and contracts from all angles. When hackers
live in miners, they cannot only dig out blocks but also dig out
vulnerabilities.

#### Reference

  1. Stolen tricks of the json-rpc interface: [Exhilarating Coin, Maverick Thief - Various Coin Stolen Tricks of Ethereum JSON-RPC Interface](https://paper.seebug.org/656/ "Exhilarating Coin, Maverick Thief - Various Coin Stolen Tricks of Ethereum JSON-RPC Interface")

  2. https://www.reddit.com/r/ethereum/comments/7lx1do/a_christmas_mystery_sweepers_and_zero_gas_price/

  3. [how-to-create-your-own-private-ethereum-blockchain-dad6af82fc9f](https://medium.com/mercuryprotocol/how-to-create-your-own-private-ethereum-blockchain-dad6af82fc9f "how-to-create-your-own-private-ethereum-blockchain-dad6af82fc9f")

  4. 0 gas transaction: <https://etherscan.io/tx/0xb1050b324f02e9a0112e0ec052b57013c16156301fa7c894ebf2f80ac351ac22>

  5. <https://mp.weixin.qq.com/s/Kk2lsoQ1679Gda56Ec-zJg>

  6. <https://paper.seebug.org/547/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/687/>

