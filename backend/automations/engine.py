from automations.models import Automation


# NOTE: Might bundle into a class later idk
def process_events(events):
    for event in events:
        handle_event(event)

def handle_event(event):
    from triggers.services import event_matches_trigger

    automations = Automation.objects.filter(
        integration=event.integration,
        trigger=event.trigger
    )

    for automation in automations:
        if event_matches_trigger(event, automation.trigger):
            # TODO: enqueue automation run via ID
            pass

