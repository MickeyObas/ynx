from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from integrations.registry import get_integration_service
from automations.models import Step, Automation, Trigger
from automations.exceptions import AutomationValidationError


def validate_step_config(step: Step) -> list[str]:
    errors = []

    if not step.config:
        return ["Step has no config provided."]
    
    service_cls = get_integration_service(step.integration.id, step.connection)

    action_schema = service_cls.get_action_schema(step.action_name)
    if not action_schema:
        return [f"Action schema not found for '{step.action_name}'."]
    
    required_fields = [key for key, field in action_schema.items() if field.get("required") is True]

    for field in required_fields:
        value = step.config.get(field)
        if value is None:
            errors.append(f"Config is missing required field '{field}'.")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"Config field '{field}' cannot be blank.")

    return errors


def validate_step(step) -> list[str]:
    """Returns a list of error strings for this step. Empty = valid."""
    errors = []

    if not step.connection:
        errors.append("Step has no connection assigned.")
    elif not step.connection.status == "active":
        errors.append(f"Connection '{step.connection.name}' is inactive or expired.")
    elif step.connection.integration != step.integration:
        errors.append(
            f"Connection '{step.connection.name}' does not match "
            f"integration '{step.integration.name}'."
        )

    if not step.action_name:
        errors.append("No action selected.")
    else:
        valid_actions = get_integration_service(step.integration.id, step.connection).get_action_keys()
        if step.action_name not in valid_actions:
            errors.append(f"Action '{step.action_name}' is not valid for this integration.")
        else:
            errors.extend(validate_step_config(step))

    return errors


def validate_trigger(trigger) -> list[str]:
    errors = []

    if not trigger:
        return ["Automation has no trigger configured."]

    if not trigger.type:
        errors.append("Trigger type is not set.")

    # TODO: Change to "ready and set all checks to ready"
    if not trigger.status in [Trigger.Status.READY, Trigger.Status.ACTIVE]: 
        errors.append("Trigger is not properly configured or has not been tested.")

    return errors


def publish_automation(automation) -> Automation:
    """
    Validates all steps + trigger, then publishes if clean.
    Raises AutomationValidationError with all collected errors if not.
    """
    all_errors = {}

    trigger = Trigger.objects.get(automation=automation)
    trigger_errors = validate_trigger(trigger)
    if trigger_errors:
        all_errors['trigger'] = trigger_errors

    step_errors = {}
    for step in automation.steps.all():
        errors = validate_step(step)
        if errors:
            step_errors[str(step.id)] = errors

    if step_errors:
        all_errors['steps'] = step_errors

    if all_errors:
        raise AutomationValidationError(errors=all_errors)
    
    print("Errors -> ", all_errors)

    now = timezone.now()

    trigger.status = Trigger.Status.ACTIVE
    trigger.save(update_fields=["status"])

    automation.steps.all().update(status=Step.Status.READY)
    automation.status = Automation.Status.ENABLED
    automation.published_at = now
    automation.save(update_fields=['status', 'published_at'])

    return automation