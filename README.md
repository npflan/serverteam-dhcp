Pretty much catered to only use for server team in npflan

oneliner for converting leases to static
```
cat leases |grep -E "(lease|hardware)"|awk '{ if($1 == "lease") printf($2); if($1=="hardware") print " " $3 }'|sort|awk '{split($1,a,"."); print "host ip-" a[3] "-" a[4] " {\n\thardware ethernet " $2 ";\n\tfixed-address " $1 ";\n}" }'
```