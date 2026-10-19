在之前的文章中，我们已经讨论了`AD`森林的安装和`AD`基础知识。在这篇文章中，让我们开始使用
`AD`对象（如用户对象、计算机对象、组对象、网络共享等）填充 `AD`环境，以及计算机如何加入域。

## 1、添加用户对象

可以使用`GUI`、`cmd`、`PowerShell`创建新用户，也可以使用脚本创建批量用户。

### 1.1 、从Active Directory用户和计算机控制台创建用户对象

从服务器管理器面板-工具-Active Directory 用户和计算机打开控制台（或者在运行中输入`dsa.msc`打开它）

![1686720520_648950082eca9f746f068.png!small?1686720521153](https://image.3001.net/images/20230614/1686720520_648950082eca9f746f068.png!small?1686720521153)

![1686720533_648950157aa09314b7caa.png!small?1686720534164](https://image.3001.net/images/20230614/1686720533_648950157aa09314b7caa.png!small?1686720534164)

点击对应的域，在`Users`容器上右键-选择`新建-用户`

![1686720546_648950224de14648ab474.png!small?1686720547338](https://image.3001.net/images/20230614/1686720546_648950224de14648ab474.png!small?1686720547338)

填写用户的姓、名、和登录名

![1686720557_6489502d495f7e2d15fef.png!small?1686720558340](https://image.3001.net/images/20230614/1686720557_6489502d495f7e2d15fef.png!small?1686720558340)

然后点下一步，设置用户的密码

![1686720568_64895038d40da43807dab.png!small?1686720569604](https://image.3001.net/images/20230614/1686720568_64895038d40da43807dab.png!small?1686720569604)

点下一步，确定无误后点完成。

![1686720581_648950457bf7e540c51cc.png!small?1686720582252](https://image.3001.net/images/20230614/1686720581_648950457bf7e540c51cc.png!small?1686720582252)

### 1.2 使用 CMD 或 Powershell 创建用户对象

使用命令提示符，我们可以使用 `net user`实用程序创建用户。

    
    
    C:\Users\Administrator>net user aduser2 Pass@123 /add /domain
    

使用`Powerhell`，我们可以使用`New-ADUser cmdlet`创建一个用户。

    
    
    PS C:\> New-ADUser -Name "aduser3" -GivenName AD -Surname User -SamAccountName aduser3 -UserPrincipalName aduser3@pentest.com -AccountPassword (ConvertTo-SecureString Password@123 -AsPlainText -Force) -PassThru
    
    

![1686720607_6489505fe3820b2a276fb.png!small?1686720608957](https://image.3001.net/images/20230614/1686720607_6489505fe3820b2a276fb.png!small?1686720608957)

现在用户账户已经创建，使用`Enable-ADAccount cmdlet`启用它。

    
    
    PS C:\> Enable-ADAccount aduser3
    

![1686720619_6489506b7063f6255495d.png!small?1686720620246](https://image.3001.net/images/20230614/1686720619_6489506b7063f6255495d.png!small?1686720620246)

使用`Powershell`批量创建用户对象。

创建一个具有随机名称的用户数组。从这里获取随机名称列表并创建一个小的随机名称数组。

    
    
    $UserNames = @('Michael', 'Christopher', 'Jessica', 'Matthew', 'Ashley', 'Jennifer', 'Joshua', 'Amanda', 'Daniel', 'David', 'James', 'Robert', 'John', 'Joseph', 'Andrew', 'Ryan', 'Brandon', 'Jason', 'Justin', 'Sarah', 'William', 'Jonathan', 'Stephanie', 'Brian', 'Nicole', 'Nicholas', 'Anthony', 'Heather', 'Eric', 'Elizabeth', 'Adam', 'Megan', 'Melissa', 'Kevin', 'Steven', 'Thomas', 'Timothy', 'Christina', 'Kyle', 'Rachel', 'Laura', 'Lauren', 'Amber', 'Brittany', 'Danielle', 'Richard', 'Kimberly', 'Jeffrey', 'Amy', 'Crystal', 'Michelle', 'Tiffany', 'Jeremy', 'Benjamin', 'Mark', 'Emily', 'Aaron', 'Charles', 'Rebecca', 'Jacob', 'Stephen', 'Patrick', 'Sean', 'Erin', 'Zachary', 'Jamie', 'Kelly', 'Samantha', 'Nathan', 'Sara', 'Dustin', 'Paul', 'Angela', 'Tyler', 'Scott', 'Katherine', 'Andrea', 'Gregory', 'Erica', 'Mary', 'Travis', 'Lisa', 'Kenneth', 'Bryan', 'Lindsey', 'Kristen', 'Jose', 'Alexander', 'Jesse', 'Katie', 'Lindsay', 'Shannon', 'Vanessa', 'Courtney', 'Christine', 'Alicia', 'Cody', 'Allison', 'Bradley', 'Samuel', 'Shawn', 'April', 'Derek', 'Kathryn', 'Kristin', 'Chad', 'Jenna', 'Tara', 'Maria', 'Krystal', 'Jared', 'Anna', 'Edward', 'Julie', 'Peter', 'Holly', 'Marcus', 'Kristina', 'Natalie', 'Jordan', 'Victoria', 'Jacqueline', 'Corey', 'Keith', 'Monica', 'Juan', 'Donald', 'Cassandra', 'Meghan', 'Joel', 'Shane', 'Phillip', 'Patricia', 'Brett', 'Ronald', 'Catherine', 'George', 'Antonio', 'Cynthia', 'Stacy', 'Kathleen', 'Raymond', 'Carlos', 'Brandi', 'Douglas', 'Nathaniel', 'Ian', 'Craig', 'Brandy', 'Alex', 'Valerie', 'Veronica', 'Cory', 'Whitney', 'Gary', 'Derrick', 'Philip', 'Luis', 'Diana', 'Chelsea', 'Leslie', 'Caitlin', 'Leah', 'Natasha', 'Erika', 'Casey', 'Latoya', 'Erik', 'Dana', 'Victor', 'Brent', 'Dominique', 'Frank', 'Brittney', 'Evan', 'Gabriel', 'Julia', 'Candice', 'Karen', 'Melanie', 'Adrian', 'Stacey', 'Margaret', 'Sheena', 'Wesley', 'Vincent', 'Alexandra', 'Katrina', 'Bethany', 'Nichole', 'Larry', 'Jeffery', 'Curtis', 'Carrie', 'Todd');
    

然后创建一个小函数，它将接受要创建的用户账户的限制，并通过这些用户名进行循环，使用`New-ADUser
cmdlet`通过从全局变量（如域名、密码等）向它传递附加参数来创建随机用户。

    
    
    for ($i=1; $i -le $UsersLimit; $i=$i+1 ) {
            $firstname = (Get-Random -InputObject $UserNames);
            $lastname = (Get-Random -InputObject $UserNames);
            $fullname = "{0} {1}" -f ($firstname , $lastname);
            $SamAccountName = ("{0}.{1}" -f ($firstname, $lastname)).ToLower();
            $principalname = "{0}.{1}" -f ($firstname, $lastname);
            if($SamAccountName.Length -le 20){
                try { 
                    Write-Host "Creating user object: $SamAccountName" -ForegroundColor 'Gray'; 
                    New-ADUser -Name "$firstname $lastname" -GivenName $firstname -Surname $lastname -SamAccountName $SamAccountName -UserPrincipalName $principalname@$Global:Domain -AccountPassword (ConvertTo-SecureString $Global:default_password -AsPlainText -Force) -PassThru | Enable-ADAccount
                } catch { 
                    Write-Host "Error creating user object: $SamAccountName" -ForegroundColor 'Red'
                }
            }
        }
    

由于`Active Directory`中用户名的最大长度限制为`20`，所以我们要检查用户名的长度`if($SamAccountName.Length
-le 20)`然后尝试创建用户，以避免创建用户时出错。

然后就可以批量创建用户了，你也可以通过向`New-ADUser cmdlet`传递额外的参数来设置标题、部门等属性，使用户账户看起来更真实。

    
    
    PS C:\Scripts> Invoke-LoadADObjects -DomainName rootdse.org -LimitUsers 15
    
    [+] Creating Bulk Domain Users in rootdse.org
    Creating user object: katie.courtney
    Creating user object: danielle.latoya
    Creating user object: craig.laura
    Creating user object: aaron.anna
    Creating user object: rebecca.julia
    Creating user object: catherine.candice
    Creating user object: jesse.todd
    Creating user object: william.jessica
    Creating user object: nicholas.april
    Creating user object: christopher.meghan
    Creating user object: whitney.ronald
    Creating user object: derek.jennifer
    Creating user object: charles.carlos
    Creating user object: catherine.joel
    Creating user object: sarah.cassandra
    [+] Bulk User objects creation completed.
    

## 2、添加计算机对象

要在 `AD`中创建计算机帐户，我们可以使用 `New-ADComputer cmdlet`：

    
    
    New-ADComputer -Name testPC01 -SamAccountName testPC01 -DNSHostName testPC01.pentest.com
    

![1686720634_6489507a873d3144e1e2c.png!small?1686720635258](https://image.3001.net/images/20230614/1686720634_6489507a873d3144e1e2c.png!small?1686720635258)

要批量创建多个计算机账户，类似于批量创建用户对象，先建一个数值

    
    
    $CompNames = @('APPSRV01', 'APPSRV02', 'APPSRV03', 'APPSRV04', 'APPSRV05', 'SQLSRV01', 'SQLSRV02', 'SQLSRV03', 'SQLSRV04', 'SQLSRV05', 'VNCSRV01', 'VNCSRV02', 'VNCSRV03', 'VNCSRV04', 'VNCSRV05', 'WEBSRV01', 'WEBSRV02', 'WEBSRV03', 'WEBSRV04', 'WEBSRV05', 'BCKUPSRV01', 'BCKUPSRV02', 'BCKUPSRV03', 'BCKUPSRV04', 'BCKUPSRV05');
    

然后运行`New-ADComputer cmdlet`：

    
    
    foreach($computer in $CompNames){
        $SamAccountName = "$computer"
        try { 
            Write-Host "Creating computer object: $($computer + "." + $Global:domainname)" -ForegroundColor 'Gray'; 
            New-ADComputer -Name $computer -SamAccountName $computer -Instance $Global:templateComp -DNSHostName $($computer + "." + $Global:domainname);
        } catch { 
            Write-Host "Error creating computer object" -ForegroundColor 'Red'
            }
    }
    

## 3、添加组对象

我们可以使用 `New-ADGroup cmdlet`创建组对象

    
    
    New-ADGroup -name "DB Administrators" -GroupScope Global
    

![1686720649_6489508988e08d1256dd3.png!small?1686720650642](https://image.3001.net/images/20230614/1686720649_6489508988e08d1256dd3.png!small?1686720650642)

要批量创建组，我们可以遵循同样的过程。

相关脚本可以在这里下载：<https://github.com/ScarredMonk/PopulateActiveDirectory>

使用脚本填充数据：

## 4、说明

本文由笔者在原文上编译，转载请注明原文出处。

原文出处：[Active Directory Lab Setup (Part 2)- Add data to AD
domain](https://rootdse.org/posts/active-directory-lab-setup-add-data/)

