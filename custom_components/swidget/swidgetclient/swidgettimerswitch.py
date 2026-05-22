from .device import (
    DeviceType,
)
from .swidgetswitch import SwidgetSwitch

class SwidgetTimerSwitch(SwidgetSwitch):

    def __init__(self, host, secret_key: str, ssl: bool, polling: bool) -> None:
        super().__init__(host=host, secret_key=secret_key, ssl=ssl, polling=polling)
        self._device_type = DeviceType.TimerSwitch

    @property
    def is_on(self) -> bool:
        """Return whether device is on, checking toggle state and timer duration."""
        toggle_state = self.assemblies['host'].components["0"].functions['toggle']["state"]
        
        # First check if toggle is on
        if toggle_state == "on":
            # If toggle is on, check if timer has expired (duration = 0)
            try:
                timer_info = self.assemblies['host'].components["0"].functions.get('timer', {})
                if isinstance(timer_info, dict):
                    timer_duration = timer_info.get("duration", None)
                    # If timer exists and is 0, device is off despite toggle state
                    if timer_duration is not None and timer_duration == 0:
                        return False
                return True
            except (KeyError, AttributeError):
                # If we can't check timer, trust the toggle state
                return True

        elif toggle_state == "off":
            # if the toggle.state is off, the fan can still be on from the timer
            try:
                timer_info = self.assemblies['host'].components["0"].functions.get('timer', {})
                if isinstance(timer_info, dict):
                    # new firmware returns timer.buttonLevel and timer.buttonTimer entities
                    # TODO: handle new timer.autoTimer and timer.autoLevel entities
                    button_timer = timer_info.get("buttonTimer", None)
                    button_level = timer_info.get("buttonLevel", None)
                    if button_level is not None:
                        # If the button level is 255 we are in "stay on" mode
                        if button_level == 255:
                            return True
                        # If the button level is 1..3 we are in "timer" mode
                        # so we should look at button_timer value as the remaining time
                        elif button_level > 0:
                            if button_timer is not None and button_timer > 0:
                                return True
                            else:
                                return False
                        else:
                            return False
            except (KeyError, AttributeError):
                # If we can't check timer, trust the toggle state
                return False

        
        return False

    async def set_countdown_timer(self, minutes):
        """Set the countdown timer."""
        await self.send_command(
            assembly="host", component="0", function="timer", command={"duration": minutes}
        )
