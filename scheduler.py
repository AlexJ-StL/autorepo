import win32com.client
from datetime import datetime, time, timedelta
import os
import sys
import logging
from typing import List, Optional, Dict

class Scheduler:
    def __init__(self, settings):
        self.settings = settings
        self.scheduler = None
        self.root_folder = None
        self.task_name = "AutomaticRepoUpdater"
        self._connect_scheduler()

    def _connect_scheduler(self) -> tuple[bool, str]:
        """Establish connection to Windows Task Scheduler with error handling"""
        try:
            self.scheduler = win32com.client.Dispatch('Schedule.Service')
            self.scheduler.Connect()
            self.root_folder = self.scheduler.GetFolder("\\")
            return True, "Connected to Task Scheduler"
        except Exception as e:
            logging.error(f"Failed to connect to Windows Task Scheduler: {e}")
            self.scheduler = None
            self.root_folder = None
            return False, f"Failed to connect to Task Scheduler: {str(e)}"

    def update_schedule(self) -> tuple[bool, str]:
        """Update the scheduled task with retry logic"""

        retries = 3
        for attempt in range(retries):
            try:
                if not self.scheduler:
                    self._connect_scheduler()

                schedule_settings = self.settings.get_schedule_settings()
                if not schedule_settings['enabled']:
                    success = self.delete_task()
                    return success, "Schedule disabled and task removed" if success else "Failed to remove task"

                # Validate schedule settings
                if not schedule_settings.get('days'):
                    return False, "No days selected for scheduling"

                hour = int(schedule_settings.get('hour', 9))
                minute = int(schedule_settings.get('minute', 0))
                trigger_time = time(hour=hour, minute=minute)

                days = schedule_settings.get('days', ['Mon', 'Wed', 'Fri'])
                day_indices = [self._get_day_index(day) for day in days]

                # Get notification offset
                notification_time = schedule_settings.get('notification', '5 minutes')
                notification_minutes = self._parse_notification_time(notification_time)

                success = self._create_task_with_notification(
                    self.task_name,
                    sys.executable,
                    trigger_time,
                    day_indices,
                    notification_minutes
                )

                message = "Schedule updated successfully" if success else "Failed to update schedule"
                return True, message
            except Exception as e:
                logging.error(f"Schedule update attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    logging.info("Retrying schedule update...")
                    time.sleep(2)
                else:
                    error_msg = f"Failed to update schedule after {retries} attempts: {str(e)}"
                    logging.error(error_msg)
                    return False, error_msg
            return False, "No days selected for scheduling"

        try:
            hour = int(schedule_settings.get('hour', 9))
            minute = int(schedule_settings.get('minute', 0))
            trigger_time = time(hour=hour, minute=minute)
            
            days = schedule_settings.get('days', ['Mon', 'Wed', 'Fri'])
            day_indices = [self._get_day_index(day) for day in days]
            
            # Get notification offset
            notification_time = schedule_settings.get('notification', '5 minutes')
            notification_minutes = self._parse_notification_time(notification_time)
            
            success = self._create_task_with_notification(
                self.task_name,
                sys.executable,
                trigger_time,
                day_indices,
                notification_minutes
            )
            
            message = "Schedule updated successfully" if success else "Failed to update schedule"
            return success, message
            
        except Exception as e:
            error_msg = f"Failed to update schedule: {str(e)}"
            logging.error(error_msg)
            return False, error_msg

    def _create_task_with_notification(self, name: str, program_path: str, 
                                     trigger_time: time, trigger_days: List[int],
                                     notification_minutes: int) -> bool:
        """Create a scheduled task with notification support"""
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
            
            # Create triggers
            if notification_minutes > 0:
                # Notification trigger
                notif_trigger = task_def.Triggers.Create(2)  # TASK_TRIGGER_WEEKLY
                notif_trigger.DaysOfWeek = sum(1 << day for day in trigger_days)
                
                # Adjust notification time
                notif_time = datetime.now().replace(
                    hour=trigger_time.hour,
                    minute=trigger_time.minute,
                    second=0,
                    microsecond=0
                ) - timedelta(minutes=notification_minutes)
                
                notif_trigger.StartBoundary = notif_time.isoformat()
                notif_trigger.Id = "NotificationTrigger"
                
                # Set notification action
                notif_action = task_def.Actions.Create(0)
                notif_action.Path = program_path
                notif_action.Arguments = "--notification"
            
            # Main task trigger
            main_trigger = task_def.Triggers.Create(2)  # TASK_TRIGGER_WEEKLY
            main_trigger.DaysOfWeek = sum(1 << day for day in trigger_days)
            main_trigger.StartBoundary = (
                datetime.now().replace(
                    hour=trigger_time.hour,
                    minute=trigger_time.minute,
                    second=0,
                    microsecond=0
                ).isoformat()
            )
            main_trigger.Id = "MainTrigger"
            
            # Main action
            main_action = task_def.Actions.Create(0)
            main_action.Path = program_path
            main_action.Arguments = "--scheduled-run"
            
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

    def get_schedule_status(self) -> Dict:
        """Get comprehensive schedule status including all relevant details"""
        status = {
            "enabled": self.settings.get("schedule_enabled", False),
            "next_run": self.get_next_run(),
            "last_run": self.get_last_run(),
            "days": self.settings.get("schedule_days", []),
            "time": f"{self.settings.get('schedule_hour', 9):02d}:{self.settings.get('schedule_minute', 0):02d}",
            "notification": self.settings.get("schedule_notification", "5 minutes"),
            "is_connected": self.scheduler is not None
        }
        
        if status["enabled"] and status["next_run"]:
            try:
                next_run = datetime.strptime(status["next_run"], "%Y-%m-%d %H:%M:%S")
                status["time_until_next"] = str(next_run - datetime.now()).split(".")[0]
            except Exception:
                status["time_until_next"] = "Unknown"
                
        return status

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

    @staticmethod
    def _parse_notification_time(notification_time: str) -> int:
        """Convert notification time string to minutes"""
        try:
            value, unit = notification_time.split()
            value = int(value)
            if unit.lower().startswith('minute'):
                return value
            elif unit.lower().startswith('hour'):
                return value * 60
            return 5  # Default to 5 minutes if parsing fails
        except Exception:
            return 5

    @staticmethod
    def _get_day_index(day_name: str) -> int:
        """Convert day name to index (0 = Sunday, 6 = Saturday)"""
        days = {
            'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3,
            'Thu': 4, 'Fri': 5, 'Sat': 6
        }
        return days.get(day_name, 1)  # Default to Monday if invalid
