""" Interval to refresh status codes in seconds. """
refresh_interval = 60.0

""" File containing groups ofurls to check in json format. See included example 'checkurls.json'. """
filename = 'checkurls.json'

""" Message to display if sites are not connectable. """
site_down = 'UNREACHABLE'

""" Number of concurrent connections while checking sites. """
number_threads = 8

""" Enable a user submitted search through urls to verify they're in the file specified in 'filename'. """
include_search = False