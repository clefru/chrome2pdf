#! /usr/bin/env nix-shell
#! nix-shell -i "python" -p "python.withPackages(p: [p.selenium])" -p "chromedriver" -p "chromium"

import json
import os
import tempfile
import shutil
import subprocess
import sys
import selenium
from selenium import webdriver
from collections import OrderedDict

if len(sys.argv) < 2:
    print "Usage: chrome2pdf.py input.ext output.pdf"
    sys.exit(-1)

_, ext = os.path.splitext(sys.argv[1])

tmpDir = tempfile.mkdtemp()
srcFile = tmpDir + "/file" + ext
pdfOut = tmpDir + "/file.pdf"

shutil.copyfile(sys.argv[1], srcFile)

# To get appState try:
# python
# >>> import json
# >>> j = json.loads(file('Preferences', 'r').read())
# >>> print json.dumps(j['printing']['print_preview_sticky_settings']['appState'])

sizes = [OrderedDict([(u'height_microns', 1189000),
                      (u'name', u'ISO_A0'),
                      (u'width_microns', 841000),
                      (u'custom_display_name', 'A0')]),
         OrderedDict([(u'height_microns', 841000),
                      (u'name', u'ISO_A1'),
                      (u'width_microns', 594000),
                      (u'custom_display_name', u'A1')]),
         OrderedDict([(u'height_microns', 594000),
                      (u'name', u'ISO_A2'),
                      (u'width_microns', 420000),
                      (u'custom_display_name', u'A2')]),
         OrderedDict([(u'height_microns', 420000),
                      (u'name', u'ISO_A3'),
                      (u'width_microns', 297000),
                      (u'custom_display_name', u'A3')]),
         OrderedDict([(u'height_microns', 297000),
                      (u'name', u'ISO_A4'),
                      (u'width_microns', 210000),
                      (u'custom_display_name', u'A4')]),
         OrderedDict([(u'height_microns', 210000),
                      (u'name', u'ISO_A5'),
                      (u'width_microns', 148000),
                      (u'custom_display_name', u'A5')]),
         OrderedDict([(u'height_microns', 355600),
                      (u'name', u'NA_LEGAL'),
                      (u'width_microns', 215900),
                      (u'custom_display_name', u'Legal')]),
         OrderedDict([(u'height_microns', 279400),
                      (u'name',u'NA_LETTER'),
                      (u'width_microns', 215900),
                      (u'custom_display_name', u'Letter')]),
         OrderedDict([(u'height_microns', 431800),
                      (u'name', u'NA_LEDGER'),
                      (u'width_microns', 279400),
                      (u'custom_display_name', u'Tabloid')])]

mediaSize = [x for x in sizes if x['custom_display_name'] == 'A4'][0]

printingState = OrderedDict(
    [(u'version', 2),
     (u'mediaSize', mediaSize),
     (u'recentDestinations',
      [OrderedDict([(u'id', u'Save as PDF'),
                    (u'origin', u'local'),
                    (u'displayName', u'Save as PDF')])]),
     (u'customMargins', None),
     (u'marginsType', 1)])

profile = {'printing.print_preview_sticky_settings.appState': json.dumps(printingState), 'savefile.default_directory': tmpDir}

options = webdriver.ChromeOptions()
# required chromedriver under NixOS to find chromium. use .strip() as there is a new line in the output.
options.binary_location = subprocess.check_output("which chromium", shell=True).strip();
options.add_experimental_option('prefs', profile)
options.add_argument('--kiosk-printing')

# Doesn't work in headless mode.. no idea why
#options.add_argument('--headless')
#options.add_argument('headless')
#options.add_argument('window-size=1200x600");

driver = webdriver.Chrome(chrome_options=options)
# Chrome will magically choose file.pdf as output name
driver.get("file://" + srcFile)
driver.execute_script('window.print();')
driver.quit()

# Place file.pdf at output, and cleanup the tmp files
shutil.copyfile(pdfOut, sys.argv[2])
os.unlink(srcFile)
os.unlink(pdfOut)
os.rmdir(tmpDir)
