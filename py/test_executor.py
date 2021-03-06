from datetime import datetime, time

import argparse
import json
import requests
import curlify
import os
import time
import urllib
import glob
import random


def date_diff_in_Seconds(dt2, dt1):
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


class ApiTestHandler:
    # def __init__(self):

    def __init__(self, settings):
        self.base_url = settings['server'] + "/platform"
        self.user = settings['user']
        self.passwd = settings['pass']

        self.token = None
        self.userId = None
        self.userAccount = None
        self.project_id = None

    def generate_test_script(self, test_case_ids, url="/v1/projects/{project_id}/generate"):
        url = url.format(project_id=self.project_id)
        payload = {"sessionId": "auT0M00iq", "testCases": test_case_ids}
        headers = self.get_header()
        del headers['content-type']
        response = requests.request("POST", self.base_url + url, json=payload, headers=headers)
        return response

    def get_testcase(self, test_case_id, url="/v1/projects/{project_id}/testcases/{test_case_id}/gettestcase"):
        url = url.format(project_id=self.project_id, test_case_id=test_case_id)
        response = requests.request("GET", self.base_url + url, headers=self.get_header())
        return response.text

    # print("got back json response: {}".format(project_response))
    # response: {"error": "Found Project with same name, id: 64", "status": "fail"}
    # if

    def upload_testcase(self, test_case_file, test_data_file, url="/v1/projects/{0}/testcases/upload"):
        url = url.format(self.project_id)
        print("url: {}".format(url))
        # files = {'file': (test_case_file, open(test_case_file, 'rb'))}
        files = {'casefile': open(test_case_file, 'rb'), 'datafile': open(test_data_file, 'rb')}
        print("test_case_file: {}".format(test_case_file))
        print("test_data_file: {}".format(test_data_file))

        payload = {"sessionId": "auT0M00iq", "accountId": self.userAccount}

        headers = self.get_header()
        del headers['content-type']

        response = requests.request("POST", self.base_url + url, files=files, data=payload, headers=headers)

        return response.text

    def upload_recorder_testcase(self, j):
        pass

    # content - type: multipart / form - data;
    def create_project(self, url="/v1/projects", name="Sanity", appUrl="login.salesforce.com"):
        print("url: {0}".format(self.base_url + url))

        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;" \
                  "name=\"params\"\r\n\r\n{{\"projectName\":\"{0}\",\"appUrl\":\"{1}\"}}" \
                  "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--".format(name, appUrl)
        # print("payload: {0}".format(payload))
        headers = self.get_header()

        response = requests.request("POST", self.base_url + url, data=payload, headers=headers)

        return response.text

    def delete_project(self, project_id, url="/v1/projects/disable"):
        payload = "{{\"projectIds\":[{0}]}}".format(project_id)
        headers = self.get_header()

        response = requests.request("POST", self.base_url + url, data=payload, headers=headers)
        return response.text

    def get_header(self):
        return {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'Authorization': "Bearer {}".format(self.token),
            'cache-control': "no-cache",
        }

    def get_token(self, url="/v1/auth"):
        resp = self.post_request(url, headers={"Content-Type": "application/json"},
                                 params={"username": self.user, "password": self.passwd}).text
        print(resp)
        j = json.loads(resp)

        self.token = j['token']
        print("token: {}".format(self.token))

        self.userId = j['userId']
        print("userId: {}".format(self.userId))

        self.userAccount = j['userAccount']
        print("userAccount: {}".format(self.userAccount))

    def post_request(self, url, params=None, headers=None, use_json=True):
        full_url = self.base_url + url
        print("full_url is {}".format(full_url))
        print("params: {}".format(params))
        if use_json:
            rsp = requests.post(full_url, json=params, headers=headers, verify=False)
        else:
            rsp = requests.post(full_url, data=params, headers=headers, verify=False)

        return rsp

    def get_request(self, url, params=None, headers=None):
        rsp = requests.get(self.base_url + url, json=params, headers=headers, verify=False)
        return rsp

    def delete_request(self, url, params=None, headers=None):
        rsp = requests.delete(self.base_url + url, json=params, headers=headers, verify=False)
        return rsp

    def put_request(self, url, params=None, headers=None):
        rsp = requests.put(self.base_url + url, json=params, headers=headers, verify=False)
        return rsp

    def execute_testsuite(self, test_suite_id, data, url="/v1/testsuite/{test_suite_id}/execute"):
        url = url.format(test_suite_id=test_suite_id)
        headers = self.get_header()
        del headers['content-type']
        response = self.post_request(url, params=data, headers=headers)
        return response

    def get_all_project(self, url="/v1/getprojects"):
        headers = self.get_header()
        return self.get_request(url, headers=headers)

    def get_json(self, response):
        if response.status_code == 200:
            return json.loads(response.text)
        return []

    def get_test_cases_by_project_id(self, project_id, url="/v1/projects/{project_id}/testcases"):
        url = url.format(project_id=project_id)
        response = self.get_request(url, headers=self.get_header())
        return response

    def get_test_case_details_by_project_name(self, project_name):
        projects = self.get_json(self.get_all_project())
        test_cases_details = []
        if not projects:
            print('Project {} is not found'.format(project_name))
            return []
        for project in projects:
            if project['projectName'] == project_name:
                self.project_id = project['projectId']
                project_id = project['projectId']
                response = self.get_test_cases_by_project_id(project_id)
                test_cases_details = self.get_json(response)
                return test_cases_details if test_cases_details else []
        return []


    def run_test_case_by_test_case_id_and_project_id(self, test_case_id):
        return self.generate_test_script([test_case_id])

    def get_all_suites(self, url="/v1/gettestsuites"):
        headers = self.get_header()
        return self.get_request(url, headers=headers)

    def get_suite_id(self, suite_name=''):
        project_name = None

        if '|' in suite_name:
            project_name, suite_name = suite_name.split('|')
        else:
            print('Should be in this format "[project_name]|[suite_name]"')

        response = self.get_all_suites()
        if response.status_code == 200:
            all_suite = json.loads(response.text)
            for suite in all_suite:
                if suite['testSuiteName'] == suite_name and project_name == suite['projectName']:
                    print(suite)
                    return suite['testSuiteId']
        return None


def run_test_cases(_settings, api_test_handler):
    project_response = api_test_handler.create_project(name="Sanity_{}".format(random.randint(999, 100000)))

    test_cases_errors = []
    test_cases_passed = []
    test_cases_skipped = []

    # print("project_response in txt form: {}".format(project_response))
    j = json.loads(project_response)

    # print("got back json response: {}".format(project_response))
    # response: {"error": "Found Project with same name, id: 64", "status": "fail"}

    project_id = j["id"]
    api_test_handler.project_id = project_id
    print("Given File(s): {}".format(_settings['files']))

    print("data file path: {}".format(os.path.abspath("data.csv")))

    # files = _settings['files']
    try:
        if _settings['files'] != "skip":
            test_files = glob.glob(_settings['files'], recursive=True)

            for tc in test_files:
                if 'data' in tc:
                    continue
                resp = api_test_handler.upload_testcase(os.path.abspath(tc), os.path.abspath("data.csv"))
                j = json.loads(resp)
                # response: {"test_case_id": 674, "name": "Test_AirBnB_with_excel_formula",
                #            "creation_time": "2019-02-05T23:49:37.648531397Z"}

                # print("json: out")
                # print(j)
                # j = json.loads(resp)
                # print(j)
                test_case_id = j["success"][0]["test_case_id"]
                resp = api_test_handler.get_testcase(test_case_id)
                print(j)
                # 'testScriptDownloadLink': 'http://minio:9000/000001/appuser/1/Sanity/64/688/Test_nearby_with_quotes.java', 'testScriptGenerationStatus': 'SUCCESS',
                while j['status'] is True or j['status'] == 0:
                    time.sleep(10)
                    print("..sleeping...\n")

                    resp = api_test_handler.get_testcase(test_case_id)
                    j = json.loads(resp)
                    print(j)

                script_result = j['testScripts'][0]

                if len(script_result["testScriptDownloadLink"]) > 0 and script_result[
                    'testScriptGenerationStatus'] != 'FAILED':
                    print("PASSED")
                    # date2 = datetime.now()

                    date1 = datetime.strptime(script_result['initiatedTime'], '%Y-%m-%dT%H:%M:%SZ')
                    date2 = datetime.strptime(script_result['generationTime'], '%Y-%m-%dT%H:%M:%SZ')

                    print("\n Testcase %d took %d seconds" % (test_case_id, date_diff_in_Seconds(date2, date1)))
                    time_taken = date_diff_in_Seconds(date2, date1)
                    test_cases_passed.append({"test_case_id": test_case_id,
                                              "time_taken": time_taken,
                                              "url": api_test_handler.base_url + "/{project_id}/{test_case_id}"
                                             .format(project_id=api_test_handler.project_id,
                                                     test_case_id=test_case_id)})
                else:
                    test_cases_errors.append({"test_case_id": test_case_id,
                                              "failed_message": j['statusMessage'],
                                              # "time_taken": time_taken,
                                              "url": api_test_handler.base_url.replace("platform",
                                                                                       "details") + "/{project_id}/{test_case_id}"
                                             .format(project_id=api_test_handler.project_id,
                                                     test_case_id=test_case_id)})

                print("Number of Tests Passed: {}".format(len(test_cases_passed)))
                print("Number of Tests Failed: {}".format(len(test_cases_errors)))
                print("Current Success Rate: {:.2f}% ".format(
                    len(test_cases_passed) * 100.0 / (len(test_cases_passed) + len(test_cases_errors))))
        else:
            print("Skipping Test Case Files as requested")

        if _settings['recorder_files'] != "skip":
            recorder_test_files = glob.glob(_settings['recorder_files'], recursive=True)

            # Look for recorder files in Test_Recorder folder
            filtered_test_files = [r for r in recorder_test_files if r.startswith("../Test_Recorder")]
            # print(filtered_test_files)
            for f in filtered_test_files:
                j = json.loads(open(f).read())

        else:
            print("Skipping Recorder Tests as requested")

    finally:
        if _settings['cleanup']:
            resp = api_test_handler.delete_project(project_id)
            j = json.loads(resp)[0]
            # print(j)
            if j["disabledStatus"] == True:
                print("Temp project successfully deleted: {0}".format(project_id))
            else:
                print("Could not delete project, response is below: \n")
                print(resp)
        print("\n\nTests complete")
        total_tests = len(test_cases_passed) + len(test_cases_errors)
        # To avoid division by zero
        if total_tests == 0:
            total_tests = 1
        print("Total Success Rate {:.2f}%".format(
            len(test_cases_passed) * 100.0 / total_tests))

        print("Test Case Errors: {}".format(test_cases_errors))




def run_suite(_settings, api_test_handler, browser='chrome', platform='linux', execution_mode='parallel'):
    suite_name = _settings['suite']
    test_suite_id = api_test_handler.get_suite_id(suite_name)
    if not test_suite_id:
        print('Suite Name not found')
    else:
        data = {"platform": platform, "browser": browser, "browserVersion": "", "executionType": "smoke",
                "executionMode": execution_mode}
        response = api_test_handler.execute_testsuite(test_suite_id, data)
        if response.status_code == 200:
            print('Test Suite is running')
        else:
            print('Test Suite is not running')

def run_project_test_cases(_settings, api_test_handler):
    project_name = _settings['project']
    test_case_details = api_test_handler.get_test_case_details_by_project_name(project_name)
    print('Total Test Case in {} project is "{}"'.format(project_name, len(test_case_details)))
    for test_case in test_case_details:
        test_case_id = test_case['testCaseId']
        api_test_handler.run_test_case_by_test_case_id_and_project_id(test_case_id)
        print('Test Case "{}" is running'.format(test_case['testCaseName']))

def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='Endpoint for Autonomiq server',
                        default='https://dev.internal.autonomiq.ai')
    parser.add_argument('-u', '--user', help='Username',
                        default='testuser')
    parser.add_argument('-p', '--pass', help='Password',
                        default='test1')
    parser.add_argument('-f', '--files', help='Test Case Files to run',
                        default='../**/*.csv')
    parser.add_argument('-pr', '--project', help='Project to run',
                        default='')
    parser.add_argument('-su', '--suite', help='Suites to run, eg: "[project_name]|[suite_name]"',
                        default='')
    parser.add_argument('-r', '--recorder_files', help='Test Recorder',
                        default='../**/*.json')
    parser.add_argument('-c', '--cleanup', help='Cleanup temp Project',
                        default=False, action="store_true")

    settings = vars(parser.parse_args())
    return settings


if __name__ == '__main__':

    _settings = process_args()
    api_test_handler = ApiTestHandler(_settings)
    api_test_handler.get_token()
    # run_test_cases(_settings, api_test_handler)
    run_suite(_settings, api_test_handler)
    run_project_test_cases(_settings, api_test_handler)
    # api_test_handler.get_test_case_details_by_project_name("test3")


