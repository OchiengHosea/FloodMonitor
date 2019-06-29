__name__ = 'whenwillitrain'

from weatherapi.apiutil import host, default_params

def request_options (lat, lon, days = 3, units = 'm'):
  d = days if days in [3, 5, 7, 10, 15] else 3
  u = units if units in ['e', 'm', 'h', 's'] else 'm'

  url = host + '/v1//geocode/{lat}/{lon}/forecast/wwir.json'.format(lat=lat, lon=lon, days=d)
  
  params = default_params()
  params['units'] = u

  return url, params


def handle_response (res):
  if res and res['forecast']:
    forecast = res['forecast']
    print('daily-forecast: returned {}-day forecast'.format(len(forecast)))

    # each entry in the forecasts array corresponds to a daily forecast
    """
    for index, daily in enumerate(forecasts):
      print('daily-forecast: day {} - High of {}, Low of {}'.format(index, daily['max_temp'], daily['min_temp']))
      print('daily-forecast: day {} - {}'.format(index, daily['narrative']))
      """
    print(forecast)
    return forecast
    # additional entries include (but not limited to):
    # lunar_phase, sunrise, day['uv_index'], night['wdir'], etc
  else:
    print('daily-forecast: no daily forecast returned')