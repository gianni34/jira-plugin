from jira import JIRA
import json
import re

class JiraManager:

    def start_connection(self):
        with open('./cred.json', 'r') as f:
            credentials = json.load(f)

        for c in credentials:
            if c['API'] == 'JIRA':
                user = c['user']
                token = c['token']
                uri = c['uri']
                
        jira = JIRA(basic_auth=(user, token), options={"server": uri})

        return jira


    def get_issues_of_proj(self, jira):
        projects = jira.projects()
        key_project = projects[0].key  # Only one project
        issues_in_proj = jira.search_issues('project=%s' % key_project)

        return issues_in_proj

    def get_sprint_name(self, jira, issue):
        sprint_data = issue.fields.customfield_10020[0].split(',')
        r = re.compile("name=")
        name_field = filter(r.match,sprint_data)
        sprint_name = name_field[0].split('=')[1]
        return sprint_name