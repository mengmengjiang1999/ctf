## 背景介绍

2020年无疑是多灾多难的一年，虽然时间目前只过去了四分之一。但借着“新冠肺炎”各种衍生的自然灾难、人为灾难接踵而至。

近期奇安信病毒响应中心在日常监测中，发现了一种新的移动银行木马Eventbot，其最早可以追溯到2020年3月1日。Eventbot使用了全新的代码结构，与目前已知的银行木马完全不同。经过分析我们发现Eventbot目前可能只是处于测试阶段，其繁琐的功能以及影响的金融应用众多。目前其主要针对欧洲一些国家的银行应用、一些加密货币钱包应用等共234个
**（见附录）** 。

Eventbot样本信息：目前发现的样本，其都使用相同的包名com.example.eventbot，代码功能也不够完善，并且代码并没有经过混淆加密处理，因此我们推断其正处于测试阶段。根据我们对样本的溯源，发现其最早出现在2020年3月1日。

![图片.png](https://image.3001.net/images/20200325/1585104387_5e7ac603a51c0.png!small)

## 样本分析

Eventbot其功能繁多，相比于近期比较活跃的Cerberus、Anubis、Joker等毫不逊色。

### 样本信息

**应用名** |  **Flash Update**  
---|---  
**包名** |  com.example.eventbot  
**MD5** |  F73F66B15791A42DAC86D0CED46D660F  
**图标** |
![图片.png](https://image.3001.net/images/20200325/1585104395_5e7ac60bed4cf.png!small)  
  
运行截图：

![图片.png](https://image.3001.net/images/20200325/1585104400_5e7ac61086207.png!small)

### 样本功能

Eventbot木马通过仿冒正常应用图标诱骗用户安装使用，其运行以后会通过仿冒升级更新，隐藏自身图标达到保护自身。Eventbot木马通过Accessibility
Service功能实施对用户手机的监控，恶意功能多达50多种。其运行后会通过服务端下发指令，实施对用户手机的操控，例如：获取并上传用户手机短信，获取并上传用户手机配置信息，获取并上传用户手机已安装应用，对用户手机浏览器进行注入，启动用户手机指定APP，删除指定应用，更新恶意插件等恶意行为。

### 代码分析

获取C2：

![图片.png](https://image.3001.net/images/20200325/1585104413_5e7ac61d1e2f3.png!small)![图片.png](https://image.3001.net/images/20200325/1585104417_5e7ac62168f7f.png!small)

通过服务端下发指令：

![图片.png](https://image.3001.net/images/20200325/1585104424_5e7ac6282fff1.png!small)

获取并上传用户手机短信：

![图片.png](https://image.3001.net/images/20200325/1585104432_5e7ac630b7752.png!small)

操控用户手机：

![图片.png](https://image.3001.net/images/20200325/1585104437_5e7ac63533728.png!small)

上传用户信息：

![图片.png](https://image.3001.net/images/20200325/1585104442_5e7ac63a50556.png!small)

数据包：

![图片.png](https://image.3001.net/images/20200325/1585104446_5e7ac63ec6f81.png!small)

## 影响分析

Eventbot主要以金融行业为目标，通过分析我们发现目前其影响了英国、德国、意大利、西班牙等国的十来家银行APP，总共影响234个金融APP，尤其以虚拟货币交易平台为主。

Eventbot仿冒的主要图标：

![图片.png](https://image.3001.net/images/20200325/1585104451_5e7ac6432deb5.png!small)

Eventbot影响的金融行业APP图标举例：

![图片.png](https://image.3001.net/images/20200325/1585104455_5e7ac64727d6d.png!small)

从中我们可以看到，Eventbot主要以虚拟货币交易平台为主要目标，虽然国内早已经关闭了虚拟货币的交易，但依然有很多人通过“科学上网”，通过一些虚拟货币交易平台在进行买卖，其中很大一部分平台APP在Eventbot的目标之中，这些无疑增加了国内用户手机中招的概率。

## 总结

进入2020年以后，Android银行木马随着“新冠肺炎”的爆发变得异常活跃，继Cerberus、Anubis木马之后，又出现了全新的木马Eventbot。虽然目前Eventbot木马只是处于测试阶段，实质性的危害还没有扩大，但其潜在的影响广泛，对国内一些进行虚拟货币交易的用户具有潜在的威胁。奇安信病毒响应中心会随时关注相关木马的实时动态，同时奇安信病毒响应中心提醒用户不要安装未知来源的APP，同时提高个人的安全意识。

目前奇安信威胁情报中心文件深度分析平台：（[https://sandbox.ti.qianxin.com/sandbox/page](https://sandbox.ti.qianxin.com/sandbox/page)）已支持Android样本分析：

![图片.png](https://image.3001.net/images/20200325/1585104463_5e7ac64fa7848.png!small)

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## IOC

文件MD5：

7107AC3BCCD8DB274B21F0E494E3ECCC

8A563B6AF3CF74C8CBB88B99E104D949

F73F66B15791A42DAC86D0CED46D660F

7F5D728119951839B46895808107B281

B3F4746A6C21D030D2B73FF2AC3CEC2F

66AE6BB78ED76B252C2EA6EC8072B0E8

664118A72533D9A0D60E9CABA439FE28

E1229D332CA43AC2B640084A0DAE9BBE

8793359481AB88914B5E60625F57277C

36988753860CD9F919B9D2A94C0AF0FC

C2:

<http://themoil.site/gate_cb8a5aea1ab302f0_c>

<http://ora.carlaarrabitoarchitetto.com/gate_cb8a5aea1ab302f0_c>

[http://ora.studiolegalebasili.com/gate_cb8a5aea1ab302f0_c](http://ora.studiolegalebasili.com/gate_cb8a5aea1ab302f0_c)

## 附录

受影响的234家金融机构应用包名：

**包名** **** |  **包名** **** |  **包名** **列3**  
---|---|---  
**com.ownrwallet.wallet** |  mobi.societegenerale.mobile.lappli |
doge.org.freewallet.app  
**com.aurigaspa.bancadalba** |  it.csebo.fec3mobileProd05772 |
it.relaxbanking  
**es.lacaixa.mobile.android.newwapicon** |  com.intesasanpaolo.inbiz |
com.revolut.revolut  
**com.tabtrader.android** |  com.sella.BancaSella |  ftb.ibank.android  
**it.creval.bancaperta** |  com.opentecheng.android.webank |  com.wirex  
**com.plutus.wallet** |  com.kutxabank.android |  it.cedacri.hb3.crasti  
**com.grppl.android.shell.BOS** |  com.latuabancaperandroid.ispb |
com.fideuram.phone  
**com.cryptotab.android** |  com.cryptoviewer |  com.coinmarketcap.android  
**com.mansoon.cryptopop** |  io.cex.app.prod |  com.latuabancaperandroid  
**com.jhapps.easyfaucetclaimer** |  it.csebo.fec3mobileProd06150 |
com.avuscapital.trading212  
**cedacri.mobile.bank.crbolzano** |  btg.org.freewallet.app |
clientapp.swiftcom.org  
**it.bnl.apps.enterprise.hellobank** |  com.payeer |
it.gruppobper.ams.android.bper  
**ch.postfinance.android** |  com.conio.wallet |  app.pay98  
**co.mona.android** |  it.bnl.apps.banking |  cash.usdx.wallet  
**com.chlegou.bitbot** |  com.pundix.xwallet |  net.bitbay.bitcoin  
**com.paytomat** |  com.coinninja.coinkeeper |
com.mediolanum.android.fullbanca  
**it.csebo.fec3mobileProd05156** |  com.beeweeb.findomestic |
com.mercuryo.app  
**it.cedacri.hb3.crcento** |  it.bper.mobile.mymoney |  com.mycelium.wallet  
**it.archie.ccbcarteprepagate** |  com.cryptonator.android |
uk.co.tsb.businessmobilebank  
**com.paxful.wallet** |  cedacri.mobile.bank.bppb |  com.bitpanda.bitpanda  
**de.postbank.finanzassistent** |  it.bnl.apps.banking.privatebnl |
mw.org.freewallet.app  
**com.caisseepargne.android.mobilebanking** |  io.bluewallet.bluewallet |
com.lloyds.ccdm  
**com.fullsix.android.labanquepostale.accountaccess** |
uk.co.cumberland.banking.pay2mobile |  com.wavesplatform.wallet  
**uk.co.metrobankonline.mobile.android.production** |
com.grppl.android.shell.halifax |  com.illimity.mobile.rtl  
**com.arkea.android.application.cmb** |  com.tideplatform.banking |
com.eofinance  
**io.eidoo.wallet.prodnet** |  io.kriptomat.app |  com.enjin.mobile.wallet  
**it.popso.SCRIGNOapp** |  com.crypterium |  com.bitnovo.app  
**com.todo1.mobile.deleteTHIS3** |  lt.lemonlabs.android.paysera |
com.starfinanz.smob.android.sfinanzstatus  
**co.uk.getmondo** |  it.csebo.fec3mobileProd05652 |  com.unicredit  
**com.bbva.netcash** |  com.citibank.mobile.au |
com.ie.vanquis.interact.shell  
**com.crypto.currency** |  it.chiantibanca.inbank |
com.swissborg.android.community  
**it.hype.app** |  com.lloydsbank.businessmobile |  com.binance.dev  
**de.schildbach.wallet** |  it.cedacri.hb2.bpbari |  com.bankofqueensland.boq  
**com.ecoPayz.appID** |  com.libertex.mobile |  at.volksbank.volksbankmobile  
**com.tmobtech.halkbank** |  com.moneybookers.skrillpayments |
com.lynxspa.bancopopolare  
**com.tforp.cryptogdx** |  com.mal.saul.coinmarketcap |  com.plunien.poloniex  
**com.db.pbc.miabanca** |  io.getdelta.android |  com.wallet.crypto.trustapp  
**com.spot.spot** |  com.starlingbank.android |
com.db.coo.secureauthenticator  
**com.dowallet** |  com.liberty.jaxx |
com.barclays.android.barclaysmobilebanking  
**com.bitcoin.mwallet** |  com.developerdesing.bitcoin |  fcabank.myfcabank  
**it.icbpi.mobile** |  ltcc.org.freewallet.app |  co.edgesecure.app  
**uk.co.hsbc.hsbcukmobilebanking** |  it.bnl.mybiz |  com.coinbase.android  
**com.swftcoin.client.android** |  com.aci.ocean.mobile |
com.mosync.app_Banco_Galicia  
**com.monitise.client.android.yorkshire** |  com.coinstats.crypto.portfolio |
at.paysafecard.android  
**im.token.app** |  quarecy.crypto |  com.magnum.wallet  
**fr.banquepopulaire.cyberplus** |
com.tarjetanaranja.emisor.serviciosClientes.appTitulares |
it.cabel.mito.mimo.android  
**com.vipera.chebanca** |  com.touchin.perfectmoney |
cloud.money.server.mining  
**co.bitx.android.wallet** |  com.garanti.cepsubesi |  com.ptpwallet  
**com.interactive_crypto.app** |  com.monitise.client.android.clydesdale |
io.atomicwallet  
**net.inverline.bancosabadell.officelocator.android** |  com.cointiply.earn |
com.electroneum.mobile  
**uk.co.tsb.newmobilebank** |  com.polehin.android |  net.bitstamp.app  
**hashengineering.darkcoin.wallet** |  uk.co.santander.santanderUK |
com.syndicomsolutions.ecoinia  
**com.thanksmister.bitcoin.localtrader** |  eth.org.freewallet.app |
com.altcoinfantasy.altcoinfantasy  
**com.bitpie** |  com.kbc.mobilebanking |  uk.co.bankofscotland.businessbank  
**it.ingdirect.app** |  pl.bzwbk.bzwbk24 |  com.tescobank.mobile  
**ch.raiffeisen.android** |  com.coinomi.wallet |  de.number26.android  
**com.ocito.cdn.activity.banquenuger** |  it.nogood.container |
com.cajaingenieros.android.bancamovil  
**com.supercrypto.cryptocyrrency** |  com.jdevelops.claimmultifaucet |
com.moneybookers.skrillpayments.neteller  
**es.ibercaja.ibercajaapp** |  com.bitrue.currency.exchange |
lt.spectrofinance.spectrocoin.android.wallet  
**com.grppl.android.shell.CMBlloydsTSB73** |  com.monitise.coop |
exodusmovement.exodus  
**com.bancsabadell.wallet** |  com.Plus500 |  app.wizink.es  
**org.toshi** |  btc.org.freewallet.app |  com.csg.cs.dnmb  
**it.copergmps.rt.pf.android.sp.bmps** |  piuk.blockchain.android |  com.xapo  
**com.ie.capitalone.uk** |  es.ceca.cajalnet |  com.commbank.netbank  
**com.myetherwallet.mewconnect** |  com.advantage.RaiffeisenBank |
com.mediaengine.allianzbank  
**com.romerock.apps.utilities.cryptocurrencyconverter** |
it.bancagenerali.mobile |  com.barclays.bca  
**com.blockfolio.blockfolio** |  au.com.heritage.app |  com.tronwallet2  
**it.gruppocariparma.nowbanking** |  com.niyo.global |  com.remitano.remitano  
**it.cartasi.mobilepos** |  com.twogetherbank.app |  com.bbva.bbvacontigo  
**com.quppy** |  com.bitpay.wallet |  com.bankinter.launcher  
**cobo.wallet** |  co.uk.mycashplus.maapp |  aib.ibank.android  
**com.barclaycard.germany** |  io.totalcoin.wallet |  network.celsius.wallet  
**com.latuabancaperandroid.pg** |  com.payoneer.android |
com.crypter.cryptocyrrency  
**com.changelly.app** |  it.phoenixspa.inbank |  it.volksbank.android  
**posteitaliane.posteapp.appbpol** |  com.mirlimited.muchbetter |
de.commerzbanking.mobil  
**crypto.aliens.bch** |  com.monese.monese.live |
cedacri.mobile.bank.hb2.bari  
**com.CredemMobile** |  com.cmcm.blockchain.bitcoin.ethereum.safewallet |
com.wrx.wazirx  
**com.coingecko.coingeckoapp** |  it.iwbank.banking |  com.nexowallet

