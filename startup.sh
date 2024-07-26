#!/bin/sh
# Export environment variables for the current session
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1='\2'/p")
