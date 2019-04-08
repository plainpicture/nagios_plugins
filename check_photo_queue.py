#!/usr/bin/env python3
"""Parse Plainpicture app metrics.

Depends:

  - https://github.com/prometheus/prom2json
"""

import json
import subprocess
import sys
import traceback

WARN = 72
CRIT = 96


def get_value(keyname):
    """Get value from given metric."""
    # print(app_queue_last_created_hours)
    # [{'name': 'app_queue_last_created_hours',
    #   'help': '',
    #   'type': 'UNTYPED',
    #   'metrics': [{'value': '15'}]}]
    value = [key for key in metrics if key['name'] == keyname]
    metrics_value = value[0]['metrics'][0]['value']
    return(metrics_value)


if __name__ == "__main__":
    try:
        # For developing: Use local file to fake results:
        # result = subprocess.run(['prom2json', 'dummy.txt'],
        #                         stdout=subprocess.PIPE)
        result = subprocess.run(
            ['prom2json', 'https://www.plainpicture.com/metrics'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # shell=True,
            check=True)
    except Exception:
        exception_msg = traceback.format_exc().splitlines()[-1]
        print('Unknown: Cant fetch metrics (' + exception_msg + ')')
        sys.exit(3)

    metrics_str = result.stdout.decode('utf-8')

    try:
        metrics = json.loads(metrics_str)
    except Exception:
        exception_msg = traceback.format_exc().splitlines()[-1]
        print('Unknown: Cant parse JSON (' + exception_msg + ')')
        sys.exit(3)

    last_created_hours = get_value('app_queue_last_created_hours')
    last_generated_hours = get_value('app_queue_last_generated_hours')
    last_exported_from_photobay_hours = \
        get_value('app_queue_last_exported_from_photobay_hours')
    last_photobay_synchronization_timestamp = \
        get_value('app_queue_last_photobay_synchronization_timestamp')

    summary = 'app_queue_last_created_hours: ' + last_created_hours + ', ' \
              'last_generated_hours: ' + last_generated_hours + ', ' \
              'last_exported_from_photobay_hours:' + \
              last_exported_from_photobay_hours + ', ' + \
              'last_photobay_synchronization_timestamp: ' + \
              last_photobay_synchronization_timestamp

    if int(last_generated_hours) >= CRIT:
        print('CRITICAL: ' + summary)
        sys.exit(2)
    else:
        if int(last_generated_hours) >= WARN:
            print('WARNING: ' + summary)
            sys.exit(1)
        else:
            print('OK: ' + summary)
