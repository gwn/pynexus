import auth
import helpers

import time


# report & report download paths for all report API calls
report_path   = 'report'
download_path = 'report-download'


def get(payload_or_report_id, outfile, request_interval=5, timeout=300, debug=False):
    """ Get the requested report from App Nexus and
    save it to the given file. """

    if isinstance(payload_or_report_id, basestring):
        report_id = payload_or_report_id
    else:
        report_id = request_report(payload_or_report_id)


    start_time = time.time()

    while True:
        time.sleep(request_interval)

        time_spent = time.time() - start_time

        if time_spent > timeout:
            raise AppNexusReportError('timeout', 'Report timed out.', report_id)
        
        if report_is_ready(report_id, debug=debug):
            break


    report_content = download_report(report_id)

    with open(outfile, 'w') as f:
        f.write(report_content)


def request_report(payload):
    """ Request a report from App Nexus and returns the report id. """

    resp = auth.request('post', report_path, json=payload)

    helpers.raise_for_error(resp)

    return resp.json()['response']['report_id']


def report_is_ready(report_id, debug=False):
    resp = auth.request('get', report_path, params={'id': report_id})

    helpers.raise_for_error(resp)

    report_status = resp.json()['response']['execution_status']

    if debug:
        print 'Checking report status for report "%s": %s' \
                  % (report_id, report_status)


    return report_status == 'ready'


def download_report(report_id):
    resp = auth.request('get', download_path, params={'id': report_id})

    helpers.raise_for_error(resp)

    return resp.text


class AppNexusReportError():
    def __init__(error_id, error_message, report_id):
        self.id        = error_id
        self.message   = error_message
        self.report_id = report_id
