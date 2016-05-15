So this was written "to get the job done". It's not pretty and needs a few things done.

1. Add better error checking (I've only included a quick password check). It needs a few try/catch blocks to assess code along the way (checking against HTTP response codes).
2. Some decoupling: Parts of the code (eg: using regex with short_url) and generally things should be in better defined functions.
3. The mainpage_links_name could probably be parsed without the user having to enter a partial filename (this would help it download differently named files).
4. Probably some further decoupling to get it working with other filesharing websites? It's a start atleast for firedrop.
