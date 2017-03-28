#!/bin/sh

cp vars.yml-template vars.yml

EXIT=0
while [ $EXIT -eq 0 ]
do
	PASS=$(pwgen 64 1)
	sed -i "0,/PASSWORD/s/PASSWORD/$PASS/" vars.yml
	echo $PASS
	grep PASSWORD vars.yml
	EXIT=$?
done
