from automations.models import Automation, EventRecord, Execution
from triggers.tasks import handle_event_task
from automations.tasks import run_automation_task

from django.utils import timezone

# NOTE: Might bundle into a class later idk
def process_events(events):
    from triggers.services import event_matches_trigger, persist_event
    print("PROCESSING EVENTS")
    for raw_event in events:
        persisted_event = persist_event(raw_event)
        # NOTE: Temporarily turning off idempotency check
        if not persisted_event.processed:
            handle_event_task.delay(persisted_event.event_id)

def handle_event(event):
    from triggers.services import event_matches_trigger

    automations = Automation.objects.filter(
        trigger__integration=event.integration,
        trigger__trigger_key=event.trigger
    )

    for automation in automations:
        print("Handling an event")
        if event_matches_trigger(event, automation.trigger):
            # TODO: Create Execution 
            execution = Execution.objects.create(
                automation=automation,
                trigger_event=event.payload,
                status=Execution.Status.RUNNING,
                started_at=timezone.now()
            )
            print("Event matches the trigger truly")
            run_automation_task.delay(event.event_id, execution.id)
        else:
            print("Event does not match the trigger")

        event.processed = True
        event.processed_at = timezone.now()
        event.save(update_fields=['processed', 'processed_at'])

