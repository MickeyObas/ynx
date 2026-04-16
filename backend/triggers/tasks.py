from celery import shared_task
from automations.models import Trigger, EventRecord

from requests.exceptions import ConnectionError, Timeout


@shared_task
def poll_triggers_task():
    print("RUNNING POLLING TASSKKKKKKKKKKKKKKKK!!!!!!")
    trigger_ids = Trigger.objects.filter(
        status="active",
        type="poll"
    ).values_list('id', flat=True)

    for trigger_id in trigger_ids:
        run_trigger_task.delay(trigger_id)


@shared_task
def handle_event_task(event_id):
    from automations.engine import handle_event
    event = EventRecord.objects.get(event_id=event_id)
    handle_event(event)


@shared_task(
    bind=True, 
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3}
)
def run_trigger_task(self, trigger_id):
    from triggers.services import run_trigger_live
    trigger = Trigger.objects.get(id=trigger_id)
    if trigger:
        print("Yes there is a trigger")
    else:
        print("There is  no trigger")
    run_trigger_live(trigger)
