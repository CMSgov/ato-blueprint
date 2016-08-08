#!/bin/bash

# Blue-green deployment script. Usage:
#
#   ./cf-blue-green <appname>

set -e
set -o pipefail
set -x


if [ $# -ne 1 ]; then
	echo "Usage:\n\n\t./cf-blue-green <appname>\n"
	exit 1
fi


BLUE=$1
GREEN="${BLUE}-B"


finally ()
{
  # we don't want to keep the sensitive information around
  rm $MANIFEST
}

on_fail () {
  finally
  echo "DEPLOY FAILED - you may need to check 'cf apps' and 'cf routes' and do manual cleanup"
}


# pull the up-to-date manifest from the BLUE (existing) application
MANIFEST=$(mktemp -t "${BLUE}_manifest.XXXXXXXXXX")
cf create-app-manifest $BLUE -p $MANIFEST

# set up try/catch
# http://stackoverflow.com/a/185900/358804
trap on_fail ERR

#DOMAIN=${B_DOMAIN:-$(cat $MANIFEST | grep domain: | awk '{print $2}')}
DOMAIN=qdev.govready.com


# create the GREEN application
cf push $GREEN -f $MANIFEST -n $GREEN
# ensure it starts
curl --fail --insecure -I "https://${GREEN}.${DOMAIN}"

# add the GREEN application to each BLUE route to be load-balanced
# TODO this output parsing seems a bit fragile...find a way to use more structured output

# govready does it a bit differently, we push with --no-hostname, so there's no field 2 (host)
#cf routes | tail -n +4 | grep $BLUE | awk '{print $3" -n "$2}' | xargs -n 3 echo cf map-route $GREEN

cf map-route $GREEN $DOMAIN --hostname \*
cf map-route $GREEN $DOMAIN

# cleanup
# TODO consider 'stop'-ing the BLUE instead of deleting it, so that depedencies are cached for next time
cf delete $BLUE -f
cf rename $GREEN $BLUE
cf delete-route $DOMAIN -n $GREEN -f
finally

echo "DONE"
