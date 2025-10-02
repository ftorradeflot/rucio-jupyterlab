#!/bin/bash
IAM_CLIENT_ID=85e6f7a5-580b-4a1c-a6d2-39055143063d
IAM_CLIENT_SECRET=AIYIneAVGs9PTVvQnxNGqDmh3rNTsyFOrrwRIqy1Zc6ngPN9hQe6I2VzDzN2uGLCPsvQI8nhYxf_V09NHk-yv7o
IAM_USER=admin
IAM_PASSWORD=password
IAM_TOKEN_ENDPOINT=https://indigoiam//token
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

result=$(curl -k -s -L \
  -d client_id=${IAM_CLIENT_ID} \
  -d client_secret=${IAM_CLIENT_SECRET} \
  -d grant_type=password \
  -d username=${IAM_USER} \
  -d password=${IAM_PASSWORD} \
  -d scope="openid profile email" \
  -d "audience=rucio" \
  ${IAM_TOKEN_ENDPOINT})

if [[ $? != 0 ]]; then
  echo "Error!"
  echo $result
  exit 1
fi

echo $result

access_token=$(echo $result | jq -r .access_token)
printf "%s" "$access_token" > "$SCRIPT_DIR/rucio_token"
echo ${access_token} | cut -d "." -f 2 | base64 -d | jq .
