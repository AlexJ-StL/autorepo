import os
from datetime import datetime, timedelta
import win32com.client
import pywintypes


class Scheduler:
    def __init__(self, settings):
        self.settings = settings
        self.scheduler = win32com.client.Dispatch('Schedule.Service')
        self.scheduler.Connect()
        self.root_folder = self.scheduler.GetFolder('\\')

    def _handle_com_error(self, e, action):
        print(f"Error {action} task: {e}")

    def create_task(self, task_name, script_path, trigger_time, trigger_days):
        task_def = self.scheduler.NewTask(0)
        trigger = task_def.Triggers.Create(1)
        trigger.StartBoundary = datetime.combine(
            datetime.today() + timedelta(days=1), trigger_time
        ).isoformat()
        trigger.DaysOfWeek = sum(2**day_index for day_index in trigger_days)
        trigger.Enabled = True
        action = task_def.Actions.Create(1)
        action.Path = os.path.abspath(script_path)
        task_def.RegistrationInfo.Description = 'Automatic Repo Updater'
        task_def.Settings.Enabled = True
        task_def.Settings.Hidden = False
        task_def.Settings.RunOnlyIfIdle = False
        task_def.Settings.WakeToRun = False
        try:
            self.root_folder.RegisterTaskDefinition(
                task_name, task_def, 6, '', '', 3
            )
        except pywintypes.com_error as e:
            self._handle_com_error(e, "creating")

    def delete_task(self, task_name):
        try:
            self.root_folder.DeleteTask(task_name, 0)
        except pywintypes.com_error as e:
            self._handle_com_error(e, "deleting")

    def update_task(self, task_name, script_path, trigger_time, trigger_days):
        try:
            task = self.root_folder.GetTask(f'\\{task_name}')
            task.Definition.Triggers.Item(1).StartBoundary = datetime.combine(
                datetime.today() + timedelta(days=1), trigger_time
            ).isoformat()
            task.Definition.Triggers.Item(1).DaysOfWeek = sum(
                2**day_index for day_index in trigger_days
            )
            task.Definition.Actions.Item(1).Path = os.path.abspath(script_path)
            task.SetAccountInformation('', '')
            self.root_folder.RegisterTaskDefinition(
                task_name, task.Definition, 6, '', '', 3
            )
        except (pywintypes.com_error, ValueError) as e:
            self._handle_com_error(e, "updating")

    def get_task_status(self, task_name):
        try:
            task = self.root_folder.GetTask(f'\\{task_name}')
            return task.State
        except pywintypes.com_error as e:
            self._handle_com_error(e, "getting status of")
            return None

    def run_task_now(self, task_name):
        try:
            task = self.root_folder.GetTask(f'\\{task_name}')
            task.Run(None)
        except pywintypes.com_error as e:
            self._handle_com_error(e, "running")

    def enable_task(self, task_name, enable):
        try:
            task = self.root_folder.GetTask(f'\\{task_name}')
            task.Enabled = enable
        except pywintypes.com_error as e:
            self._handle_com_error(e, "enabling/disabling")
