#!/usr/bin/env sh
#
# NAME
#        split-lines.sh - Split long vCard lines
#
# SYNOPSIS
#        split-lines.sh FILE...
#
# DESCRIPTION
#        Simply inserts the sequence CR, LF, space to make every line 75
#        characters (excluding CR and LF).
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

awk '
{
    if (length() > 76) {
        printf("%s\r\n ", substr($0, 1, 75));
        $0 = substr($0, 76);
        while (length() > 75) {
            printf("%s\r\n ", substr($0, 1, 74));
            $0 = substr($0, 75);
        }
    }
    print $0;
}' "$@"
