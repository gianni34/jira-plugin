from  docs_manager import DocsManager
from  jira_manager import JiraManager
from datetime import date, timedelta
from collections import defaultdict

class Issue:
    
    PRIORITIES = {'Lowest': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Highest': 5}

    def __init__(self):
        self.id = 0
        self.key = ''
        self.name = ''
        self.developer = ''
        self.estimateTime = 0
        self.priority = 3
        self.type = ''
        self.link = ''
        

    def __repr__(self):
        return "Name: " + self.name


class Report:

    def parse_issues_and_developers(self, issues_in_proj):
        
        issues = []
        developers = []

        for issue in issues_in_proj:
            try:
                new_issue = Issue()

                new_issue.key = issue.key
                new_issue.id = issue.id
                new_issue.name = issue.fields.summary
                
                if issue.fields.timeoriginalestimate != None:
                    new_issue.estimateTime = int(issue.fields.timeoriginalestimate)/3600
                else: 
                    new_issue.estimateTime = 0
                
                if issue.fields.assignee.displayName != None:
                    new_issue.developer = issue.fields.assignee.displayName
                else:
                    new_issue.developer = 'No assignment'
                
                new_issue.priority = Issue.PRIORITIES[issue.fields.priority.name]
                new_issue.type = issue.fields.issuetype.name
                new_issue.link = issue.permalink()

                issues.append(new_issue)

                if not issue.fields.assignee.displayName in developers:
                    developers.append(issue.fields.assignee.displayName)
            except:
                print "Error: Unexpected error occurred during creation of an Issue"
        
        return issues, developers


    def get_issues_per_developer(self, issues, developers):
        issues_x_developer = defaultdict(list)
        for i in issues:
            issues_x_developer[i.developer].append(i)

        for key, value in issues_x_developer.items():
            issues_x_developer[key] = sorted(issues_x_developer[key], key=lambda x: x.priority, reverse=True)
        
        return issues_x_developer


def main():
    jira = JiraManager()
    jira_connection = jira.start_connection()
    issues_of_proj = jira.get_issues_of_proj(jira_connection)

    sprint_name = jira.get_sprint_name(jira_connection, issues_of_proj[0])
    report = Report()
    tasks, developers = report.parse_issues_and_developers(issues_of_proj)
    tasks_per_developer = report.get_issues_per_developer(tasks, developers)
    
    start_date = date.today() + timedelta(7) #It does not exist a start_date for sprints that dont are running
    #sprint_name = 'Sprint 3'

    doc_manager = DocsManager()
    doc = doc_manager.create_doc(sprint_name)
    doc_manager.share_doc(doc)
    worksheet = doc_manager.insert_labels(doc, sprint_name, start_date)
    doc_manager.insert_data_in_doc(worksheet, tasks_per_developer)

main()