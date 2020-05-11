import gspread
from datetime import date
from datetime import datetime
from datetime import timedelta
import json

COLUMN = 3
ROW = 2

class DocsManager:
    def create_doc(self, sheetname):
        gc = gspread.service_account(filename='./file.json')
        sh = gc.create(sheetname)
        return sh
        
    
    def share_doc(self, doc):
        with open('./mail_list.json', 'r') as f:
            mail_list = json.load(f)
        for mail in mail_list[0]['emails']:
            doc.share(mail, perm_type='user', role='writer')
        

    def insert_labels(self, doc, sprint, sprint_beginning):
        col = COLUMN
        row = ROW
        worksheet = doc.sheet1
        worksheet.format('1', {'textFormat': {'bold': True, "fontSize": 14}})
        worksheet.update_cell(1,1, sprint)
        worksheet.format('2', {'textFormat': {'bold': True, "fontSize": 11}, "horizontalAlignment": "CENTER",})
        for i in range(0,14):
            date_mod = sprint_beginning + timedelta(i)
            worksheet.update_cell(row, col , date_mod.strftime('%d/%m/%Y'))
            col += 1

        return worksheet


    def insert_data_in_doc(self, doc, tasks_per_developer):
        row_developer = ROW + 1
        for devs, tasks in tasks_per_developer.items(): 
            col = COLUMN -1
            doc.format('B%s'% row_developer, {'textFormat': {'bold': True, "fontSize": 11}})
            doc.update_cell(row_developer,col, devs)

            max_tasks_per_day = 0
            current_day = 0
            hours_days = [8] * 10 
            row_task = row_developer
            col += 1
            finish = False

            for task in tasks:
                estimate = task.estimateTime
                if  row_task - row_developer > max_tasks_per_day:
                    max_tasks_per_day = row_task - row_developer
                while estimate > 0:    
                    if hours_days[9] == 0: # Last day of the sprint has 0 hours remaining
                        finish = True
                        break            
                    day_value = doc.cell(ROW, col).value
                    weekday = datetime.strptime(day_value, '%d/%m/%Y').weekday()
                    if weekday == 4: #Saturday
                        doc.update_cell(row_task, col, "FRIDAY")
                        col +=1
                        doc.update_cell(row_task, col, "SATURDAY")
                        col +=1
                    doc.update_cell(row_task, col,"=HIPERLINK(\"%s\", \"%s\")" % (task.link, task.key))
                    if estimate >= hours_days[current_day]:
                        estimate -= hours_days[current_day]
                        hours_days[current_day] = 0
                        col += 1
                        current_day += 1
                        row_task = row_developer
                    else:
                        hours_days[current_day] -= estimate
                        estimate = 0
                        row_task +=  1  
                if finish:
                    break      
            row_developer += max_tasks_per_day +2
