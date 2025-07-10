#!/bin/bash

# Test script to verify Discord webhook format

WEBHOOK_URL="https://discord.com/api/webhooks/1392851349871263794/OnlF2OAVJ9HTfr35M-vb-I4BFevFRWJLaNRCJAPGk3Mt8y3ZUIh3ggKvZ1OJkZqeAwuw"

# Test 1: Simple content with ping
echo "Test 1: Simple content with ping"
curl -H "Content-Type: application/json" -X POST "$WEBHOOK_URL" \
  -d '{"content":"<@474581341581606912> Test 1: This ping should be outside the embed"}'

sleep 2

# Test 2: Content + Embed
echo -e "\n\nTest 2: Content + Embed"
curl -H "Content-Type: application/json" -X POST "$WEBHOOK_URL" \
  -d '{
    "content": "<@474581341581606912> Test 2: Ping outside embed",
    "embeds": [{
      "title": "Test Alert",
      "description": "This is inside the embed",
      "color": 15158332
    }]
  }'

sleep 2

# Test 3: Exact format that AlertManager should send
echo -e "\n\nTest 3: AlertManager format"
PAYLOAD='{
  "content": "<@474581341581606912> **CRITICAL ALERT!**",
  "embeds": [{
    "title": "🚨 TestAlert",
    "description": "**Alert:** TestAlert\\n**Namespace:** default\\n**Pod/Resource:** test-pod\\n**Summary:** Test summary\\n**Details:** Test details\\n**Started:** Jul 10, 15:00 UTC\\n**Severity:** critical",
    "color": 15158332
  }]
}'

curl -H "Content-Type: application/json" -X POST "$WEBHOOK_URL" -d "$PAYLOAD"