#!/usr/bin/env bash
#
# NAME
#        split.sh - Split a multiple vCards file into individual files
#
# SYNOPSIS
#        split.sh FILE...
#
# DESCRIPTION
#        Can be used to process vCards individually. Restore the original file
#        with `cat xx* > original.vcf`.
#
#        See `man csplit` for options.
#
# BUGS
#        https://github.com/l0b0/vcard/issues
#
# COPYRIGHT
#        Copyright (C) 2012-2013 Victor Engmark
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

for path
do
    csplit --elide-empty-files --prefix "$(basename -- "$path")" "$path" $'/^BEGIN:VCARD\r$/' {*} >/dev/null
done
