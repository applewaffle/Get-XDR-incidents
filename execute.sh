#!/bin/bash
DIR="$( cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
source ./bin/activate

for customer in $(ls config | grep -v customer.json); do
	python get-xdr-incidents.py "$customer"
	
done
