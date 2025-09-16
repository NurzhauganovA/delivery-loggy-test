#!/bin/bash
set -ex
cd api/migrations \
&& aerich upgrade \
&& cd ../.. \
&& delivery-cli fixtures load ./cli/fixtures/permissions.json \
&& delivery-cli fixtures load ./cli/fixtures/groups.json \
&& delivery-api