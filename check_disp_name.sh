OK=0
for f in $(find . -name r2.po); do
	grep -i -q display-name-en $f
	if [ "$?" != "0" ]; then
		echo "$f: Missing Display-Name"
		OK=1
	fi
done
exit $OK
