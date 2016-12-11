# coding: utf-8
from datetime import datetime
import os
import json

from stuf import stuf
import requests

TOKEN = os.environ['COMMUTER_NAVITIA_TOKEN']


def admin_region(q):
    # TODO(tsileo): memoize result
    resp = requests.get('https://api.sncf.com/v1/coverage/sncf/places?q='+q, auth=(TOKEN, '')).json()
    # print resp['places']
    # print resp
    for place in resp['places']:
        if 'administrative_region' in place:
            return place['administrative_region']['id']

    return

def journey(from_, to, date_time):
    from_region = admin_region(from_)
    to_region = admin_region(to)
    # print from_region
    resp = requests.get(
        'https://api.sncf.com/v1/coverage/sncf/journeys?from=' + from_region + '&to=' + to_region + '&disable_geojson=true&datetime=' + date_time,
        auth=(TOKEN, '')
    ).json()
    journey = resp['journeys'][0]
    for section in journey['sections']:
        if 'mode' in section and section['mode'] == 'walking': continue
        return section

    return

def query(q):
    # TODO(tsileo): memoize result
    resp = requests.get('https://api.sncf.com/v1/coverage/sncf/places?q='+q, auth=(TOKEN, '')).json()
    # print resp['places']
    # print resp
    for place in resp['places']:
        if place['embedded_type'] == 'stop_area':
            return resp['links'][0]['href'].format(**stuf(place))
    return
# requests.get('https://api.sncf.com/v1/coverage/sncf/journeys?from=admin:414972extern&to=admin:7444extern&datetime=20161212T094000',
# TODO(tsileo):
# an endpoint for 3 next trip (and handle recurrent/trip in the server?)?
# endpoints to store stip (reccurent optional), list and delete them

def disruption(qs, qdate):
    q =  query(qs)
    # print q
    resp = requests.get(q + '/traffic_reports?from_datetime='+qdate, auth=(TOKEN, '')).json()
    # print resp
    return resp

def stop_schedules(qs, qheadsign, qdate):
    q =  query(qs)
    # print q
    resp = requests.get(q + '/departures?from_datetime='+qdate+'&disable_geojson=true&duration=3600', auth=(TOKEN, '')).json()
    print json.dumps(resp)
    for index, stop in enumerate(resp['departures']):

        # print stop['display_informations']['direction']
        # print json.dumps(stop)
        headsign = stop['display_informations']['headsign']
        # if qheadsign and headsign != qheadsign:
            # continue

        disruptions = []
        for link in stop['display_informations']['links']:
            # print link
            if link['type'] == 'disruption':
                disruptions.append(link['id'])

        out = dict(line_id=stop['route']['line']['id'])
        out['display_informations'] = stop['display_informations']
        out['stop_date_time'] = stop['stop_date_time']
        t1 = datetime.strptime(out['stop_date_time']['departure_date_time'], '%Y%m%dT%H%M%S')
        t2 = datetime.strptime(out['stop_date_time']['base_departure_date_time'], '%Y%m%dT%H%M%S')
        out['stop_date_time']['delay_minutes'] = (t1 - t2).seconds / 60
        out['stop_date_time']['delayed'] = bool(out['stop_date_time']['delay_minutes'])
        out['disruptions'] = []
        if disruptions and 'disruptions' in resp:
            for d in resp['disruptions']:
                # if d['id'] in disruptions:
                d['cause'] = d['impacted_objects'][0]['impacted_stops'][0]['cause']
                del d['impacted_objects']
                out['disruptions'].append(d)
        # return stop
        # for d in disruption(qs, qdate)['disruptions']:
            # print
            # print d
            # print
        return out
    return None

# print json.dumps(stop_schedules('Paris Est', '839125', '20161209T143000'))
# json.dumps(stop_schedules('Troyes', None, '20161212T094000'))
# print json.dumps(stop_schedules('Troyes', '11942', '20161209T094000'))
# print json.dumps(stop_schedules('Paris Est', '11847', '20161209T194000'))
# print json.dumps(disruption('Troyes')['disruptions'])
print json.dumps(journey('Troyes', 'Paris', '20161212T094000'))
