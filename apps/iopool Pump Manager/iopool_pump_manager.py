import re
from datetime import datetime, timedelta

import hassapi as hass
import src.config_validator as ConfigValidator
import src.constants as Constants
from pydantic import ValidationError

"""
Author : Marc Guyard

Doc : https://github.com/mguyard/appdaemon-iopoolpumpmanager/blob/main/README.md
Bug Report : https://github.com/mguyard/appdaemon-iopoolpumpmanager/issues/new?assignees=&labels=Bug&projects=&template=bug_report.yml
Feature Request : https://github.com/mguyard/appdaemon-iopoolpumpmanager/issues/new?assignees=&labels=Feature+Request&projects=&template=feature_request.yml
"""  # noqa: E501


class iopoolPumpManager(hass.Hass):
    def initialize(self):
        config = None
        try:
            config = ConfigValidator.Config(**self.args["config"])
        except ValidationError as err:
            self.stop_app(self.name)
            self.log(err, level="ERROR")
            raise RuntimeError("Invalid configuration. Please check the app logs for more information.") from err

        if config is not None:
            self.dryrun = config.dryrun
            if self.dryrun:
                self.log("***** Running in Dryrun mode", level="INFO")
            try:
                self._verify_entities(config=config)
            except RuntimeError as err:
                self.stop_app(self.name)
                self.log(err, level="ERROR")
                raise RuntimeError("Invalid configuration. Please check the app logs for more information.") from err

            self.log(f"Configuration : {config.dict()}", level="DEBUG")

            self.log(f"INIT - Pool is in {self.get_state(entity_id=config.filtration_mode)} mode", level="INFO")

            match self.get_state(entity_id=config.filtration_mode).lower():
                case "standard":
                    self.standard_handlers = {}
                    # Create task for each slots
                    self.log(
                        f"{len(config.filtration_summer.slots.dict().items())} Filtration Slots exists", level="INFO"
                    )
                    latest_slot = self._find_latest_slot(config.filtration_summer.slots.dict())
                    for slot, slot_config in config.filtration_summer.slots.dict().items():
                        slot_name = self._get_slot_name(slot_name=slot, slot_config=slot_config)
                        self.log(f"Slot : '{slot_name}' - {slot_config}", level="INFO")
                        latest = False
                        if slot == latest_slot:
                            self.log(f"Slot '{slot_name}' is the latest slot", level="INFO")
                            latest = True

                        handler_start = self.run_daily(
                            callback=self._callback_start_filtration,
                            start=slot_config.get("start").replace(tzinfo=None),
                            config=config,
                            slot=slot,
                            slot_config=slot_config,
                            latest=latest,
                        )
                        self.standard_handlers[f"{slot}_start"] = handler_start

                        # Create end task for each slots to garantee that the filtration will stop in case
                        # of app restart
                        end_time = self._get_slot_endtime(slot_name=slot_name, slot_config=slot_config, config=config)
                        handler_end = self.run_daily(
                            callback=self._callback_stop_filtration,
                            start=end_time,
                            config=config,
                            latest=latest,
                        )
                        self.standard_handlers[f"{slot}_end"] = handler_end
                        self.log(
                            f"{slot_name} with {slot_config.get('duration_percent')}% of filtration / "
                            f"Start : {slot_config.get('start').replace(tzinfo=None)} / "
                            f"Slot End : {end_time}",
                            level="DEBUG",
                        )

                    # Listen change in boost selector (input_select entity)
                    if config.boost.selector is not None:
                        self.listen_state(
                            callback=self._callback_boost_change,
                            entity_id=config.boost.selector,
                            config=config,
                        )
                    # Listen event when boost timer finished
                    if config.boost.timer is not None:
                        self.listen_event(
                            callback=self._callback_boost_timer_finished,
                            entity_id=config.boost.timer,
                            event="timer.finished",
                            config=config,
                        )

                    # Listen change in boost selector (input_select entity)

                    self.log(f"Standard mode - {len(self.standard_handlers)} handlers created", level="INFO")
                    self.log(f"List of handlers : {self.standard_handlers}", level="INFO")

                case "active-winter":
                    self.run_daily(
                        callback=self._callback_start_filtration,
                        start=config.filtration_winter.start.replace(tzinfo=None),
                        config=config,
                    )
                    self.run_daily(
                        callback=self._callback_stop_filtration,
                        start=(
                            datetime.combine(datetime.today(), config.filtration_winter.start.replace(tzinfo=None))
                            + config.filtration_winter.duration
                        ).time(),
                        config=config,
                        latest=True,
                    )
                    # Calcul and set the calculated duration for the day
                    self._get_standard_day_filtration_duration(config=config)
                case "passive-winter":
                    self.log("Pool is in passive mode. No action will be executed.", level="INFO")

            # Listen change in pool mode (input_select entity)
            self.listen_state(callback=self._callback_pool_mode_change, entity_id=config.filtration_mode)

        self.log(f"{self.name} fully Initialized !", level="INFO")

    def _verify_entities(self, config: ConfigValidator.Config) -> None:
        entities_dict = {
            "config.pump_switch": (config.pump_switch if config.pump_switch is not None else None),
            "config.filtration_mode": (config.filtration_mode if config.filtration_mode is not None else None),
            "config.filtration_summer.recommanded_duration": (
                config.filtration_summer.recommanded_duration
                if config.filtration_summer.recommanded_duration is not None
                else None
            ),
            "config.filtration_summer.elapsed_today": (
                config.filtration_summer.elapsed_today if config.filtration_summer.elapsed_today is not None else None
            ),
            "config.boost.selector": (config.boost.selector if config.boost.selector is not None else None),
            "config.boost.timer": (config.boost.timer if config.boost.timer is not None else None),
        }

        self.log(f"List all entities : {entities_dict}", level="DEBUG")
        # Remove None entities
        entities = {k: v for k, v in entities_dict.items() if v is not None}
        self.log(f"List all entities filtered (None Excluded) : {entities}", level="DEBUG")

        # Check if entities exists and are valid
        for configKey, entity in entities.items():
            if not self.entity_exists(entity_id=entity):
                raise RuntimeError(
                    f"Entity {entity} defined in configuration {configKey} does not exist. "
                    "Please check your configuration."
                )
            match configKey:
                case "config.filtration_mode":
                    required_options = ["Standard", "Active-Winter", "Passive-Winter"]
                    options = self.get_state(entity_id=entity, attribute="options")
                    if not all(option in required_options for option in options):
                        raise RuntimeError(
                            f"Options for {entity} are not valid ({options}). Required options : {required_options}"
                        )
                case "config.filtration_summer.recommanded_duration":
                    if self.get_state(entity_id=entity, attribute="unit_of_measurement") != "min":
                        raise RuntimeError(
                            f"Unit of measurement for {entity} is not valid. Required unit of measurement : min"
                        )
                    if self.get_state(entity_id=entity, attribute="device_class") != "duration":
                        raise RuntimeError(f"Device class for {entity} is not valid. Required device class : duration")
                case "config.filtration_summer.elapsed_today":
                    if self.get_state(entity_id=entity, attribute="unit_of_measurement") != "h":
                        raise RuntimeError(
                            f"Unit of measurement for {entity} is not valid. Required unit of measurement : h"
                        )
                    if self.get_state(entity_id=entity, attribute="device_class") != "duration":
                        raise RuntimeError(f"Device class for {entity} is not valid. Required device class : duration")
                    if self.get_state(entity_id=entity, attribute="state_class") != "measurement":
                        raise RuntimeError(f"State class for {entity} is not valid. Required state class : measurement")
                case "config.boost.selector":
                    required_options = ["Aucun", "None"]
                    options = self.get_state(entity_id=entity, attribute="options")
                    if not any(option in required_options for option in options):
                        raise RuntimeError(
                            f"Options for {entity} are not valid. At least one of required options : {required_options}"
                        )
                    # Check other options (duration options)
                    duration_options = [option for option in options if option not in required_options]
                    for option in duration_options:
                        if not re.match(r"^\d+H$", option):
                            raise RuntimeError(
                                f"Option {option} for {entity} is not in the correct format. "
                                "It should be one or more digits followed by 'H'."
                            )
                case "config.boost.timer":
                    if not self.get_state(entity_id=entity, attribute="restore"):
                        self.log(
                            f"Restore attribute for {entity} is set to false. It's recommanded to switch to : True",
                            level="WARNING",
                        )

            # Create entity for filtration duration calculated
            filtration_calculated_attribute = {
                "friendly_name": "Calculated filtration duration",
                "device_class": "duration",
                "unit_of_measurement": "h",
                "icon": "mdi:clock-outline",
                "source": "AD-" + self.name,
                "config-version": Constants.CONFIG_VERSION,
            }
            if self.get_state(entity_id=Constants.CALCULATED_DURATION_ENTITY) is None:
                self.log(f"Create entity {Constants.CALCULATED_DURATION_ENTITY} for storage", level="DEBUG")
                self.set_state(
                    entity_id=Constants.CALCULATED_DURATION_ENTITY,
                    state=0,
                    attributes=filtration_calculated_attribute,
                )
            else:
                # If entity already exists, check if it's managed by the current app
                if (
                    self.get_state(entity_id=Constants.CALCULATED_DURATION_ENTITY, attribute="source")
                    != "AD-" + self.name
                ):
                    raise RuntimeError(
                        f"Entity {Constants.CALCULATED_DURATION_ENTITY} already exists and "
                        f"is not managed by {self.name}. Please check your configuration."
                    )
                # If entity already exists and is managed by the current app
                # check if the configuration version is up to date
                else:
                    if (
                        self.get_state(entity_id=Constants.CALCULATED_DURATION_ENTITY, attribute="config-version")
                        != Constants.CONFIG_VERSION
                    ):
                        self.log(
                            f"Entity {Constants.CALCULATED_DURATION_ENTITY} has an old configuration version. "
                            f"Current version : {Constants.CONFIG_VERSION}. Updating entity...",
                            level="INFO",
                        )
                        # Update entity with new configuration
                        self.set_state(
                            entity_id=Constants.CALCULATED_DURATION_ENTITY,
                            state=self.get_state(entity_id=Constants.CALCULATED_DURATION_ENTITY),
                            attributes=filtration_calculated_attribute,
                        )

        self.log("All entities exists and are valid", level="DEBUG")

    def _get_slot_name(self, slot_name: str, slot_config: ConfigValidator.SlotConfig) -> str:
        """
        Returns the name of the slot.

        Args:
            slot_name (str): The slot name.
            slot_config (dict): The slot configuration.

        Returns:
            str: The name of the slot.

        """
        return slot_config.get("name") if slot_config.get("name") is not None else slot_name

    def _find_latest_slot(self, slots: ConfigValidator.SlotName) -> str | None:
        """
        Finds the latest slot from the given slots dictionary.

        Args:
            slots (ConfigValidator.SlotName): A dictionary containing slot names as keys and
                                              slot configurations as values.

        Returns:
            str | None: The name of the latest slot, or None if no slots are found.

        """
        latest_slot = None
        latest_start_time = None

        self.log(f"Search for the last slot from : {slots}", level="DEBUG")

        for slot_name, slot_config in slots.items():
            start_time = slot_config.get("start").replace(tzinfo=None)

            if latest_start_time is None or start_time > latest_start_time:
                latest_start_time = start_time
                latest_slot = slot_name

        return latest_slot

    def _find_next_slot(self, reference_slot: ConfigValidator.SlotConfig, config: ConfigValidator.Config) -> str | None:
        """
        Finds the next slot after the reference slot based on the given configuration.

        Args:
            reference_slot (ConfigValidator.SlotConfig): The reference slot to compare against.
            config (ConfigValidator.Config): The configuration object.

        Returns:
            str | None: The name of the next slot, or None if no next slot is found.
        """
        reference_start = datetime.combine(datetime.today(), reference_slot.get("start").replace(tzinfo=None))
        next_slot = None
        next_start = None

        for slot, slot_config in config.filtration_summer.slots.dict().items():
            slot_start = datetime.combine(datetime.today(), slot_config.get("start").replace(tzinfo=None))
            if slot_start > reference_start:
                if next_slot is None or slot_start < next_start:
                    next_slot = slot
                    next_start = slot_start

        return next_slot

    def _get_standard_day_filtration_duration(self, config: ConfigValidator.Config) -> int:
        """
        Returns the total filtration duration for the day.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Returns:
            float: The total filtration duration for the day.

        """
        duration = 0
        # Check if filtration mode is standard
        if self.get_state(entity_id=config.filtration_mode).lower() == "standard":
            # Check if the recommanded duration is available
            if self.get_state(entity_id=config.filtration_summer.recommanded_duration) == "unavailable":
                self.log(
                    f"Entity {config.filtration_summer.recommanded_duration} is unavailable. "
                    "Set the minimal duration configured",
                    level="WARNING",
                )
                duration = int(float(config.filtration_summer.min_duration)) if not None else 0
            else:
                recommanded_duration = int(
                    float(self.get_state(entity_id=config.filtration_summer.recommanded_duration))
                )
                # Check if the recommanded duration is less than the minimal duration
                if (
                    config.filtration_summer.min_duration is not None
                    and recommanded_duration < config.filtration_summer.min_duration
                ):
                    self.log(
                        f"Recommanded duration ({recommanded_duration} min) is less than the minimal duration "
                        f"({config.filtration_summer.min_duration} min). Set the minimal duration configured",
                        level="INFO",
                    )
                    duration = int(float(config.filtration_summer.min_duration))
                # Check if the recommanded duration is greater than the maximal duration
                elif (
                    config.filtration_summer.max_duration is not None
                    and recommanded_duration > config.filtration_summer.max_duration
                ):
                    self.log(
                        f"Recommanded duration ({recommanded_duration} min) is greater than the maximal duration "
                        f"({config.filtration_summer.max_duration} min). Set the maximal duration configured",
                        level="INFO",
                    )
                    duration = int(float(config.filtration_summer.max_duration))
                # Set the recommanded duration if it's between the minimal and maximal duration
                else:
                    duration = int(recommanded_duration)
        # Check if filtration mode is active winter
        # TODO : Tester ceci en activant le mode winter et verifier que l'entité calculé est bien MaJ
        elif self.get_state(entity_id=config.filtration_mode).lower() == "active-winter":
            duration = int(float(config.filtration_winter.duration.total_seconds() / 60))

        self.log(f"Calculated duration for the day : {duration} min", level="INFO")
        # Set the calculated duration in the entity
        self.set_state(entity_id=Constants.CALCULATED_DURATION_ENTITY, state=duration)
        return duration

    def _get_slot_duration(
        self, slot_name: str, slot_config: ConfigValidator.SlotConfig, config: ConfigValidator.Config
    ) -> int:
        """
        Calculate the duration for a given slot based on the slot configuration and the overall configuration.

        Args:
            slot_name (str): The name of the slot.
            slot_config (ConfigValidator.SlotConfig): The configuration for the slot.
            config (ConfigValidator.Config): The overall configuration.

        Returns:
            int: The calculated duration for the slot in minutes.
        """

        day_duration = self._get_standard_day_filtration_duration(config=config)
        slot_duration = (day_duration * slot_config.get("duration_percent")) / 100
        self.log(
            f"Duration for slot '{self._get_slot_name(slot_name=slot_name, slot_config=slot_config)}' :"
            f" {int(slot_duration)} min",
            level="DEBUG",
        )
        return int(slot_duration)

    def _get_slot_endtime(
        self, slot_name: str, slot_config: ConfigValidator.SlotConfig, config: ConfigValidator.Config
    ) -> datetime:
        """
        Calculates the end time for a given time slot.

        Args:
            slot_name (str): The name of the time slot.
            slot_config (ConfigValidator.SlotConfig): The configuration for the time slot.
            config (ConfigValidator.Config): The overall configuration.

        Returns:
            datetime: The end time of the time slot.

        """
        start_time = slot_config.get("start").replace(tzinfo=None)
        slot_duration = self._get_slot_duration(slot_name=slot_name, slot_config=slot_config, config=config)
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=slot_duration)).time()
        self.log(
            f"End time for slot '{self._get_slot_name(slot_name=slot_name, slot_config=slot_config)}' : {end_time}",
            level="DEBUG",
        )
        return end_time

    def _between_slots_start_end(self, config: ConfigValidator.Config) -> bool:
        """
        Checking if now is between the start and end time of all slot declared.
        Based on handlers created.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Returns:
            bool: True if there are multiple slots with both start and end timers running, False otherwise.
        """
        count = 0
        for slot_name, _ in config.filtration_summer.slots.dict().items():
            handler_start_time = None
            handler_end_time = None
            # If both start and end handlers are running
            if self.timer_running(self.standard_handlers[f"{slot_name}_start"]) and self.timer_running(
                self.standard_handlers[f"{slot_name}_end"]
            ):
                handler_start_time, _, _ = self.info_timer(self.standard_handlers[f"{slot_name}_start"])
                handler_end_time, _, _ = self.info_timer(self.standard_handlers[f"{slot_name}_end"])
            # If only start handler is running, end was removed as slot was too close to next slot
            # In this case, we need to find the next slot to get the start time as end time of current slot
            elif self.timer_running(self.standard_handlers[f"{slot_name}_start"]) and not self.timer_running(
                self.standard_handlers[f"{slot_name}_end"]
            ):
                next_slot = self._find_next_slot(
                    reference_slot=vars(config.filtration_summer.slots.root[slot_name]), config=config
                )
                if next_slot is not None:
                    handler_start_time, _, _ = self.info_timer(self.standard_handlers[f"{slot_name}_start"])
                    handler_end_time, _, _ = self.info_timer(self.standard_handlers[f"{next_slot}_start"])
            # If handle start and end are None, we skip the slot and set is_between to False
            # Check is now is between start and end time of the slot
            # Start date can be next day, in this case that means that the start is recurring
            # and start is right for the day
            if handler_start_time is not None and handler_end_time is not None:
                is_between = self.now_is_between(
                    handler_start_time.strftime("%H:%M:%S"), handler_end_time.strftime("%H:%M:%S")
                )
                # Show debug information
                self.log(
                    f"Slot '{slot_name}' - Start : {handler_start_time.strftime('%H:%M:%S')} / "
                    f"End : {handler_end_time.strftime('%H:%M:%S')}",
                    level="DEBUG",
                )
            else:
                is_between = False

            self.log(
                f"Now is between : {is_between}",
                level="DEBUG",
            )
            # If now is between start and end time of the slot, we increment the count
            if is_between:
                count += 1
        # If count is greater than 1, it means that now is between start and end time of one or multiple slots
        if count > 0:
            return True
        else:
            return False

    def _start_pump(self, config: ConfigValidator.Config) -> None:
        """
        Starts the pool pump.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Returns:
            None
        """
        if self.get_state(entity_id=config.pump_switch) == "off":
            if not self.dryrun:
                self.turn_on(entity_id=config.pump_switch)
            else:
                self.log("Dryrun mode - No start action will be executed.", level="INFO")
            self.log(f"Pool Pump {config.pump_switch} turned on", level="INFO")
        else:
            self.log(f"Pool Pump {config.pump_switch} already turned on", level="INFO")

    def _stop_pump(self, config: ConfigValidator.Config) -> None:
        """
        Stops the pool pump.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Returns:
            None
        """
        # Checking if a boost is in progress. When boost is in progress, we don't stop the pump
        if self._is_boost_in_progress(config=config):
            self.log("Boost in progress. No action will be executed.", level="INFO")
            return

        if self.get_state(entity_id=config.pump_switch) == "on":
            if not self.dryrun:
                self.turn_off(entity_id=config.pump_switch)
            else:
                self.log("Dryrun mode - No stop action will be executed.", level="INFO")
            self.log(f"Pool Pump {config.pump_switch} turned off", level="INFO")
        else:
            self.log(f"Pool Pump {config.pump_switch} already turned off", level="INFO")

    def _callback_start_filtration(self, **kwargs: dict):
        """
        Callback method to start the filtration process.

        Args:
            kwargs (dict): Keyword arguments containing the following keys:
                - config (object): Configuration object.
                - slot (str): Name of the current slot.
                - slot_config (object): Configuration object for the current slot.
                - latest (bool): Flag indicating if it's the last slot.

        Returns:
            None
        """
        self._start_pump(config=kwargs["config"])

        # If the slot argument isn't provided, we return - Used when the callback is called for active winter mode
        if "slot" not in kwargs:
            return

        # Retrieve the filtration duration for the slot
        this_slot_duration = self._get_slot_duration(
            slot_name=kwargs["slot"], slot_config=kwargs["slot_config"], config=kwargs["config"]
        )

        # if it's not the last slot, we create the end task based on duration
        if not kwargs["latest"]:
            slot_name = self._get_slot_name(slot_name=kwargs["slot"], slot_config=kwargs["slot_config"])
            # Checking if the next slot is too close to the current slot
            next_slot = self._find_next_slot(reference_slot=kwargs["slot_config"], config=kwargs["config"])
            next_slot_config = kwargs["config"].filtration_summer.slots.root[next_slot]
            next_slot_start = datetime.combine(datetime.today(), next_slot_config.start.replace(tzinfo=None))
            this_slot_end = datetime.combine(
                datetime.today(),
                self._get_slot_endtime(
                    slot_name=kwargs["slot"], slot_config=kwargs["slot_config"], config=kwargs["config"]
                ),
            )
            time_delta = next_slot_start - this_slot_end
            self.log(f"This Slot end at : {this_slot_end} / Next Slot start at : {next_slot_start}", level="DEBUG")
            self.log(
                "Time Delta between End of this slot and " f"start of next slot: {time_delta.total_seconds() / 60} min",
                level="DEBUG",
            )
            self.log(f"This Slot Duration : {this_slot_duration} mn", level="DEBUG")
            # If the time between end of current slot and start of next slot is negative or zero (no enough time)
            if int(time_delta.total_seconds() / 60) <= 0:
                self.log(f"Next Slot Config : {vars(next_slot_config)}", level="DEBUG")
                self.log(
                    f"Time between '{slot_name}' "
                    f"and '{self._get_slot_name(slot_name=next_slot,slot_config=vars(next_slot_config))}' is less than "
                    "the filtration duration of "
                    f"'{slot_name}'. "
                    "We will not stop filtration for "
                    f"{slot_name}",
                    level="WARNING",
                )
                if f"{kwargs['slot']}_end" in self.standard_handlers and self.timer_running(
                    self.standard_handlers[f"{kwargs['slot']}_end"]
                ):
                    self.cancel_timer(self.standard_handlers[f"{kwargs['slot']}_end"])
                    self.log(
                        f"End task canceled for '{slot_name}'",
                        level="INFO",
                    )
            # If the time between the end of the current slot and the start of the next slot is > than the filtration
            else:
                # If the end task already exists, we cancel it to create a new one that really match duration
                if f"{kwargs['slot']}_end" in self.standard_handlers and self.timer_running(
                    self.standard_handlers[f"{kwargs['slot']}_end"]
                ):
                    self.cancel_timer(self.standard_handlers[f"{kwargs['slot']}_end"])
                # Create end task based on duration (duration of slot can change during day based on
                # recommanded duration)
                handler = self.run_in(
                    callback=self._callback_stop_filtration,
                    delay=this_slot_duration * 60,
                    config=kwargs["config"],
                    latest=kwargs["latest"],
                )
                self.standard_handlers[f"{kwargs['slot']}_end"] = handler
                self.log(f"List of handlers : {self.standard_handlers}", level="DEBUG")
        else:
            slot_name = self._get_slot_name(slot_name=kwargs["slot"], slot_config=kwargs["slot_config"])
            # When it's the last slot, we calculate the remaining time of filtration
            self.log(
                f"'{slot_name}' is the last slot",
                level="INFO",
            )
            # Calculate remaining time of filtration
            filtration_duration = float(self._get_standard_day_filtration_duration(config=kwargs["config"]))
            elapsed_today = float(self.get_state(entity_id=kwargs["config"].filtration_summer.elapsed_today)) * 60
            filtration_left = filtration_duration - elapsed_today
            self.log(f"Remaining time of filtration : {filtration_left} min", level="INFO")
            # Cancel original end task if exists
            if f"{kwargs['slot']}_end" in self.standard_handlers and self.timer_running(
                self.standard_handlers[f"{kwargs['slot']}_end"]
            ):
                self.cancel_timer(self.standard_handlers[f"{kwargs['slot']}_end"])
            # Create new end task based on remaining time if it's positive
            if filtration_left > 0:
                handler = self.run_in(
                    callback=self._callback_stop_filtration,
                    delay=filtration_left * 60,
                    config=kwargs["config"],
                    latest=kwargs["latest"],
                )
                self.standard_handlers[f"{kwargs['slot']}_end"] = handler
            else:
                self.log("No remaining time of filtration. Stopping filtration...", level="INFO")
                self._callback_stop_filtration(config=kwargs["config"], latest=kwargs["latest"])
            self.log(f"List of handlers : {self.standard_handlers}", level="DEBUG")

    def _callback_stop_filtration(self, **kwargs: dict):
        """
        Callback method to stop the filtration of the pool pump.

        Args:
            kwargs (dict): Additional keyword arguments.
                - config (object): Configuration object.
                - latest (bool): Flag indicating if it's the last slot.

        Returns:
            None
        """
        self._stop_pump(config=kwargs["config"])
        # TODO : Tester si ca fonctionne bien
        if kwargs["latest"]:
            event_name = "iopoolpumpmanager_event"
            event_type = "end_filtration"
            event_data = {
                "elapsed_min": int(
                    float(self.get_state(entity_id=kwargs["config"].filtration_summer.elapsed_today)) * 60
                ),
                "required_min": int(self.get_state(entity_id=Constants.CALCULATED_DURATION_ENTITY)),
                "end_at": datetime.now().astimezone().isoformat(),
                "boost_in_progress": self._is_boost_in_progress(config=kwargs["config"]),
            }
            self._fire_event(event_name=event_name, type=event_type, event_data=event_data)

    def _callback_pool_mode_change(self, entity: str, attribute: str, old: str, new: str, **kwargs: dict):
        """
        Callback function triggered when the pool mode changes.

        Args:
            entity (str): The entity that triggered the callback.
            attribute (str): The attribute that triggered the callback.
            old (str): The old value of the attribute.
            new (str): The new value of the attribute.
            kwargs (dict): Additional keyword arguments.

        Returns:
            None
        """
        self.log(f"Pool mode changed from {old} to {new}. Reloading configuration...", level="INFO")
        self.restart_app(self.name)

    def _callback_boost_change(self, entity: str, attribute: str, old: str, new: str, **kwargs: dict):
        """
        Callback function triggered when the boost selector changes.

        Args:
            entity (str): The entity that triggered the callback.
            attribute (str): The attribute that triggered the callback.
            old (str): The old value of the attribute.
            new (str): The new value of the attribute.
            kwargs (dict): Additional keyword arguments.
                - config (object): Configuration object.

        Returns:
            None
        """
        self.log(f"Boost selector changed from {old} to {new}.", level="INFO")
        if new in ["Aucun", "None"]:
            self.log("Boost selector set to 'None'. No action will be executed.", level="INFO")
            # Cancel boost timer following the boost selector change
            if self.get_state(entity_id=kwargs["config"].boost.timer) == "active":
                if not self.dryrun:
                    self.call_service(service="timer/cancel", entity_id=kwargs["config"].boost.timer)
                else:
                    self.log("Dryrun mode - Timer Cancel action will not be executed.", level="INFO")

            # Check if the boost ended during a normal filtration slot
            if self._between_slots_start_end(config=kwargs["config"]):
                self.log("Boost ended during normal filtration slot. No action will be executed.", level="INFO")
            else:
                self.log("Stop filtration following the boost selector change", level="INFO")
                self._stop_pump(config=kwargs["config"])
        else:
            boost_duration_hour = int("".join(filter(str.isdigit, new)))
            boost_duration_timer = boost_duration_hour * 3600
            self.call_service(
                service="timer/start", entity_id=kwargs["config"].boost.timer, duration=boost_duration_timer
            )
            self._start_pump(config=kwargs["config"])

    def _callback_boost_timer_finished(self, event_name: str, data: dict, **kwargs: dict):
        """
        Callback function triggered when the boost timer finishes.

        Args:
            event_name (str): The event that triggered the callback.
            data (dict): The data associated with the event.
            kwargs (dict): Additional keyword arguments.
                - config (object): Configuration object.

        Returns:
            None
        """
        self.log(f"Boost timer '{kwargs['config'].boost.timer}' finished.", level="INFO")
        # Get actual boost state
        ended_boost = self.get_state(entity_id=kwargs["config"].boost.selector)
        started_at = datetime.now() - timedelta(hours=int("".join(filter(str.isdigit, ended_boost))))
        # Reset boost selector to None/Aucun
        none_option = None
        boost_options = self.get_state(entity_id=kwargs["config"].boost.selector, attribute="options")
        if "Aucun" in boost_options:
            none_option = "Aucun"
        elif "None" in boost_options:
            none_option = "None"
        self.select_option(entity_id=kwargs["config"].boost.selector, option=none_option)
        # Fire event
        self._fire_event(
            event_name="iopoolpumpmanager_event",
            type="end_boost",
            event_data={
                "boost": ended_boost,
                "started_at": started_at.astimezone().isoformat(),
                "ended_at": datetime.now().astimezone().isoformat(),
            },
        )

    def _is_boost_in_progress(self, config: ConfigValidator.Config) -> bool:
        """
        Checks if a boost is in progress.

        Args:
            config (ConfigValidator.Config): The configuration object.

        Returns:
            bool: True if the boost is in progress, False otherwise.
        """
        return self.get_state(entity_id=config.boost.timer) == "active"

    def _fire_event(self, event_name: str, type: str, event_data: dict) -> None:
        """
        Fires an event with the specified event name, type, and event data.

        Args:
            event_name (str): The name of the event to be fired.
            type (str): The type of the event.
            event_data (dict): The data associated with the event.

        Returns:
            None
        """
        self.log(f"Firing event '{event_name}' with data: {event_data}", level="INFO")
        self.fire_event(event=event_name, type=type, event_data=event_data)
