# Retrieving information from Home Assistant

> [!NOTE]
>
> We're going to use several types of entities that we'll retrieve via RESTful Sensor.
> For simplicity's sake, we're going to declare them in a Home Assistant package.

_Home Assistant can only retrieve information provided by the iopool cloud. This means that if the data is not correct or up to date on the iopool mobile app, the data will not be good in Home Assistant._

## Retrieve your iopool API key

To do this, go to your iopool application and :

- Select the More menu (bottom right)
- Go to Settings
- Retrieve your API key

## Declaration of Home Assistant packages

Open your Home Assistant `configuration.yaml` with the editor you usually use (like Studio Code Server addon).

Add a configuration package in the `homeassistant:` section, as shown below:

```yaml
homeassistant:
  # Load packages
  packages: !include_dir_merge_named includes/packages
```

If you already have a reference of this type in your configuration and understand it, you can skip to the next chapter (_but keep the associated directory in mind_).

In this example, __packages will be different files__ in the `includes/packages` directory.

Regarding the use of !include_dir_merge_named, I invite you to [learn more here](https://www.home-assistant.io/docs/configuration/splitting_configuration#advanced-usage).

## Declare your API key in secrets.yaml

Open your `secrets.yaml` with your usual editor.

Add the reference to your previously retrieved iopool key:

```yaml
# iopool
iopool_api_key: icimacléapiiopool
```

> [!NOTE]
>
> Adding your API key to secrets.yaml is not mandatory, but is recommended if you want to share YAML code with confidence.
> The rest of this tutorial assumes that you are using secrets.yaml. If you're not, you'll need to adapt your configuration in the next chapter.

## Retrieving your pool ID

You need to know your pool ID in order to query the iopool API.

Unfortunately, this ID is not visible on the mobile application interface, but it can be easily retrieved.

To do so, simply run one of the following commands, depending on your operating system:

### For Unix/Linux (can also works on some Windows)

```bash
curl --header 'x-api-key: icimacléapiiopool' https://api.iopool.com/v1/pools/
```

### For Windows

```powershell
$headers=@{}
$headers.Add("x-api-key", "icimacléapiiopool")
$response = Invoke-WebRequest -Uri 'https://api.iopool.com/v1/pools/' -Method GET -Headers $headers
```

> [!WARNING]
>
> Be sure to change icimacléapiiopool to your real API key, retrieved in the previous steps.

The answer will be something like this:

```json
[
  {
    "id": "1aaa22b3-ccc4-4567-d888-e999ff000000",
    "title": "Your Pool Name",
    "latestMeasure": {
      "temperature": 23.129907809491385,
      "ph": 7.422857142857143,
      "orp": 660,
      "mode": "standard",
      "isValid": true,
      "ecoId": "/Keb7cMf",
      "measuredAt": "2024-05-24T14:04:00.000Z"
    },
    "mode": "STANDARD",
    "hasAnActionRequired": false,
    "advice": {
      "filtrationDuration": 4
    }
  }
]
```

The content of the id field is your basin identifier. If you have several probes, you'll see the above example several times, so you'll need to choose the right identifier.

## Declaration of your iopool package

Create an `iopool.yaml` file in the `includes/packages` folder

> [!WARNING]
>
> We assume that you have declared the folder for your packages as defined in the "Home Assistant package declaration" paragraph.
> If not, please adjust the folder in which to create the file

This file will contain all the entities to be created, regardless of their type.
Let's start by detailing the elements, and you'll find the complete file at the end of this chapter.

```yaml
iopool:
  sensor:
    - platform: rest
      unique_id: fabc1ee2-0bbe-416e-b23d-2474ac25fe4e
      name: iopool
      resource: https://api.iopool.com/v1/pool/<votre_id_de_bassin_ici>
      value_template: "{{ value_json.title }}"
      json_attributes:
        - id
        - latestMeasure
        - hasAnActionRequired
        - advice
        - mode
      headers:
        x-api-key: !secret iopool_api_key
      scan_interval: 300
      icon: mdi:pool
```

The first line `iopool:` is used to declare the package name. This is necessary because we use `include_dir_merge_named` in our package directory declaration.
Next, we declare a sensor that will be fed by the Rest platform that enables Home Assistant to make API requests.

The sensor will be named `sensor.iopool` and its state will be the name of your pool. Data will be refreshed every 5 minutes (300 seconds).

It will also contain several attributes that serve as data storage. I won't go into detail here, as these attributes are of little importance at this stage.

***

Now that we've created the entity able to retrieve information from the iopool API, we need to create entities to store each piece of information separately, so that we can more easily exploit it later.

```yaml
template:
    - sensor:
        - name: "temperature_iopool_piscine"
          unique_id: b336b008-dc88-4e3b-afd9-d662979fb0c1$
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['temperature'] | round(2) }}"
          device_class: temperature
          unit_of_measurement: "°C"
          state_class: measurement
          icon: mdi:pool-thermometer
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "ph_iopool_piscine"
          unique_id: f4804a67-1224-4507-a4fb-21d983958b7c
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['ph'] | round(1) }}"
          unit_of_measurement: "pH"
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "orp_iopool_piscine"
          unique_id: e0ef9122-c53a-41ae-be72-517f3fcbb443
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['orp'] | round(0) }}"
          unit_of_measurement: "mV"
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "recommanded_filtration_iopool_piscine"
          unique_id: f53659ba-922f-4861-9198-73a7dd43ae6a
          state: "{{ state_attr('sensor.iopool', 'advice')['filtrationDuration'] * 60 }}"
          device_class: duration
          unit_of_measurement: "min"
          icon: mdi:sun-clock-outline
          
        - name: "mode_iopool_piscine"
          unique_id: af6db587-be33-44e7-950c-fa52f0453d1f
          state: "{{ state_attr('sensor.iopool', 'mode') }}"
          icon: mdi:auto-mode

    - binary_sensor:
        - name: "required_actions_iopool_piscine"
          unique_id: fb6bb7e0-86ad-4f27-90ee-47c39db0ab12
          state: "{{ state_attr('sensor.iopool', 'hasAnActionRequired') }}"
          device_class: problem
          icon: mdi:checkbox-marked-circle-plus-outline
```

> [!WARNING]
>
> Our `template:` must be at the same indentation level as the `sensor` we declared earlier. If in doubt, please refer to the full version of the file at the end of this chapter.

As you can see, we use a template to collect the information presented in sensor.iopool and distribute it to different sensor and binary_sensor entities:

- sensor.temperature_iopool_piscine
- sensor.ph_iopool_piscine
- sensor.orp_iopool_piscine
- sensor.recommanded_filtration_iopool_piscine
- sensor.mode_iopool_piscine
- binary_sensor.required_actions_iopool_piscine

As each entity has a unique_id, you can modify the entity name via the Home Assistant web interface to make it more comprehensible. I suggest the following names:

- Swimming pool sensor temperature
- pH Swimming pool probe
- Disinfection capacity Piscine sensor
- Recommendation Filtration time Swimming pool sensor
- Swimming pool probe mode
- Actions required Sonde Piscine

## Full configuration file

```yaml
iopool:
  sensor:
    - platform: rest
      unique_id: fabc1ee2-0bbe-416e-b23d-2474ac25fe4e
      name: iopool
      resource: https://api.iopool.com/v1/pool/<votre_id_de_bassin_ici>
      value_template: "{{ value_json.title }}"
      json_attributes:
        - id
        - latestMeasure
        - hasAnActionRequired
        - advice
        - mode
      headers:
        x-api-key: !secret iopool_api_key
      scan_interval: 300
      icon: mdi:pool

      
  template:
    - sensor:
        - name: "temperature_iopool_piscine"
          unique_id: b336b008-dc88-4e3b-afd9-d662979fb0c1$
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['temperature'] | round(2) }}"
          device_class: temperature
          unit_of_measurement: "°C"
          state_class: measurement
          icon: mdi:pool-thermometer
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "ph_iopool_piscine"
          unique_id: f4804a67-1224-4507-a4fb-21d983958b7c
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['ph'] | round(1) }}"
          unit_of_measurement: "pH"
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "orp_iopool_piscine"
          unique_id: e0ef9122-c53a-41ae-be72-517f3fcbb443
          state: "{{ state_attr('sensor.iopool', 'latestMeasure')['orp'] | round(0) }}"
          unit_of_measurement: "mV"
          attributes:
            source: "{{ state_attr('sensor.iopool', 'latestMeasure')['mode'] }}"
            isValid: "{{ state_attr('sensor.iopool', 'latestMeasure')['isValid'] }}"
            measuredAt: "{{ state_attr('sensor.iopool', 'latestMeasure')['measuredAt'] }}"
            
        - name: "recommanded_filtration_iopool_piscine"
          unique_id: f53659ba-922f-4861-9198-73a7dd43ae6a
          state: "{{ state_attr('sensor.iopool', 'advice')['filtrationDuration'] * 60 }}"
          device_class: duration
          unit_of_measurement: "min"
          icon: mdi:sun-clock-outline
          
        - name: "mode_iopool_piscine"
          unique_id: af6db587-be33-44e7-950c-fa52f0453d1f
          state: "{{ state_attr('sensor.iopool', 'mode') }}"
          icon: mdi:auto-mode

    - binary_sensor:
        - name: "required_actions_iopool_piscine"
          unique_id: fb6bb7e0-86ad-4f27-90ee-47c39db0ab12
          state: "{{ state_attr('sensor.iopool', 'hasAnActionRequired') }}"
          device_class: problem
          icon: mdi:checkbox-marked-circle-plus-outline
```

# Dashboard example

Here's an example of a map showing the status of your pool using iopool data:

```yaml
type: horizontal-stack
cards:
  - type: entities
    entities:
      - type: custom:mushroom-title-card
        title: Piscine
        alignment: center
        title_tap_action:
          action: none
        subtitle_tap_action:
          action: none
      - type: custom:vertical-stack-in-card
        horizontal: true
        cards:
          - type: custom:mushroom-entity-card
            entity: sensor.mode_iopool_piscine
          - type: custom:mushroom-entity-card
            entity: binary_sensor.required_actions_iopool_piscine
            name: Actions Requises
            icon_color: red
      - type: custom:vertical-stack-in-card
        cards:
          - type: conditional
            conditions:
              - entity: sensor.mode_iopool_piscine
                state: STANDARD
            card:
              type: custom:vertical-stack-in-card
              cards:
                - type: custom:mini-graph-card
                  entities:
                    - entity: sensor.temperature_iopool_piscine
                      name: Température iopool
                  hours_to_show: 96
                  animate: true
                  line_width: 5
                  group_by: hour
                  state_adaptive_color: true
                  hour24: true
                  decimals: 1
                  show:
                    extrema: true
                    average: true
                    labels: false
                  color_thresholds:
                    - value: 20
                      color: '#44739e'
                    - value: 24
                      color: '#12f33f'
                    - value: 30
                      color: '#f39c12'
                    - value: 32
                      color: '#c0392b'
                - type: custom:pool-monitor-card
                  title: Données de piscine
                  temperature: sensor.temperature_iopool_piscine
                  ph: sensor.ph_iopool_piscine
                  orp: sensor.orp_iopool_piscine
                  show_labels: true
                  language: fr
    state_color: false
    show_header_toggle: false
```

![image of card](image.png)

Several types of cards are used and necessary to compose this card:

- Mushroom
- Vertical Stack in Card
- Mini Graph Card
- Pool Monitor Card