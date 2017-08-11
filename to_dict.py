import json

_json = """{
    "Pacesetter6thSense": {
        "NotificationRepeat": 3
    },
    "_NewPermissionsComment": "New for multi-org clients, can be toggled individually (i.e. no to orgs but yes to menu permissions)",
    "PacesetterEnableMenuPermissions": true,
    "PacesetterEnableOrganizations": false,
    "PacesetterEnableSlowLocations": true,
    "PacesetterMenuBackgroundArt": "SHORTCODE_menu",
    "PacesetterCourseName": "LONGNAME",
    "PacesetterCourseConfig": {},
    "PacesetterMenuPriority": [
        "member",
        "staff",
        "default"
    ],
    "PacesetterCourseNames": [
        "LONGNAME"
    ],
    "PacesetterCourseIDs": [],
    "PacesetterGroupConfig": {
        "member": {
            "IsPOPEnabled": false,
            "PaymentTypes": "",
            "IsCCEnabled": false
        },
        "default": {
            "IsPOPEnabled": false,
            "PaymentTypes": "",
            "IsCCEnabled": false,
            "CreateAccountButtonTitle": "",
            "SignInButtonTitle": "Login"
        }
    },
    "PacesetterLoginDetails": {
        "default": {
            "cancel": "30,30,30,1",
            "body": "30,30,30,1",
            "login": "30,30,30,1"
        }
    },
    "_HomeDetailsComment": "Supports configuration for main screen of app. Elements are delimited by pipe and are RGBA for X, RGBA for Y, Button title, IGNORED, action, action details. Supports call, url, memberdirectory, map, and startround actions.",
    "PacesetterBackgroundConfig": {
        "should_load": "1",
        "use": "panoramic",
        "video": "IJn_7aHv8dg",
        "panoramic": "SHORTCODE_pano.jpg",
        "logo": "150|100|600|SHORTCODE_logo_transparent.png"
    },
    "PacesetterRoundMenuDetails": {
        "default": [
            [
                "Golf",
                "End Round||endround"
            ]
        ]
    },
    "_RemoteConfigComment": "This enables remote config. Can't be changed remotely and included only for informational purposes.",
    "PacesetterRemoteConfig": true,
    "PacesetterShowStartRound": false,
    "PacesetterIsPrivateApp": true,
    "PoweredByPacesetter": true,
    "PacesetterStripeKey": "",
    "PacesetterWelcomeArt": "SHORTCODE_welcome.jpg",
    "PacesetterClientID": "45",
    "PacesetterCourseID": "0",
    "PacesetterPhoneNumberLink": "tel://",
    "PacesetterTurnhouseArt": ""
}"""

def standard_dict(key='city'):  # TODO: add in golf club key
    d = json.loads(_json)
    return d