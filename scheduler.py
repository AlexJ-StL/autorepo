import win32com.client
from datetime import datetime, time
import os
import sys
import logging
from typing import List, Optional

class Scheduler:
    def __init__(self, settings):
        self.settings = settings
        self.scheduler = win32com.client.Dispatch('Schedule.Service')
        try:
            self.scheduler.Connect()
        except Exception as e:
            logging.error(f"Failed to connect to Windows Task Scheduler: {e}")
            self.scheduler = None
        
        self.task_name = "AutomaticRepoUpdater"
        self.root_folder = self.scheduler.GetFolder("\\") if self.scheduler else None

    def create_task(self, name: str, program_path: str, 
                   trigger_time: time, trigger_days: List[int]) -> bool:
        """Create a new scheduled task"""
        if not self.scheduler:
            return False

        try:
            # Create task definition
            task_def = self.scheduler.NewTask(0)
            
            # Set general info
            task_def.RegistrationInfo.Description = "Automatic Repository Update Task"
            task_def.Settings.Enabled = True
            task_def.Settings.Hidden = False
            task_def.Settings.WakeToRun = False
            
            # Create trigger
            trigger = task_def.Triggers.Create(2)  # TASK_TRIGGER_WEEKLY
            trigger.DaysOfWeek = sum(1 << day for day in trigger_days)
            trigger.StartBoundary = (
                datetime.now().replace(
                    hour=trigger_time.hour,
                    minute=trigger_time.minute,
                    second=0,
                    microsecond=0
                ).isoformat()
            )
            
            # Create action
            action = task_def.Actions.Create(0)
            action.Path = program_path
            action.Arguments = "--scheduled-run"
            
            # Register the task
            self.root_folder.RegisterTaskDefinition(
                name,
                task_def,
                6,  # TASK_CREATE_OR_UPDATE
                None,  # No user needed for current user context
                None,  # No password
                0  # TASK_LOGON_NONE
            )
            return True
            
        except Exception as e:
            logging.error(f"Failed to create scheduled task: {e}")
            return False

    def update_schedule(self) -> bool:
        """Update the scheduled task based on current settings"""
        if not self.scheduler:
            return False

        schedule_settings = self.settings.get_schedule_settings()
        if not schedule_settings['enabled']:
            return self.delete_task()

        try:
            hour = int(schedule_settings.get('hour', 9))
            minute = int(schedule_settings.get('minute', 0))
            trigger_time = time(hour=hour, minute=minute)
            
            days = schedule_settings.get('days', ['Mon', 'Wed', 'Fri'])
            day_indices = [self._get_day_index(day) for day in days]
            
            return self.create_task(
                self.task_name,
                sys.executable,
                trigger_time,
                day_indices
            )
            
        except Exception as e:
            logging.error(f"Failed to update schedule: {e}")
            return False

    def delete_task(self) -> bool:
        """Delete the scheduled task"""
        if not self.scheduler:
            return False

        try:
            self.root_folder.DeleteTask(self.task_name, 0)
            return True
        except Exception as e:
            logging.error(f"Failed to delete scheduled task: {e}")
            return False

    def get_next_run(self) -> Optional[str]:
        """Get the next scheduled run time"""
        if not self.scheduler:
            return None

        try:
            task = self.root_folder.GetTask(self.task_name)
            next_run = task.NextRunTime
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    def get_last_run(self) -> Optional[str]:
        """Get the last run time"""
        if not self.scheduler:
            return None

        try:
            task = self.root_folder.GetTask(self.task_name)
            last_run = task.LastRunTime
            return last_run.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    @staticmethod
    def _get_day_index(day_name: str) -> int:
        """Convert day name to index (0 = Sunday, 6 = Saturday)"""
        days = {
            'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3,
            'Thu': 4, 'Fri': 5, 'Sat': 6
        }
        return days.get(day_name, 1)  # Default to Monday if invalid
