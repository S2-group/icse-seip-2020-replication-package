on run {url_to_download}
	tell application "Google Chrome"
	        activate
	        open location "http://" & url_to_download
	        delay 2

			set tab_name to title of active tab of front window
			delete (every tab of every window where its title = tab_name)
	end tell
end run