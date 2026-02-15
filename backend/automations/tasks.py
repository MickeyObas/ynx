from celery import shared_task

from automations.models import Automation, EventRecord, Step


@shared_task
def test_task():
    print("Yep this is working.")

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def run_automation_task(self, automation_id, event_id):
    automation = Automation.objects.get(id=automation_id)
    event = EventRecord.objects.get(event_id=event_id)

    steps = Step.objects.filter(
        automation=automation
    ).order_by('order')

    print("NOW RUNNING AUTOMATION!!!")

    context = {
        "event": event.payload,
        "step_results": {},
    }

    for step in steps:
        result = execute_step(step, context)
        context["step_results"][str(step.id)] = result


def execute_step(step, context):
    if step.kind == Step.Kind.ACTION:
        return execute_action(step, context)

    if step.kind == Step.Kind.CONDITION:
        return execute_condition(step, context)

    raise ValueError(f"Unknown step kind: {step.kind}")


def execute_action(step, context):
    from integrations.registry import get_integration_service

    action_name = step.action_name
    config = step.config 
    service_cls = get_integration_service(
        step.integration.id,
        connection=step.connection
    )
    if not service_cls:
        raise ValueError(f"Service could not be instantiated.")

    result = service_cls.perform_action(
        action_id=action_name,
        connection=step.connection,
        config=config,
        context=context
    )

    return result

def execute_condition(step, context):
    condition = step.config.get("expression")

    # Example: {"expression": "event.amount > 1000"}
    # result = evaluate_expression(condition, context)

    # print(f"Condition evaluated to {result}")
    # return result

