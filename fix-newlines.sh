#!/bin/sh
#
# NAME
#        fix-newlines.sh - Use DOS newlines and ensure a single empty line
#        between vCards
#
# SYNOPSIS
#        fix-newlines.sh FILE...
#
# DESCRIPTION
#        Requires unix2dos.
#
# BUGS
#        https://github.com/l0b0/vcard/issues
#
# COPYRIGHT
#        Copyright (C) 2013 Victor Engmark
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

set -o errexit -o noclobber -o nounset

# Convert to DOS newlines
unix2dos -- "$@"

dir="$(dirname -- "$(readlink -f -- "$0")")"
declare -r dir

# Working directory
TMPDIR="${TMPDIR:-/tmp}"
temporary_dir="$(mktemp -d "$TMPDIR/XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")"
declare -r temporary_dir
trap 'rm -rf -- "$temporary_dir"' 0
trap 'exit 2' 1 2 3 15

# Ensure two DOS newlines only at the end
for path
do
    absolute_path="$(readlink -f -- "$path")"
    cd -- "$temporary_dir"
    "$dir/split.sh" "$absolute_path"
    cd - > /dev/null

    filename="$(basename -- "$absolute_path")"
    sed -i -e '/^\r$/d;$a
    set +o noclobber
    cat -- "${temporary_dir}/${filename}"???????? > "$absolute_path"
    set -o noclobber
done