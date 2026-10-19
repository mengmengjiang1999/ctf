import py7zr
import re




logs = open(
   "flow_505974f1525bf82dfa87621e167756ca/第一阶段/oa.access.log"
).read() 
# + open("combine.txt").read()




def get_ip(logs):
   ips = []
   for log in logs.split("\n"):
       try:
           ip = re.findall(r"\d+\.\d+\.\d+\.\d+", log)[0]
           ips.append(ip)
       except:
           pass
   return ips


ips = list(set(get_ip(logs)))


print(ips)


for item in ips:
    try:
        with py7zr.SevenZipFile(
            "flow_505974f1525bf82dfa87621e167756ca/第二阶段/二阶段汇总.7z",
            mode="r",
            password=item,
        ) as z:
            z.extractall()
    except:
        pass
