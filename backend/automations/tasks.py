from celery import shared_task

from automations.models import Automation, EventRecord, Step, Execution, Task

from django.utils import timezone

@shared_task
def test_task():
    print("Yep this is working.")

@shared_task(
        bind=True, 
        autoretry_for=(Exception,), 
        retry_kwargs={"max_retries": 3},
        retry_backoff=True,
        retry_backoff_max=60,
        retry_jitter=True
    )
def run_automation_task(self, automation_id, event_id):
    automation = Automation.objects.get(id=automation_id)
    event = EventRecord.objects.get(event_id=event_id)

    execution = Execution.objects.create(
        automation=automation,
        trigger_event=event.payload,
        status=Execution.Status.RUNNING,
        started_at=timezone.now()
    )

    has_failure = False
    print("NOW RUNNING AUTOMATION!!!")


    try:
        steps = Step.objects.filter(
            automation=automation
        ).order_by('order')


        context = {
            "event": event.payload,
            "step_results": {},
        }

        for step in steps:
            task, created = Task.objects.get_or_create(
                execution=execution,
                step=step,
                defaults={
                    "input_payload":step.config,
                    "status": Task.Status.RUNNING,
                    "started_at": timezone.now()
                }
            )

            if task.status == Task.Status.SUCCESS:
                context["step_results"][str(step.id)] = task.output_payload
                continue

            try:
                result = execute_step(step, context)
                context["step_results"][str(step.id)] = result
                task.status = Task.Status.SUCCESS
                task.output_payload = result
                task.finished_at = timezone.now()
                task.save()

            except Exception as step_error:
                has_failure = True
                task.error = str(step_error)
                task.status = Task.Status.FAILED
                task.finished_at = timezone.now()
                task.save()
                raise step_error
        
        execution.status = (
            Execution.Status.FAILED
            if has_failure
            else Execution.Status.SUCCESS
        )

    except Exception as execution_error:
        execution.status = Execution.Status.FAILED
        execution.error = str(execution_error)

    finally:
        execution.finished_at = timezone.now()
        execution.save()



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

