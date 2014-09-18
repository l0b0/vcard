#!/bin/sh
#
# NAME
#        format-TEL.sh - Format TEL property values
#
# SYNOPSIS
#        format-TEL.sh [OPTION...] FILE...
#
# DESCRIPTION
#        Uses the national telephone number formatting rules as defined in
#        <http://en.wikipedia.org/wiki/National_conventions_for_writing_telephone_numbers>.
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

# Sorted by country code
replacements='/^TEL[;:]/{
    # NANP countries
    s/\(+1\)\([0-9]\{3\}\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/

    # Netherlands
    s/\(+31\)\(6\)\([0-9]\{8\}$\)/\1 \2 \3/ # Mobile

    # Belgium
    s/\(+32\)\(4[0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}$\)/\1 \2 \3 \4 \5/ # Mobile

    # France
    s/\(+33\)\([0-9]\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}$\)/\1 \2 \3 \4 \5 \6/

    # Switzerland
    s/\(+41\)\([0-9]\{2\}\)\([0-9]\{3\}\)\([0-9]\{2\}\)\([0-9]\{2\}$\)/\1 \2 \3 \4 \5/

    # United Kingdom
    s/\(+44\)\(800\)\(1111$\)/\1 \2 \3/
    s/\(+44\)\(845\)\(4647$\)/\1 \2 \3/
    s/\(+44\)\(9[0-9]\{2\}\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(8[0-9]\{2\}\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(8[0-9]\{2\}\)\([0-9]\{6\}$\)/\1 \2 \3/
    s/\(+44\)\(7[0-9]\{3\}\)\([0-9]\{6\}$\)/\1 \2 \3/
    s/\(+44\)\(500\)\([0-9]\{6\}$\)/\1 \2 \3/
    s/\(+44\)\(5[0-9]\{3\}\)\([0-9]\{6\}$\)/\1 \2 \3/
    s/\(+44\)\(3[0-9]\{2\}\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(2[0-9]\)\([0-9]\{4\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(19467\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(17687\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(17684\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(17683\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(16977\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(16977\)\([0-9]\{4\}$\)/\1 \2 \3/
    s/\(+44\)\(16974\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(16973\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(15396\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(15395\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(15394\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(15242\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(13873\)\([0-9]\{5\}$\)/\1 \2 \3/
    s/\(+44\)\(1[0-9]1\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(11[0-9]\)\([0-9]\{3\}\)\([0-9]\{4\}$\)/\1 \2 \3 \4/
    s/\(+44\)\(1[0-9]\{3\}\)\([0-9]\{6\}$\)/\1 \2 \3/
    s/\(+44\)\(1[0-9]\{3\}\)\([0-9]\{5\}$\)/\1 \2 \3/

    # Denmark
    s/\(+45\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}$\)/\1 \2 \3 \4 \5/

    # Norway
    s/\(+47\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}$\)/\1 \2 \3 \4 \5/

    # Germany (DIN 5008)
    s/\(+49\)\([0-9]\{4\}\)\([0-9]\{6\}$\)/\1 \2 \3/
}'

sed "$replacements" "$@"
