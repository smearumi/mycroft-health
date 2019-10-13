# Copyright 2019 S. M. Estiaque Ahmed
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sqlite3
from datetime import timedelta
from json2html import json2html

# For test.
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from adapt.intent import IntentBuilder
from mycroft.util.time import now_local
from mycroft.skills.core import MycroftSkill
from mycroft.skills.core import intent_handler
from mycroft.util.format import pronounce_number


class HealthSkill(MycroftSkill):
    def __init__(self):
        super(HealthSkill, self).__init__(name="HealthSkill")
        self.log.error(self.root_dir)
        self.home_dir = os.path.expanduser('~')
        self.log.error(self.home_dir)

    @intent_handler(IntentBuilder("PressureIntent").require("Track")
                    .require("Health").require("Pressure"))
    def handle_pressure_intent(self, message):
        top = self.get_response("top.mh")

        if not top:
            self.speak_dialog("error.input.mh")
            return

        try:
            top = float(top)

        except Exception:
            self.speak_dialog("error.input.mh")
            return

        bottom = self.get_response("bottom.mh")

        if not bottom:
            self.speak_dialog("error.input.mh")
            return

        try:
            bottom = float(bottom)

        except Exception:
            self.speak_dialog("error.input.mh")
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        self.log.error(top)
        self.log.error(bottom)
        self.log.error(person)

        pressure_data = [(now_local(), "pressure", str(top), "", person),
                         (now_local(), "pressure", str(bottom), "", person)]

        confirm = self.ask_yesno(
                            "confirm.pressure.mh",
                            {"top": pronounce_number(top),
                             "bottom": pronounce_number(bottom)})

        if confirm == "yes":
            if not self.insert_db(pressure_data):
                self.speak_dialog("error.save.mh")

    @intent_handler(IntentBuilder("SugarIntent").require("Track")
                    .require("Health").require("Sugar").require("Value"))
    def handle_sugar_intent(self, message):
        value = message.data.get("Value")

        if not value:
            self.speak_dialog("error.input.mh")
            return

        try:
            value = float(value)

        except Exception:
            self.speak_dialog("error.input.mh")
            return

        meal_status = self.get_response("meal.mh")

        if not meal_status:
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        self.log.error(value)
        self.log.error(meal_status)
        self.log.error(person)

        sugar_data = [(now_local(), "diabetes", str(value),
                       meal_status, person)]

        confirm = self.ask_yesno(
                            "confirm.sugar.mh",
                            {"meal": meal_status,
                             "value": pronounce_number(value)})

        if confirm == "yes":
            if not self.insert_db(sugar_data):
                self.speak_dialog("error.save.mh")

    @intent_handler(IntentBuilder("TemperatureIntent").require("Track")
                    .require("Health").require("Temperature").require("Value"))
    def handle_temperature_intent(self, message):
        value = message.data.get("Value")

        if not value:
            self.speak_dialog("error.input.mh")
            return

        try:
            value = float(value)

        except Exception:
            self.speak_dialog("error.input.mh")
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        self.log.error(value)
        self.log.error(person)

        temperature_data = [(now_local(), "temperature",
                             str(value), "", person)]

        confirm = self.ask_yesno(
                            "confirm.temperature.mh",
                            {"value": pronounce_number(value)})

        if confirm == "yes":
            if not self.insert_db(temperature_data):
                self.speak_dialog("error.save.mh")

    @intent_handler(IntentBuilder("PainIntent").require("Track")
                    .require("Health").require("Pain").require("Value"))
    def handle_pain_intent(self, message):
        value = message.data.get("Value")

        if not value:
            self.speak_dialog("error.input.mh")
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        self.log.error(value)
        self.log.error(person)

        pain_data = [(now_local(), "pain", value, "", person)]

        confirm = self.ask_yesno(
                            "confirm.pain.mh",
                            {"value": value})

        if confirm == "yes":
            if not self.insert_db(pain_data):
                self.speak_dialog("error.save.mh")

    @intent_handler(IntentBuilder("HeartbeatIntent").require("Track")
                    .require("Health").require("Heartbeat").require("Value"))
    def handle_heartbeat_intent(self, message):
        value = message.data.get("Value")

        if not value:
            self.speak_dialog("error.input.mh")
            return

        try:
            value = int(value)

        except Exception:
            self.speak_dialog("error.input.mh")
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        self.log.error(value)
        self.log.error(person)

        heartbeat_data = [(now_local(), "heartbeat", str(value),
                          "", person)]

        confirm = self.ask_yesno(
                            "confirm.heartbeat.mh",
                            {"value": pronounce_number(value)})

        if confirm == "yes":
            if not self.insert_db(heartbeat_data):
                self.speak_dialog("error.save.mh")

    @intent_handler(IntentBuilder("GenerateIntent").require("Generate")
                    .require("Health").require("Report").require("Month"))
    # @intent_handler(IntentBuilder("GenerateIntent").require("Generate")
    #                 .require("Health").require("Report"))
    def handle_generate_intent(self, message):
        # month = message.data.get("Month")
        # self.log.error(month)

        # For test.
        month = "this"

        if not month:
            self.speak_dialog("error.input.mh")
            return

        category = self.get_response("category.mh")

        if not category or category not in ["pressure", "diabetes", "pain",
                                            "temperature", "heartbeat"]:
            self.speak_dialog("error.input.mh")
            return

        person = self.get_response("person.mh")
        person = "" if not person else person

        current_datetime = now_local()

        # Multi languages support should be implemented here.
        if month == "this" or month == "current":
            to_datetime = current_datetime

        elif month == "last" or month == "previous":
            to_datetime = current_datetime.replace(
                                            day=1,
                                            hour=23,
                                            minute=59,
                                            second=59,
                                            microsecond=0) - timedelta(days=1)

        from_datetime = to_datetime.replace(
                                        day=1,
                                        hour=0,
                                        minute=0,
                                        second=0,
                                        microsecond=0)

        health_data_list = self.get_data(from_datetime, to_datetime,
                                         category, person)

        health_data = []

        for data in health_data_list:
            health_data.append({
                            'Datetime': data[0].strftime("%m/%d/%Y %H:%M:%S"),
                            'Category': data[1],
                            'Value': data[2],
                            'Parameter': data[3],
                            'Person': data[4]})

        table = json2html.convert(json=health_data)

        content = """
        <!DOCTYPE html><html><head><style>table{font-family:arial,sans-serif;
        border-collapse:collapse;width:100%;}td,th{border:1px solid #dddddd;
        text-align:left;padding:8px;}tr:nth-child(even)
        {background-color: #dddddd;}</style></head><body>"""

        content = """
        {0}<h2>Health Data: {1} to {2}</h2>
        {3}</body></html>""".format(
                                content,
                                from_datetime.strftime("%m/%d/%Y %H:%M:%S"),
                                to_datetime.strftime("%m/%d/%Y %H:%M:%S"),
                                table)

        # self.send_email(
        #             "Health Report - {0}".format(category.upper()),
        #             content)

        # For test.
        message = Mail(
                from_email="Mycroft Health <health@mycroft.ai>",
                to_emails="smearumi@gmail.com",
                subject="Mycroft Health Report - {0}".format(category.upper()),
                html_content=content)

        api_key = "SG.yJSmPOSlR8CDxWrEiHtkiw.08p0jt2Isa_F9we0"
        api_key = "{0}-H22n2_prFhVBLuBxVcSOSiV4EM".format(api_key)

        try:
            sg = SendGridAPIClient(api_key)
            _ = sg.send(message)

        except Exception:
            pass

    def db_connect(self):
        self.log.error(self.root_dir)

        try:
            connection = sqlite3.connect(
                                    "{0}/mycroft-health.db".format(
                                                                self.home_dir),
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                    sqlite3.PARSE_COLNAMES)

        except Exception:
            return None

        try:
            cursor = connection.cursor()

            sql = """CREATE TABLE health_data (datetime TIMESTAMP NOT NULL,
                     category TEXT NOT NULL, value TEXT NOT NULL,
                     parameter TEXT, person TEXT)"""

            cursor.execute(sql)
            connection.commit()
            # connection.close()

        except Exception:
            pass

        return connection

    def insert_db(self, data):
        connection = self.db_connect()

        if not connection:
            return

        sql = """INSERT INTO health_data VALUES (?, ?, ?, ?, ?)"""

        with connection:
            try:
                cursor = connection.cursor()
                cursor.executemany(sql, data)
                connection.commit()

            except Exception:
                connection.rollback()
                return False

        return True

    def get_data(self, from_datetime, to_datetime, category, person):
        connection = self.db_connect()

        if not connection:
            return

        sql = "SELECT * FROM health_data WHERE datetime > ? and datetime < ?"
        sql = "{0} and category = ? and person = ?".format(sql)
        data_tuple = (from_datetime, to_datetime, category, person)

        with connection:
            try:
                cursor = connection.cursor()
                cursor.execute(sql, data_tuple)
                return cursor.fetchall()

            except Exception:
                return None

    def stop(self):
        pass


def create_skill():
    return HealthSkill()
