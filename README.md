# mproxy-gbf
GRANBLUE FANTASY CACHING PROXY

# Why use this software
* Because your browser cache just isn't enough for how much multimedia-rich content you view.
* Because you think that your latency to Akamai's CDN is too high and want to locally cache Granblue Fantasy assets. (The latency is a factor when your browser checks the asset server for modifications before using the cached version.)

Modern browsers will cache a ton of data, but what if it's not enough to cache your regular browsing data **and** Granblue Fantasy assets? I have no idea if this actually is an issue, but I wrote this caching proxy anyway.

# How to use this software

0. Don't use this software.
1. Download and install Python 3 (https://www.python.org/downloads/)
2. Modify `gbf-proxy.ini` if you want.
3. Setup environment and run:
```
    py -m pip install -r requirements.txt
    py gbf-proxy.py
```
4. Point your browser to the proxy configuration in `gbf-proxy.ini` (default: `localhost:8080`).

# Tips

You can use PAC files so that you don't need to proxy ALL your browser traffic through `mproxy-gbf`. Here is a sample PAC file:

```
function FindProxyForURL(url, host) {
	if (shExpMatch(url, "*.granbluefantasy.jp/*")
		&& !shExpMatch(url, "*game.granbluefantasy.jp/(authentication|ob/r)*")) {
		return "PROXY localhost:8080";
	}

	return "DIRECT";
}
```
This PAC file is also included in this repository as `gbf-proxy.pac`.

## Chrome on Windows with PAC files

Chrome uses Windows' proxy settings, so you have to tell Windows to use your PAC file. (Hint: Internet Options)

## Firefox with PAC Files

I think you can tell Firefox to use a PAC file.

## Assets aren't loading or something is missing

Currently, there isn't anything implemented to verify cache data. So things could go wrong. For example, music may never load due to a hiccup when the music is first cached.

In the worst case, you can nuke the entire cache directory and start fresh.
