#!/bin/bash

# Get the first argument
context=$1
if [ -z "$context" ]; then
  echo "Usage: $0 <context>"
  exit 1
fi

# Requested memory
kubectl --context $context get pods --all-namespaces -o json | jq '[.items[] | {(.metadata.namespace + "/" + .metadata.name): .spec.containers[].resources.requests.memory}] | map(select(.[] != null))' > mem_req.json && \

# Used memory
kubectl --context $context top pods --all-namespaces --no-headers | awk '{print "{\""$1 "/" $2"\": \""$4"\"}"}' | jq -s '.' > mem_used.json && \

# Generate stats
python memstats.py