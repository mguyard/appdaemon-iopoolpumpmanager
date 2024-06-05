iopool Pump Manager need Home Assistant entities in addition to your pump switch.

This guide will explain you how to create it :

# iopoolPumpManager package

Create a new package [as we already done for iopool entitites](iopool_entities.md) named `iopoolPumpManager.yaml` with this content :

```yaml
iopoolpumpmanager:
  sensor:
    - platform: history_stats
      name: pool_elapsed_filtration_duration
      unique_id: 4d0b5749-d6f8-4d79-a9b1-5f542ad0b4b0
      entity_id: switch.pool_switch
      state: "on"
      type: time
      start: "{{ now().replace(hour=0, minute=0, second=0) }}"
      end: "{{ now() }}"

  input_select:
    pool_boost_selector:
      name: Pool Boost Selector
      icon: mdi:plus-box-multiple
      options:
        - None
        - 1H
        - 4H
        - 8H
        - 24H
    pool_mode:
      name: Pool Mode
      icon: mdi:sun-snowflake-variant
      options:
        - Standard
        - Active-Winter
        - Passive-Winter

  timer:
    pool_boost:
      name: Pool Boost Timer
      restore: true
      icon: mdi:timer-plus
```

> [!WARNING]
> 
> Please modify your `entity_id` in history_stat __to match your pump switch__

This configuration create :
- An history_stats entity who automatically calculate  how many time our pool switch was `On` today.
- A input_select for boost selection. You need to have at least `None` and one boost (boost format is <NumberOfHour>H)
- A input_select with mode of the pool (manually managed) to define type of filtration you want
- A timer triggered when a boost is launch for the time of boost