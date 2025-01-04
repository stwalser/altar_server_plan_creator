# Altar Server Plan Creator

This Python application assigns altar servers automatically to different masses. The masses, the 
altar servers and other information must be specified in four different .yaml files.

## Usage

The script requires three `.json` files called `altar_servers.yaml`, `holy_masses.yaml` and `plan_info.yaml`. They must be located in the `config/` folder and follow the following schema.

### altar_servers.yaml

    {
        '$defs': {
            'Vacation': {
                'description': 'The vacation class.',
                'properties': {
                    'start': {
                        'format': 'date',
                        'title': 'Start',
                        'type': 'string'
                    },
                    'end': {
                        'format': 'date',
                        'title': 'End',
                        'type': 'string'
                    }
                },
                'required': ['start', 'end'],
                'title': 'Vacation',
                'type': 'object'
            }
        },
        'description': 'The altar server class, containing the information of one server and convenience methods.',
        'properties': {
            'name': {
                'title': 'Name',
                'type': 'string'
            },
            'siblings': {
                'anyOf': [{
                    'items': {
                        'type': 'string'
                    },
                    'type': 'array'
                }, {
                    'type': 'null'
                }],
                'default': [],
                'title': 'Siblings'
            },
            'avoid': {
                'default': [],
                'items': {
                    'type': 'integer'
                },
                'title': 'Avoid',
                'type': 'array'
            },
            'vacations': {
                'default': [],
                'items': {
                    '$ref': '#/$defs/Vacation'
                },
                'title': 'Vacations',
                'type': 'array'
            },
            'locations': {
                'default': [],
                'items': {
                    'type': 'string'
                },
                'title': 'Locations',
                'type': 'array'
            },
            'service_dates': {
                'default': [],
                'items': {
                    'format': 'date',
                    'type': 'string'
                },
                'title': 'Service Dates',
                'type': 'array'
            }
        },
        'required': ['name'],
        'title': 'AltarServer',
        'type': 'object'
    }

### holy_masses.json

    {
        '$defs': {
            'Event': {
                'description': 'Class that represents a single event in the event calendar. Typically, a mass.',
                'properties': {
                    'id': {
                        'title': 'Id',
                        'type': 'string'
                    },
                    'n_servers': {
                        'title': 'N Servers',
                        'type': 'integer'
                    },
                    'time': {
                        'format': 'time',
                        'title': 'Time',
                        'type': 'string'
                    },
                    'comment': {
                        'anyOf': [{
                            'type': 'string'
                        }, {
                            'type': 'null'
                        }],
                        'default': None,
                        'title': 'Comment'
                    },
                    'location': {
                        'anyOf': [{
                            'type': 'string'
                        }, {
                            'type': 'null'
                        }],
                        'default': None,
                        'title': 'Location'
                    },
                    'servers': {
                        'anyOf': [{
                            'items': {
                                'type': 'string'
                            },
                            'type': 'array'
                        }, {
                            'additionalProperties': {
                                'items': {
                                    'type': 'string'
                                },
                                'type': 'array'
                            },
                            'propertyNames': {
                                'format': 'date'
                            },
                            'type': 'object'
                        }, {
                            'type': 'null'
                        }],
                        'default': None,
                        'title': 'Servers'
                    }
                },
                'required': ['id', 'n_servers', 'time'],
                'title': 'Event',
                'type': 'object'
            },
            'EventDay': {
                'description': 'Class that represents a day containing one or multiple events.',
                'properties': {
                    'id': {
                        'title': 'Id',
                        'type': 'string'
                    },
                    'name': {
                        'anyOf': [{
                            'type': 'string'
                        }, {
                            'type': 'null'
                        }],
                        'default': None,
                        'title': 'Name'
                    },
                    'events': {
                        'items': {
                            '$ref': '#/$defs/Event'
                        },
                        'title': 'Events',
                        'type': 'array'
                    }
                },
                'required': ['id', 'events'],
                'title': 'EventDay',
                'type': 'object'
            }
        },
        'description': 'The Event calendar class that contains all events and their information.',
        'properties': {
            'weekday': {
                'additionalProperties': {
                    '$ref': '#/$defs/EventDay'
                },
                'title': 'Weekday',
                'type': 'object'
            },
            'easter': {
                'additionalProperties': {
                    '$ref': '#/$defs/EventDay'
                },
                'title': 'Easter',
                'type': 'object'
            },
            'date': {
                'additionalProperties': {
                    '$ref': '#/$defs/model_json_schema'
                },
                'propertyNames': {
                    'format': 'date'
                },
                'title': 'Date',
                'type': 'object'
            },
            'custom': {
                'additionalProperties': {
                    '$ref': '#/$defs/EventDay'
                },
                'propertyNames': {
                    'format': 'date'
                },
                'title': 'Custom',
                'type': 'object'
            }
        },
        'required': ['weekday', 'easter', 'date', 'custom'],
        'title': 'EventCalendar',
        'type': 'object'
    }

### plan_info.json

    {
        '$defs': {
            'WelcomeText': {
                'description': 'The welcome text of the plan.',
                'properties': {
                    'greeting': {
                        'title': 'Greeting',
                        'type': 'string'
                    },
                    'body': {
                        'items': {
                            'type': 'string'
                        },
                        'title': 'Body',
                        'type': 'array'
                    },
                    'dismissal': {
                        'title': 'Dismissal',
                        'type': 'string'
                    }
                },
                'required': ['greeting', 'body', 'dismissal'],
                'title': 'WelcomeText',
                'type': 'object'
            }
        },
        'description': 'The plan info.',
        'properties': {
            'start_date': {
                'format': 'date',
                'title': 'Start Date',
                'type': 'string'
            },
            'end_date': {
                'format': 'date',
                'title': 'End Date',
                'type': 'string'
            },
            'welcome_text': {
                '$ref': '#/$defs/WelcomeText'
            }
        },
        'required': ['start_date', 'end_date', 'welcome_text'],
        'title': 'PlanInfo',
        'type': 'object'
    }


## Features
