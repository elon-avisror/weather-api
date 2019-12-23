import json
import sys

params_dict = {4: 'specific-humidity',
               10: 'soil_temperature_level_1',
               36: '10m_u_component_of_wind',
               37: '10m_v_component_of_wind',
               38: '2m_temperature',
               41: 'soil_temperature_level_2',
               47: 'surface_net_solar_radiation',
               54: 'soil_temperature_level_3',
               72: 'maximum_2m_temperature_since_previous_post_processing',
               73: 'minimum_2m_temperature_since_previous_post_processing',
               99: 'total_precipitation',
               107: 'soil_temperature_level_4'}


# TODO: create a min_max function - gets an array of day metrics and operator (>/<) and gets the min_or_max of this day
def min_max(arr, op):
    return False


# TODO: create an average function - run on the day array and for each variable calculate its average
def avg(arr):
    # for each var in dict, gets the avg
    return False


def get_date(ref_time):
    datetime = ref_time.split('T')
    return {'date': datetime[0], 'hour': datetime[1].split('.')[0]}


def convert_cds_json(cds_json):

    res = {'day': []}
    day = {}
    cnt_d = 0
    first_day = ''
    cnt_hr = 0

    for cds_element in cds_json:

        # first time init (it is the first item in the dictionary)
        if first_day == '':
            first_day = get_date(cds_element['header']['refTime'])

            day = {'date': first_day['date'],
                   'hour': [{first_day['hour']: {
                       params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]
                   }}]}

        else:
            # take the refTime and parse from it the hours of each day and its values
            last_day = get_date(cds_element['header']['refTime'])

            # same day
            if first_day['date'] == last_day['date']:

                # same hour
                if first_day['hour'] == last_day['hour']:
                    day['hour'][cnt_hr][first_day['hour']][params_dict[cds_element['header']['parameterNumber']]] = cds_element['data'][0]

                # new hour
                else:
                    day['hour'].append({last_day['hour']: {params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}})
                    first_day['hour'] = last_day['hour']
                    cnt_hr += 1

            # new day
            else:
                res['day'].append(day)
                cnt_d += 1

                # the first day of this date
                first_day = {'date': last_day['date'],
                           'hour': [{last_day['hour']: {params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}}]}

                # save the day
                day = {'date': last_day['date'],
                           'hour': [{last_day['hour']: {params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}}]}

                # init the hours-count
                cnt_hr = 0

    return res


cds_json = json.loads(open('res1.json').read())

print(convert_cds_json(cds_json))
