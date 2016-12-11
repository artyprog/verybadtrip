# coding: utf-8
import json

from nameko.web.handlers import http

import config
import commuter

trips_config = config.load()


class TripService:
    name = "trip_service"

    @http('GET', '/next_trips')
    def get_method(self, request):
        trips = []
        for trip_config in trips_config:
            trips.append(commuter.stop_schedules(
                trip_config.from_, trip_config.headsign, trip_config.date_time,
            ))
        return json.dumps({'trips': trips})
