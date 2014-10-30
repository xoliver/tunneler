Tunneler
=======

Stuff to make stuff tunnels with stuff

Configuration
-------------

Create file ~/.tunneler.cfg with something similar to this:

	# Sample configuration file
	# Copy to ~/.tunneler.cfg and adapt

	# Common settings section (optional)
	[common]
	# If a tunnel does not specify a user this one will be used
	default_user = YOUR_DEFAULT_USER

	# Tunnel groups (optional)
	[groups]
	# Multiple names are allowed. These must be defined in the file
	tunnel_group_1 =
			tunnel1
			tunnel2:port  # Specifying a local port here overrides the tunnel's default

	# Tunnel information - copy at will. 'user' is optional
	[TUNNEL-NAME]
	name = TUNNEL_LONG_NAME
	local_port = LOCAL_MACHINE_PORT
	remote_port = SERVER_PORT
	server = SERVER_NAME
	user = OPTIONAL_USER_NAME


Usage
-----

	Usage: tunneler [OPTIONS] COMMAND [ARGS]...

	Options:
	  --verbose  Show verbose information
	  --help     Show this message and exit.

	Commands:
	  check  Check the state of a tunnel
	  show   Show active/inactive (tunnels|groups|all)
	  start  Start one or more tunnels
	  stop   Stop one or more or ALL tunnels
