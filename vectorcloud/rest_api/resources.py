#!/usr/bin/env python3

from flask import request
from flask_restful import Resource
from vectorcloud import db
from vectorcloud.models import Status, Command, Application
from vectorcloud.main.utils import undock_robot, dock_robot,\
    robot_connect_cube, robot_dock_cube, get_stats,\
    execute_db_commands
from vectorcloud.application_system.utils import run_script_func


class UndockRobot(Resource):
    def get(self):
        undock_robot()
        return {'Undock': 'Complete'}


class DockRobot(Resource):
    def get(self):
        dock_robot()
        return {'Dock': 'Complete'}


class ConnectCube(Resource):
    def get(self):
        robot_connect_cube()
        return {'Cube': 'Connected'}


class DockCube(Resource):
    def get(self):
        robot_dock_cube()
        return {'Cube': 'Docked'}


class GetStatus(Resource):
    def get(self):
        err_msg = get_stats(force=True)

        if err_msg:
            return err_msg

        status = Status.query.first()
        return {'version': status.version,
                'battery_voltage': status.battery_voltage,
                'battery_level': status.battery_level,
                'status_charging': status.status_charging,
                'cube_battery_level': status.cube_battery_level,
                'cube_id': status.cube_id,
                'cube_battery_volts': status.cube_battery_volts,
                'timestamp': status.timestamp,
                'ip': status.ip,
                'name': status.name
                }


class AddCommand(Resource):
    def get(self):
        commands = Command.query.all()

        command_list = []
        for command in commands:
            command_list.append(command.command)

        return {'Commands': command_list}

    def put(self):
        command = request.form['data']
        db_command = Command(command=command)
        db.session.add(db_command)
        db.session.commit()

        commands = Command.query.all()
        command_list = []
        for command in commands:
            command_list.append(command.command)

        return {'Commands': command_list}


class ExecuteCommands(Resource):
    def get(self):
        err_msg = execute_db_commands()
        if err_msg:
            return err_msg
        return {'Commands': 'Complete'}


class ClearCommands(Resource):
    def get(self):
        db.session.query(Command).delete()
        db.session.commit()
        return {'Commands': 'Cleared'}


class RunApplication(Resource):
    def get(self, app_name):
        app_name = app_name.replace('-', ' ')
        application = Application.query.filter_by(script_name=app_name).first()

        if not application:
            output = 'Application not found.'

        else:
            output = run_script_func(application.hex_id)

        return {'Output': output}
