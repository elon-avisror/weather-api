import json

params_dict = {99: 'maximum_2m_temperature_since_previous_post_processing',
               36: 'total_precipitation',
               37: '10m_u_component_of_wind',
               38: '10m_v_component_of_wind',
               39: '2m_temperature'}


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

        # first time of each day
        if first_day == '':
            cnt_hr = 0
            first_day = get_date(cds_element['header']['refTime'])

            # it is the first item in the dictionary
            if day == {}:
                day = {'date': first_day['date'],
                       'hour': [{first_day['hour']: {
                           params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]
                       }}]}
            else:
                day = new_day

        else:
            # TODO: take the refTime and parse from it the hours of each day and its values
            last_day = get_date(cds_element['header']['refTime'])

            # same day
            if first_day['date'] == last_day['date']:

                print(day)
                # same hour
                if first_day['hour'] == last_day['hour']:
                    #day['hour'][cnt_hr][first_day['hour']] = {params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}
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
                new_day = {'date': last_day['date'],
                           'hour': [{last_day['hour']: {params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}}]}
                first_day = ''

    return res


cds_json = json.loads(open('generate.json').read())

print(convert_cds_json(cds_json))
