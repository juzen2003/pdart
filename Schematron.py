# This is a small script to check the output of probatron to see
# whether there were failures, and to convert that to an exit code.

import sys
import xml.dom.minidom

xml = xml.dom.minidom.parse(sys.stdin)
failed_asserts = xml.documentElement.getElementsByTagName('svrl:failed-assert')
if len(failed_asserts) > 0:
    print xml.toprettyxml(indent='  ', newl='\n', encoding='utf-8')
    exit(1)
else:
    exit(0)
