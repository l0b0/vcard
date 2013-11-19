#!/usr/bin/env bash
#
# NAME
#        sort-lines.sh - Sort vCard property lines according to a custom key
#
# SYNOPSIS
#        sort-lines.sh KEYFILE FILE...
#
# DESCRIPTION
#        Use to minimize the diff between your file and files exported from
#        third party services.
#
# EXAMPLES
#        ./sort-lines.sh sorts/Gmail.re ~/contacts/*.vcf
#              Sort properties like a Gmail contact export.
#
# BUGS
#        https://github.com/l0b0/vcard/issues
#
# COPYRIGHT
#        Copyright (C) 2012 Victor Engmark
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

set -o errexit -o noclobber -o nounset -o pipefail

dir="$(dirname -- "$(readlink -f -- "$0")")"
declare -r dir

# Process parameters
pattern_file="$(readlink -f -- "$1")"
declare -r pattern_file
shift

# Working directory
TMPDIR="${TMPDIR:-/tmp}"
temporary_dir="$(mktemp -d "$TMPDIR/XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")"
declare -r temporary_dir
trap 'rm -rf -- "$temporary_dir"' 0
trap 'exit 2' 1 2 3 15
cd -- "$temporary_dir"

lines() {
    wc -l "$@" | cut -d ' ' -f 1
}

for path
do
    # Split
    "$dir/split.sh" "$path"

    filename="$(basename -- "$path")"
    for vcard in "$filename"????????
    do
        ll_vcard=ll-"$vcard"
        sorted_ll_vcard=sll-"$vcard"
        sorted_vcard=s-"$vcard"

        # Join long lines
        set +o noclobber
        "$dir/join-lines.sh" "$vcard" > "$ll_vcard"
        set -o noclobber

        # Match patterns into new file
        while IFS= read -r -u 9 pattern
        do
            set +o noclobber
            grep -e "$pattern" -- "$ll_vcard" >> "$sorted_ll_vcard" || true
            set -o noclobber
        done 9< "$pattern_file"

        # Split long lines
        set +o noclobber
        "$dir/split-lines.sh" "$sorted_ll_vcard" > "$sorted_vcard"
        set -o noclobber

        # Assert that we matched all lines
        if [ "$(lines "$vcard")" -ne "$(lines "$sorted_vcard")" ]
        then
            echo "Unmatched line counts:" >&2
            diff -u -- "$vcard" "$sorted_vcard" >&2
            exit 1
        fi
    done

    # Restore file
    set +o noclobber
    cat -- s-* > "$path"
    set -o noclobber
    rm -- *
done
