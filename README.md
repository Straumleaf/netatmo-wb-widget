# netatmo-wb-widget
Waybar widget for Netatmo weather station. Written with use of [lnetatmo](https://github.com/philippelt/netatmo-api-python) API library: https://github.com/philippelt/netatmo-api-python

## Widget setup

+ assuming that Python already installed.
+ please install [lnetatmo](https://github.com/philippelt/netatmo-api-python) API library by:

        pip install lnetatmo

+ clone this repository.
+ go to https://dev.netatmo.com and make a registration
    -  login there and go to **My apps** through the top right menu
       or go straight to https://dev.netatmo.com/apps/ , whatever you prefer.
    -  and create netatmo application by choosing **Create** button.
    -  then fill such fields as: **app name**, **description**, **data protection officer name** and **data protection officer email** with appropriate information.
    -  and push the button **Save**, after that you will get access to: client ID, client secret
        and also access to Token generator which is required to get access to your Weather Station.
+ copy **client ID**, **client secret** and generated token and paste it in the file **.netatmo.credentials**.
+ place **.netatmo.credentials** file to your home directory, please.

       cp .netatmo.credentials ~/
+ now everything is ready to setup **netatmo-wb-widget.py**
+ ussualy I'm placing widget sripts to the **./config/waybar/script** directory but you could place it wherever you want but do not forget co correct the path to this script accordingly, in the waybar config file. For instance here below a part of my waybar config file: 

        "custom/netatmo": {
            "format": "<span color=\"#E47E39\">󰋞</span> {} {icon}",
            "format-icons": ["","","","",""],
            "tooltip": true,
            "interval": 1800,
            "exec": "~/.config/waybar/scripts/netatmo-wb-widget.py",
            "return-type": "json"
        },
    - you could change interval option as it suits. By default it set to 1800 sec or 30 min.
    - turn On or Off tooltip and so on.
+ widget is returning back a JSON structure for waybar.
+ you could also mention in waybar **style.css** file temperature syles(color) like it mentioned below, for instance (there are 3 type - hot, cold and normal classes, here described only two of them):

        #custom-netatmo {
            color: #EBCB8B;
        }

        #custom-netatmo.cold {
            color:deepskyblue;
        }

        #custom-netatmo.hot {
            color: #BF616A;
        }
