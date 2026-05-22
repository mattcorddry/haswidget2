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
        
        return False

    async def set_countdown_timer(self, minutes):
        """Set the countdown timer."""
        await self.send_command(
            assembly="host", component="0", function="timer", command={"duration": minutes}
        )
