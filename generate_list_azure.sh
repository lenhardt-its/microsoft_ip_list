#!/bin/bash
MICROSOFT_IP_RANGES_URL="https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
MICROSOFT_IP_RANGES_URL_FINAL=$(curl -Lfs "${MICROSOFT_IP_RANGES_URL}" | grep -Eoi '<a [^>]+>' | grep -Eo 'href="[^\"]+"' | grep "download.microsoft.com/download/" | grep -m 1 -Eo '(http|https)://[^"]+')
DL_PATH=/tmp/azure
tmp=$(mktemp)

# create dl path
mkdir $DL_PATH $FINAL_PATH

# get list
curl -s -o $tmp $MICROSOFT_IP_RANGES_URL_FINAL

# get names and create ip lists
jq -r '.values[] | select (.properties.region == "" ) | .name' $tmp | sort -u | while read name; do
  jq -r '.values[] | select (.name == '\"$name\"' ) | .properties.addressPrefixes[]' $tmp >> $DL_PATH/"$name"_new
  if [ "$(wc -l < $DL_PATH/"$name"_new)" -eq "0" ]; then
    #need to change to monitoring things
        echo "$name has a problem" >&2
        continue
    fi
    sort -u -o docs/azure/"$name".txt $DL_PATH/"$name"_new
    rm -f $DL_PATH/"$name"_new
done

# remove tmp
rm -f $tmp
rm -rf $DL_PATH