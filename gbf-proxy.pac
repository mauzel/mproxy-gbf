function FindProxyForURL(url, host) {
	if (shExpMatch(url, "*.granbluefantasy.jp/*")
		&& !shExpMatch(url, "*game.granbluefantasy.jp/(authentication|ob/r)*")) {
		return "PROXY localhost:8080";
	}
	
	return "DIRECT";
}