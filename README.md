# mproxy-gbf
GRANBLUE FANTASY CACHING PROXY

# Why use this software
* Because your browser cache just isn't enough for how much multimedia-rich content you view.
* Because you think that your latency to Akamai's CDN is too high and want to locally cache Granblue Fantasy assets. (The latency is a factor when your browser checks the asset server for modifications before using the cached version.)

Modern browsers will cache a ton of data, but what if it's not enough to cache your regular browsing data **and** Granblue Fantasy assets? I have no idea if this actually is an issue, but I wrote this caching proxy anyway.

# How to use this software

0. Don't use this software.
1. Modify `gbf-proxy.ini` if you want.
2. Setup environment and run:
```
    pip install -r requirements.txt
    python gbf-proxy.py
```
4. Point your browser to the proxy configuration in `gbf-proxy.ini` (default: `localhost:8080`).

# Tips

You can use PAC files so that you don't need to proxy ALL your browser traffic through `mproxy-gbf`. Here is a sample PAC file:

```
function FindProxyForURL(url, host) {
	if (shExpMatch(url, "*.granbluefantasy.jp/*")) {
		return "PROXY localhost:8080";
	}

	return "DIRECT";
}
```

## Chrome on Windows with PAC files

Chrome uses Windows' proxy settings, so you have to tell Windows to use your PAC file.

## Firefox with PAC Files

I think you can tell Firefox to use a PAC file.
