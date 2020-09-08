#!/usr/bin/env bash

usage_exit() {
    echo "usage: $0 { gitpoll | ispoll } [COURSE [DB [USER]]]"
    echo
    echo "Arguments can be also read from environemnt variables:"
    printf "  \$FRAG_SUBJECT (${FRAG_SUBJECT:-[unset]}),"
    printf " \$FRAG_HOST (${FRAG_HOST:-[unset]}), and"
    echo " \$FRAG_USER (${FRAG_USER:-[unset]})."
    echo "User also defaults to current \$USER ($USER)"
    exit $1
}

if ! [[ "$1" ]]; then
    usage_exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

POLL=$1
COURSE=${2:-$FRAG_SUBJECT}
DB=${3:-$FRAG_HOST}
USER=${4:-${FRAG_USER:-$USER}}

if ! [[ "$COURSE" ]] || ! [[ "$DB" ]] || ! [[ "$USER" ]]; then
    usage_exit 2
fi

cat $DIR/common.sql | sed -e "s/{COURSE}/$COURSE/g" -e "s/{POLL}/$POLL/g" \
    | psql -h $DB -d $COURSE -U $USER --echo-all
