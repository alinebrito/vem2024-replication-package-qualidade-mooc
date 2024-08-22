import sys
import pandas as pd
import os


def get_metrics(texts):
    global issues_dict
    global report
    ignoreCourseInLine = 0
    df = pd.read_csv('dataset-alura.csv', sep='\t')
    df = df.reset_index()
    courses = df.iterrows()
    base_path = '/home/Documents/Cursos/reports/'
    bug_counter = dict()
    code_smell_counter = dict()
    vulnerability_counter = dict()
    for index, course in courses:
        report_path = course['path']
        if index < ignoreCourseInLine:
            return
        if not pd.isna(report_path):
            issues_dict = {
                'CODE_SMELL': {'INFO': 0, 'MINOR': 0, 'MAJOR': 0, 'CRITICAL': 0, 'BLOCKER': 0},
                'VULNERABILITY': {'INFO': 0, 'MINOR': 0, 'MAJOR': 0, 'CRITICAL': 0, 'BLOCKER': 0},
                'BUG': {'INFO': 0, 'MINOR': 0, 'MAJOR': 0, 'CRITICAL': 0, 'BLOCKER': 0}
            }
            try:
                report = getReport(base_path, report_path)
            except Exception as e:
                if e.__str__().__contains__('No such file or directory'):
                    df.at[index, 'metrics_done'] = False
                    continue
                print(e)

            # Report
            issues = report.iterrows()

            for index_, issue in issues:
                type_issue = issue['type']
                severity = issue['severity']
                rule = issue['rule']
                issues_dict[type_issue][severity] += 1

                if type_issue == 'BUG':
                    bug_counter[rule] = bug_counter.setdefault(rule, 0) + 1
                elif type_issue == 'CODE_SMELL':
                    code_smell_counter[rule] = code_smell_counter.setdefault(rule, 0) + 1
                elif type_issue == 'VULNERABILITY':
                    vulnerability_counter[rule] = vulnerability_counter.setdefault(rule, 0) + 1

                bug_rules_counter_df = pd.DataFrame.from_dict(data=bug_counter, columns=['counter'], orient='index')
                bug_rules_counter_df = bug_rules_counter_df.reset_index()
                bug_rules_counter_df = bug_rules_counter_df.sort_values(by=['counter'], ascending=False)
                bug_rules_counter_df.to_csv('rules_count/bug_rules_counter.csv', sep='\t')

                code_smell_rules_counter_df = pd.DataFrame.from_dict(data=code_smell_counter, columns=['counter'],
                                                              orient='index')
                code_smell_rules_counter_df = code_smell_rules_counter_df.reset_index()
                code_smell_rules_counter_df = code_smell_rules_counter_df.sort_values(by=['counter'], ascending=False)
                code_smell_rules_counter_df.to_csv('rules_count/code_smells_rules_counter.csv', sep='\t')

                vulnerability_rules_counter_df = pd.DataFrame.from_dict(data=vulnerability_counter, columns=['counter'], orient='index')
                vulnerability_rules_counter_df = vulnerability_rules_counter_df.reset_index()
                vulnerability_rules_counter_df = vulnerability_rules_counter_df.sort_values(by=['counter'], ascending=False)
                vulnerability_rules_counter_df.to_csv('rules_count/vulnerability_rules_counter.csv', sep='\t')

        save_unit_issues_in_courses(df, index, issues_dict)
        save_total_issues_in_courses(df, index, issues_dict)
        save_if_doesnt_have_issues_of_type(df, index, issues_dict)
        df.at[index, 'metrics_done'] = True

    df.to_csv('dataset_alura_issues.csv', sep='\t')


def save_unit_issues_in_courses(df, index, issues_dict):
    df.at[index, 'code_smells_info'] = issues_dict['CODE_SMELL']['INFO']
    df.at[index, 'code_smells_minor'] = issues_dict['CODE_SMELL']['MINOR']
    df.at[index, 'code_smells_major'] = issues_dict['CODE_SMELL']['MAJOR']
    df.at[index, 'code_smells_critical'] = issues_dict['CODE_SMELL']['CRITICAL']
    df.at[index, 'code_smells_blocker'] = issues_dict['CODE_SMELL']['BLOCKER']
    df.at[index, 'bugs_info'] = issues_dict['BUG']['INFO']
    df.at[index, 'bugs_minor'] = issues_dict['BUG']['MINOR']
    df.at[index, 'bugs_major'] = issues_dict['BUG']['MAJOR']
    df.at[index, 'bugs_critical'] = issues_dict['BUG']['CRITICAL']
    df.at[index, 'bugs_blocker'] = issues_dict['BUG']['BLOCKER']
    df.at[index, 'vulnerabilities_info'] = issues_dict['VULNERABILITY']['INFO']
    df.at[index, 'vulnerabilities_minor'] = issues_dict['VULNERABILITY']['MINOR']
    df.at[index, 'vulnerabilities_major'] = issues_dict['VULNERABILITY']['MAJOR']
    df.at[index, 'vulnerabilities_critical'] = issues_dict['VULNERABILITY']['CRITICAL']
    df.at[index, 'vulnerabilities_blocker'] = issues_dict['VULNERABILITY']['BLOCKER']


def save_total_issues_in_courses(df, index, issues_dict):
    df.at[index, 'total_code_smells'] = sum(issues_dict['CODE_SMELL'].values())
    df.at[index, 'total_bugs'] = sum(issues_dict['BUG'].values())
    df.at[index, 'total_vulnerabilities'] = sum(issues_dict['VULNERABILITY'].values())


def save_if_doesnt_have_issues_of_type(df, index, issues_dict):
    df.at[index, 'no_code_smells'] = True if sum(issues_dict['CODE_SMELL'].values()) == 0 else False
    df.at[index, 'no_bugs'] = True if sum(issues_dict['BUG'].values()) == 0 else False
    df.at[index, 'no_vulnerabilities'] = True if sum(issues_dict['VULNERABILITY'].values()) == 0 else False


def returnPathCSVReportFromCourse(course_report_path):
    res = []
    for file in os.listdir(course_report_path):
        if file.endswith('.csv'):
            res.append(file)
    return course_report_path + "/" + res[0]


def getReport(base_path, report_path):
    course_report_path = "{}{}".format(base_path, report_path)
    report = returnPathCSVReportFromCourse(course_report_path)
    return pd.read_csv(report, sep='\t')


if __name__ == '__main__':
    get_metrics("")
