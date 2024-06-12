# Automation to send notification when filtration or boost ended

Please find below the automation code:

> [!WARNING]
>
> Please take attention to replace in automations below the service `notify.mobile_app_iphone_de_marc` by your own notify service

## French version

```yaml
alias: Notification Filtration Piscine Demo - FR
description: Send a notification when filtration or boost finished
trigger:
  - platform: event
    event_type: iopoolpumpmanager_event
    event_data:
      type: end_filtration
    id: end_filtration
    alias: Receive a FILTRATION end event
  - alias: Receiving a BOOST end event
    platform: event
    event_type: iopoolpumpmanager_event
    event_data:
      type: end_boost
    id: end_boost
condition: []
action:
  - choose:
      - conditions:
          - condition: trigger
            id:
              - end_filtration
            alias: Triggered by the end of FILTRATION
        sequence:
          - service: notify.mobile_app_iphone_de_marc
            metadata: {}
            data:
              title: 💦 Filtration terminée pour aujourd'hui
              message: >-
                La filtration a tournée aujourd'hui durant {{  
                (trigger.event.data.event_data.elapsed_min|int * 60) |  
                timestamp_custom('%Hh%M', false) }} sur une durée de {{   
                (trigger.event.data.event_data.required_min|int * 60) |  
                timestamp_custom('%Hh%M', false) }} , soit  {{ (100 /  
                trigger.event.data.event_data.required_min *  
                trigger.event.data.event_data.elapsed_min) | round(0) }}% du
                temps prévu.  {{   '\n' -}} {% if
                trigger.event.data.event_data.boost_in_progress == False  
                %}Aucun{% else %}1{% endif %} Boost en cours.
            alias: Send notification of end of Filtration
      - conditions:
          - alias: Triggered by the end of BOOST
            condition: trigger
            id:
              - end_boost
        sequence:
          - alias: Send notification of end of Boost
            service: notify.mobile_app_iphone_de_marc
            data:
              title: 💦 Fin de Boost {{ trigger.event.data.event_data.boost }}
              message: >-
                Un BOOST de {{ trigger.event.data.event_data.boost }} vient de
                terminer.{{   '\n' -}} Il avait commencé le {{  
                as_timestamp(trigger.event.data.event_data.started_at)|timestamp_custom('%d/%m/%Y
                %H:%M') }}  et terminé à  {{
                as_timestamp(trigger.event.data.event_data.ended_at)|timestamp_custom('%d/%m/%Y
                %H:%M') }}
mode: queued
```

## English version

```yaml
alias: Notification Filtration Piscine Demo - EN
description: Send a notification when filtration or boost finished
trigger:
  - platform: event
    event_type: iopoolpumpmanager_event
    event_data:
      type: end_filtration
    id: end_filtration
    alias: Receive a FILTRATION end event
  - alias: Receiving a BOOST end event
    platform: event
    event_type: iopoolpumpmanager_event
    event_data:
      type: end_boost
    id: end_boost
condition: []
action:
  - choose:
      - conditions:
          - condition: trigger
            id:
              - end_filtration
            alias: Triggered by the end of FILTRATION
        sequence:
          - service: notify.mobile_app_iphone_de_marc
            metadata: {}
            data:
              title: 💦 Filtration complete for today
              message: >-
                The filtration system was in operation today for {{  
                (trigger.event.data.event_data.elapsed_min|int * 60) |  
                timestamp_custom('%Hh%M', false) }} over a period of {{   
                (trigger.event.data.event_data.required_min|int * 60) |  
                timestamp_custom('%Hh%M', false) }} , i.e. {{ (100 /  
                trigger.event.data.event_data.required_min *  
                trigger.event.data.event_data.elapsed_min) | round(0) }}% of the
                scheduled time.  {{   '\n' -}} {% if
                trigger.event.data.event_data.boost_in_progress == False  
                %}No{% else %}1{% endif %} Boost in progress.
            alias: Send notification of end of Filtration
      - conditions:
          - alias: Triggered by the end of BOOST
            condition: trigger
            id:
              - end_boost
        sequence:
          - alias: Send notification of end of Boost
            service: notify.mobile_app_iphone_de_marc
            data:
              title: 💦 End of Boost {{ trigger.event.data.event_data.boost }}
              message: >-
                A {{ trigger.event.data.event_data.boost }} Boost has just
                finished.{{   '\n' -}} He started the {{  
                as_timestamp(trigger.event.data.event_data.started_at)|timestamp_custom('%d/%m/%Y
                %H:%M') }}  and finished at  {{
                as_timestamp(trigger.event.data.event_data.ended_at)|timestamp_custom('%d/%m/%Y
                %H:%M') }}
mode: queued
```