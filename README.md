# firedrop_file_getter

This is a simple script the intention of which is to help you download a large number of files from a firedrop folder at once.

Example: You've shared a folder of your holiday photos in a firedrop folder, your friend doesn't have a firedrop account. Rather than clicking, waiting 10sec and downloading 50 files (one at a time), simply run this script.

Script uses: cookiejar, mechanize, beautifulsoup, requests, tdqm to provide automated parsing of firedrop folder and download page, storing of links, and file download status indication. Files are then queued and threaded to download one at a time.

User Guide:

1. You need to enter the direct firedrop folder URL.
2. You need to enter a partial filename to help the parser. Eg: If a file is called "FamilyPhotos_DSC_0001.jpg" Simple enter 'Family'.
3. You need to enter the folder password.

That's it. This is my first attempt at working with Python, so apologies for structure.

No License included, feel free to do whatever you need to do with this.

Checkout TODO.md if you'd like to contribute, or shoot us a pullrequest!
