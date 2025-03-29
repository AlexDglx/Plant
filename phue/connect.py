#!/usr/bin/python
from phue import Bridge
b = Bridge("192.168.1.67")
b.connect()
print(b.get_api())

light = b.get_light_objects('name')
print(light)

state = light['Hue smart plug 1'].on

if(state==True):
    light['Hue smart plug 1'].on = False
    print('Light turned off')
else:
    light['Hue smart plug 1'].on = True
    print('Light turned on')

print(light["Hue smart plug 1"].__dict__)